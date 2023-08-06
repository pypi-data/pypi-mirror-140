from mite_vspkg.src.util import util_const

from mite_vspkg.lib import vsdownload


def check_regexes(string, regexes):
    for regex in regexes:
        if regex.match(string):
            return True
    return False


def check_dict_white(dict_to_check, trait_whitelist):
    for trait, white_regexes in trait_whitelist.items():
        if (trait not in dict_to_check
                or not check_regexes(dict_to_check[trait], white_regexes)):
            return False
    return True


def check_dict_black(dict_to_check, trait_blacklist):
    for trait, black_regexes in trait_blacklist.items():
        if (trait in dict_to_check
                and check_regexes(dict_to_check[trait], black_regexes)):
            return False
    return True


def check_minmax_size(size, min_max):
    min_size = min_max["min"]
    max_size = min_max["max"]
    if (min_size != -1 and size < min_size):
        return False
    if (max_size != -1 and size > max_size):
        return False
    return True


def check_pkg(package, pkg_filter):
    check_size = vsdownload.pkg_download_size(package, util_const.EXT_CHECK)
    unpack_size = vsdownload.pkg_download_size(package, util_const.EXT_UNPACK)
    install_size = vsdownload.pkg_install_size(package)
    return (check_minmax_size(check_size, pkg_filter["size"]["check"])
            and check_minmax_size(unpack_size, pkg_filter["size"]["unpack"])
            and check_minmax_size(install_size, pkg_filter["size"]["install"])
            and check_dict_white(package, pkg_filter["trait_whitelist"])
            and check_dict_black(package, pkg_filter["trait_blacklist"]))


def filter_packages(packages, pkg_filter, dep_filter):
    init_packages = [pkg for pkg in packages if check_pkg(pkg, pkg_filter)]
    if dep_filter["skip_dependencies"]:
        return init_packages
    else:
        potential_dep_pkgs = [pkg for pkg in packages
                              if check_pkg(pkg, dep_filter["pkg_filter"])]
        potential_dep_pkgs_by_ID = vsdownload.get_packages_by_ID(
            potential_dep_pkgs, dep_filter["prioritize"])
        dep_packages = vsdownload.get_dep_packages(potential_dep_pkgs_by_ID,
                                                   init_packages,
                                                   dep_filter["incl_type"])
        # Remove init packages from dep packages to avoid duplicates.
        init_pkgs_IDs = {pkg["id"].lower() for pkg in init_packages}
        dep_packages = [p for p in dep_packages
                        if p["id"].lower() not in init_pkgs_IDs]
        return init_packages + dep_packages


def check_payload(payload, pl_filter):
    payload_size = 0
    if "size" in payload:
        payload_size = payload["size"]
    return (check_minmax_size(payload_size, pl_filter["size"])
            and check_dict_white(payload, pl_filter["trait_whitelist"])
            and check_dict_black(payload, pl_filter["trait_blacklist"]))


def filter_payloads(packages, pl_filter):
    for package in packages:
        if "payloads" in package:
            package["payloads"] = [pl for pl in package["payloads"]
                                   if check_payload(pl, pl_filter)]


def check_file(filename, file_filter):
    return (check_regexes(filename, file_filter["whitelist"])
            and not check_regexes(filename, file_filter["blacklist"]))


def filter_files(packages, file_filter):
    for package in packages:
        for payload_info in package["mitePayloadsInfo"].values():
            payload_info["files"] = [f for f in payload_info["files"]
                                     if check_file(f, file_filter)]
