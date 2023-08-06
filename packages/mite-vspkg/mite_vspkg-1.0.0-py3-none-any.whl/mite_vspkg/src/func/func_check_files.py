import os
import shutil
import time
import zipfile

from mite_vspkg.src.util import util_const
from mite_vspkg.src.util import util_enum
from mite_vspkg.src.util import util_json
from mite_vspkg.src.util import util_msi

from mite_vspkg.lib import vsdownload


def print_remain_total_pkgs(pkgs, payload_exts, skip_if_traits=[]):
    remain_pkgs_len = 0
    for pkg in pkgs:
        if not any(trait in pkg for trait in skip_if_traits):
            remain_pkgs_len += 1
    size_formatted = vsdownload.format_size(
        vsdownload.pkgs_download_size(pkgs, payload_exts, skip_if_traits))
    print("Remaining %d packages to check, for a total download size of %s"
          % (remain_pkgs_len, size_formatted))


def scan_ZIP(payload, payload_file):
    payload_info = {"url": payload["url"], "size": payload["size"]}
    with zipfile.ZipFile(payload_file, 'r') as ZIP_file_obj:
        payload_info["files"] = ZIP_file_obj.namelist()
    return payload_info


def scan_MSI(payload, payload_file, CAB_info):
    payload_name = vsdownload.get_payload_name(payload)
    payload_info = {"url": payload["url"], "size": payload["size"]}
    payload_info["files"] = util_msi.get_filelist_MSI(payload_file)
    CABs_req, CABs_embedded_req = (
        util_msi.get_required_CABs_for_MSI(payload_name, CAB_info))
    if CABs_req:
        payload_info["CABs"] = CABs_req
    if CABs_embedded_req:
        payload_info["CABsEmbedded"] = CABs_embedded_req
    return payload_info


def scan_files(payloads, pkg_dir, CAB_info):
    # "mitePayloadsInfo": {
    #     <base payload name>: {
    #         "url": ...,
    #         "size": ...,
    #         "files": [...],
    #         "CABs": {<CAB name>: {"url": ..., "size": ...}},
    #         "CABsEmbedded": {<CAB name>: [<MSIs with the CAB>]},
    #     }
    # }
    # "CABs" and "CABsEmbedded" are optional.
    # "CABs" - required .cab files;
    #          can be downloaded from an URL.
    # "CABsEmbedded" - required .cab files;
    #                  can only be found in another .msi.
    mite_payloads_info = {}
    for payload in payloads:
        payload_name = vsdownload.get_payload_name(payload)
        payload_file = os.path.join(pkg_dir, payload_name)
        if payload_name.lower().endswith((".vsix", ".zip")):
            mite_payloads_info[payload_name] = scan_ZIP(
                payload, payload_file)
        if payload_name.lower().endswith(".msi"):
            mite_payloads_info[payload_name] = scan_MSI(
                payload, payload_file, CAB_info)
    return mite_payloads_info


def get_mite_payloads_info(package, download_dir):
    if "payloads" in package:
        package_key = vsdownload.get_package_key(package)
        pkg_dir = os.path.join(download_dir, package_key)
        CAB_info = util_msi.get_CAB_info(package["payloads"], pkg_dir)
        return scan_files(package["payloads"], pkg_dir, CAB_info)
    else:
        return {}


def retry_JSON(out_file, retry_check):
    pkgs_retry = util_json.load_JSON(out_file)
    if pkgs_retry and (retry_check == util_enum.retry.RETRY
                       or retry_check == util_enum.retry.RETRY_FAILED):
        for package in pkgs_retry:
            if "mitePayloadsInfo" in package:
                continue
            elif ("miteErrors" in package
                  and retry_check != util_enum.retry.RETRY_FAILED):
                continue
            else:
                return pkgs_retry
    return {}


def backup_out(out_file):
    if os.path.isfile(out_file):
        cur_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        backup_file = "%s.oldresult.%s" % (out_file, cur_time)
        shutil.copyfile(out_file, backup_file)
        print("Created a backup of the previous output at %s" % backup_file)


def fill_package_info(packages, skip_if_traits, options):
    print_remain_total_pkgs(packages, util_const.EXT_CHECK, skip_if_traits)
    bytes_downloaded_no_backup = 0
    for package_ind, package in enumerate(packages):
        if not any(t in package for t in skip_if_traits):
            bytes_downloaded = 0
            try:
                bytes_downloaded = vsdownload.download_packages(
                    [package],
                    util_const.EXT_CHECK,
                    options["download_dir"],
                    options["download_options"])
                package["mitePayloadsInfo"] = (
                    get_mite_payloads_info(package, options["download_dir"]))
            except Exception as except_inst:
                except_inst_name = type(except_inst).__name__
                error_str = "%s: %s" % (except_inst_name, except_inst)
                if "miteErrors" not in package:
                    package["miteErrors"] = []
                package["miteErrors"].append(error_str)
                pkg_formatted = vsdownload.format_package(package)
                print("Failed to check package: %s\n%s"
                      % (pkg_formatted, error_str))
            if (not options["keep_download"]
                    and os.path.exists(options["download_dir"])):
                shutil.rmtree(options["download_dir"])
            bytes_downloaded_no_backup += bytes_downloaded
            if bytes_downloaded_no_backup >= options["backup_after_bytes"]:
                util_json.dump_JSON(packages, options["out_file"])
                bytes_downloaded_no_backup = 0
                print("Saved intermediate results to the 'out_file':\n%s"
                      % options["out_file"])
                # This "packages[package_ind+1:]" slice is a workaround
                #     to not count already checked packages.
                print_remain_total_pkgs(packages[package_ind+1:],
                                        util_const.EXT_CHECK,
                                        skip_if_traits)


def main(packages, options):
    pkgs_retry = retry_JSON(options["out_file"], options["retry_check"])
    if pkgs_retry:
        # Ignore the selected packages and retry the last attempt.
        pkgs_with_payloads_info = pkgs_retry
        print("Ignoring the selected packages and retrying the last attempt.")
    else:
        # Getting new data so trying to backup the previous output.
        backup_out(options["out_file"])
        pkgs_with_payloads_info = packages

    fill_package_info(
        pkgs_with_payloads_info, ["mitePayloadsInfo", "miteErrors"], options)

    util_json.dump_JSON(pkgs_with_payloads_info, options["out_file"])

    if options["retry_check"] == util_enum.retry.RETRY_FAILED:
        print("Retrying failed packages.")
        fill_package_info(
            pkgs_with_payloads_info, ["mitePayloadsInfo"], options)
        util_json.dump_JSON(pkgs_with_payloads_info, options["out_file"])

    print("Saved final results to the 'out_file':\n%s"
          % options["out_file"])
