# Modified version of msvc-wine/vsdownload.py
# https://github.com/mstorsjo/msvc-wine
#
# Copyright (c) 2019 Martin Storsjo
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import collections
import hashlib
import multiprocessing.pool
import os
import shutil
import signal
import urllib.parse
import urllib.request

from mite_vspkg.src.util import util_const


def get_packages_by_ID(packages, prioritize_by_traits):

    def prioritize_package(package):
        priority = 0
        for trait, prioritize in prioritize_by_traits.items():
            if (trait in package
                    and prioritize["regex"].match(package[trait])):
                priority -= prioritize["weight"]
        return priority

    packages_by_ID = {}
    for package in packages:
        pkg_ID = package["id"].lower()
        if pkg_ID not in packages_by_ID:
            packages_by_ID[pkg_ID] = []
        packages_by_ID[pkg_ID].append(package)
    for key in packages_by_ID:
        packages_by_ID[key].sort(key=prioritize_package)
    return packages_by_ID


def find_package(packages, pkg_ID, chip):
    pkg_ID = pkg_ID.lower()
    candidates = None
    if pkg_ID not in packages:
        return None
    candidates = packages[pkg_ID]
    if chip:
        chip = chip.lower()
        for a in candidates:
            if "chip" in a and a["chip"].lower() == chip:
                return a
    return candidates[0]


def right_deptype(deptype, dep_incl_type):
    if (deptype == "Optional"
            and not dep_incl_type["optional"]):
        return False
    if (deptype == "Recommended"
            and not dep_incl_type["recommended"]):
        return False
    return True


def get_package_key(pkg):
    package_key = pkg["id"]
    if "version" in pkg:
        package_key += "-" + pkg["version"]
    if "type" in pkg:
        package_key += "-" + pkg["type"]
    if "chip" in pkg:
        package_key += "-" + pkg["chip"]
    if "machineArch" in pkg:
        package_key += "-" + pkg["machineArch"]
    if "productArch" in pkg:
        package_key += "-" + pkg["productArch"]
    if "language" in pkg:
        package_key += "-" + pkg["language"]
    return package_key


def get_real_dep_ID(dep_ID, dep_info):
    if "id" in dep_info:
        return dep_info["id"]
    else:
        return dep_ID


def get_trait_from_dep_info(dep_info, trait, default):
    trait_value = default
    if trait in dep_info:
        trait_value = dep_info[trait]
    return trait_value


def get_deps_tree(pkgs_by_ID, pkg, dep_incl_type):
    dep_tree = collections.OrderedDict()
    if "dependencies" in pkg:
        deps = pkg["dependencies"]
        for raw_dep_ID, dep_info in deps.items():
            dep_ID = get_real_dep_ID(raw_dep_ID, dep_info)
            deptype = get_trait_from_dep_info(dep_info, "type", "")
            if right_deptype(deptype, dep_incl_type):
                dep_chip = get_trait_from_dep_info(
                    dep_info, "chip", pkg.get("chip", None))
                dep_pkg = find_package(pkgs_by_ID, dep_ID, dep_chip)
                if dep_pkg:
                    dep_pkg_str = format_package(dep_pkg)
                    if deptype:
                        dep_pkg_str += " (%s)" % deptype
                    dep_tree[dep_pkg_str] = get_deps_tree(pkgs_by_ID,
                                                          dep_pkg,
                                                          dep_incl_type)
    return dep_tree


def get_rev_deps_tree(pkgs_by_ID, rev_deps_by_pkg_key, pkg, dep_incl_type):
    dep_tree = collections.OrderedDict()
    pkg_key = get_package_key(pkg)
    rev_deps = rev_deps_by_pkg_key.get(pkg_key, {})
    for rev_dep_ID, rev_dep_info in rev_deps.items():
        rev_dep_deptype = get_trait_from_dep_info(rev_dep_info, "type", "")
        rev_dep_chip = get_trait_from_dep_info(
            rev_dep_info, "chip", pkg.get("chip", None))
        rev_dep_pkg = find_package(pkgs_by_ID, rev_dep_ID, rev_dep_chip)
        if right_deptype(rev_dep_deptype, dep_incl_type) and rev_dep_pkg:
            rev_dep_pkg_str = format_package(rev_dep_pkg)
            if rev_dep_deptype:
                rev_dep_pkg_str += " (%s)" % rev_dep_deptype
            dep_tree[rev_dep_pkg_str] = get_rev_deps_tree(pkgs_by_ID,
                                                          rev_deps_by_pkg_key,
                                                          rev_dep_pkg,
                                                          dep_incl_type)
    return dep_tree


def aggregate_depends(pkgs_by_ID, included_pkg_keys, pkg, dep_incl_type):
    dep_packages = []
    if "dependencies" in pkg:
        deps = pkg["dependencies"]
        for raw_dep_ID, dep_info in deps.items():
            dep_ID = get_real_dep_ID(raw_dep_ID, dep_info)
            deptype = get_trait_from_dep_info(dep_info, "type", "")
            if right_deptype(deptype, dep_incl_type):
                dep_chip = get_trait_from_dep_info(
                    dep_info, "chip", pkg.get("chip", None))
                dep_pkg = find_package(pkgs_by_ID, dep_ID, dep_chip)
                if dep_pkg:
                    dep_pkg_key = get_package_key(dep_pkg)
                    if dep_pkg_key not in included_pkg_keys:
                        dep_packages.append(dep_pkg)
                        included_pkg_keys[dep_pkg_key] = True
                        dep_packages.extend(
                            aggregate_depends(pkgs_by_ID,
                                              included_pkg_keys,
                                              dep_pkg,
                                              dep_incl_type))
    return dep_packages


def get_dep_packages(pkgs_by_ID, target_pkgs, dep_incl_type):
    dep_packages = []
    included_pkg_keys = {}
    for target_pkg in target_pkgs:
        dep_packages.extend(aggregate_depends(pkgs_by_ID,
                                              included_pkg_keys,
                                              target_pkg,
                                              dep_incl_type))
    return dep_packages


def pkg_install_size(package):
    total_size = 0
    if "installSizes" in package:
        sizes = package["installSizes"]
        for location in sizes:
            total_size += sizes[location]
    return total_size


def pkgs_install_size(packages):
    total_size = 0
    for pkg in packages:
        total_size += pkg_install_size(pkg)
    return total_size


def pkg_download_size(package, payload_exts, skip_if_traits=[]):
    total_size = 0
    if ("payloads" in package
            and not any(trait in package for trait in skip_if_traits)):
        for payload in package["payloads"]:
            payload_name = get_payload_name(payload)
            if (payload_name.lower().endswith(payload_exts)
                    and "size" in payload):
                total_size = total_size + payload["size"]
    return total_size


def pkgs_download_size(packages, payload_exts, skip_if_traits=[]):
    total_size = 0
    for pkg in packages:
        total_size += pkg_download_size(pkg, payload_exts, skip_if_traits)
    return total_size


def format_size(size):
    if size > 900*1024*1024:
        return "%.1f GB" % (size/(1024*1024*1024))
    if size > 900*1024:
        return "%.1f MB" % (size/(1024*1024))
    if size > 1024:
        return "%.1f KB" % (size/1024)
    return "%d bytes" % (size)


def format_package(pkg):
    pkg_str = pkg["id"]
    if "type" in pkg:
        pkg_str += " (%s)" % pkg["type"]
    if ("chip" in pkg
            or "machineArch" in pkg
            or "productArch" in pkg):
        arch_strs = [
            pkg.get("chip", ""),
            pkg.get("machineArch", ""),
            pkg.get("productArch", ""),
        ]
        pkg_str += " (%s)" % "; ".join(arch_strs)
    if "language" in pkg:
        pkg_str += " (%s)" % pkg["language"]
    check_size = format_size(pkg_download_size(pkg, util_const.EXT_CHECK))
    unpack_size = format_size(pkg_download_size(pkg, util_const.EXT_UNPACK))
    installed_size = format_size(pkg_install_size(pkg))
    pkg_str += " (%s; %s; %s)" % (check_size, unpack_size, installed_size)
    return pkg_str


def print_package_list(packages):
    pkgs_str = ""
    for pkg in sorted(packages, key=lambda pkg: pkg["id"]):
        pkgs_str += "\n"
        pkgs_str += format_package(pkg)
    print(pkgs_str)


def sha256_file(file_to_check):
    sha256_hash = hashlib.sha256()
    with open(file_to_check, "rb") as file_obj:
        for byte_block in iter(lambda: file_obj.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def sha256_check_payload(payload_info, filepath):
    if "sha256" in payload_info:
        calculated_sha256 = sha256_file(filepath).lower()
        payload_info_sha256 = payload_info["sha256"].lower()
        if calculated_sha256 == payload_info_sha256:
            return True
    return False


def get_payload_name(payload):
    name = payload["fileName"]
    if "\\" in name:
        name = name.split("\\")[-1]
    if "/" in name:
        name = name.split("/")[-1]
    return name


def package_has_downloadable_payloads(package, payload_exts):
    if "payloads" in package:
        for payload in package["payloads"]:
            name = get_payload_name(payload)
            payload_size = 0
            if "size" in payload:
                payload_size = payload["size"]
            if name.lower().endswith(payload_exts) and payload_size:
                return True
    return False


# https://noswap.com/blog/python-multiprocessing-keyboardinterrupt
def init_download_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def download_packages(packages, payload_exts, download_dir, download_options):
    download_args = []
    os.makedirs(download_dir, exist_ok=True)
    for package in packages:
        package_key = get_package_key(package)
        if package_has_downloadable_payloads(package, payload_exts):
            package_dir = os.path.join(download_dir, package_key)
            os.makedirs(package_dir, exist_ok=True)
            for payload in package["payloads"]:
                payload_name = get_payload_name(payload)
                if payload_name.lower().endswith(payload_exts):
                    filepath = os.path.join(package_dir, payload_name)
                    pl_file_ID = os.path.join(package_key, payload_name)
                    args = (payload, filepath, pl_file_ID, download_options)
                    download_args.append(args)
    downloaded = 0
    if download_args:
        threads_num = download_options["threads"]
        with multiprocessing.Pool(threads_num, init_download_worker) as pool:
            tasks = [pool.apply_async(_download_payload, args)
                     for args in download_args]
            downloaded = sum(task.get() for task in tasks)
    return downloaded


def _download_payload(payload, filepath, payload_file_ID, download_options):
    attempts = download_options["attempts"]
    for attempt in range(attempts):
        try:
            if os.access(filepath, os.F_OK):
                if sha256_check_payload(payload, filepath):
                    print("Using existing file: %s" % (payload_file_ID),
                          flush=True)
                    return 0
                else:
                    print("Mismatch or missing sha256, removing file: %s"
                          % payload_file_ID,
                          flush=True)
                    os.remove(filepath)
            payload_size = 0
            if "size" in payload:
                payload_size = payload["size"]
            print("Downloading %s (%s)"
                  % (payload_file_ID, format_size(payload_size)),
                  flush=True)
            URL = payload["url"]
            timeout = download_options["timeout"]
            with urllib.request.urlopen(URL, timeout=timeout) as response:
                with open(filepath, "wb") as file_obj:
                    shutil.copyfileobj(response, file_obj)
            if not sha256_check_payload(payload, filepath):
                if download_options["allow_hash_mismatch"]:
                    print("WARNING: "
                          "Mismatch or missing sha256 for downloaded file: %s"
                          % payload_file_ID,
                          flush=True)
                else:
                    raise Exception(
                        "Mismatch or missing sha256 for downloaded file %s"
                        % payload_file_ID)
            return payload_size
        except Exception as e:
            if attempt == attempts - 1:
                raise
            print("%s: %s" % (type(e).__name__, e), flush=True)


def print_sel_pkgs(pkgs):
    print_package_list(pkgs)
    check_download_size = format_size(
        pkgs_download_size(pkgs, util_const.EXT_CHECK))
    unpack_download_size = format_size(
        pkgs_download_size(pkgs, util_const.EXT_UNPACK))
    install_size = format_size(pkgs_install_size(pkgs))
    print("\n"
          "Selected packages: %d\n"
          "Download size to check files: %s\n"
          "Download size to unpack files: %s\n"
          "Install size: %s\n"
          %
          (len(pkgs), check_download_size, unpack_download_size, install_size))
