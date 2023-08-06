import os
import subprocess
import urllib.parse
import zipfile

from mite_vspkg.src.util import util_const
from mite_vspkg.src.util import util_msi

from mite_vspkg.lib import vsdownload


def download_packages(packages, options):
    bytes_downloaded = vsdownload.download_packages(
        packages,
        util_const.EXT_UNPACK,
        options["download_dir"],
        options["download_options"])
    print("Downloaded %s in total."
          % (vsdownload.format_size(bytes_downloaded)))


def extract_required_embedded_CABs(payloads, package_dir):
    package_key = os.path.basename(package_dir)
    CAB_info = util_msi.get_CAB_info(payloads, package_dir)
    for payload in payloads:
        payload_name = vsdownload.get_payload_name(payload)
        CABs_req, CABs_embedded_req = (
            util_msi.get_required_CABs_for_MSI(payload_name, CAB_info))
        for CAB_embedded_name, MSIs_with_CAB in CABs_embedded_req.items():
            req_MSI_name = MSIs_with_CAB[0]
            req_MSI_filepath = os.path.join(package_dir, req_MSI_name)
            print("Extracting CAB in %s: %s from %s"
                  % (package_key, CAB_embedded_name, req_MSI_name))
            CAB_file_contents = subprocess.check_output(
                ["msiinfo", "extract", req_MSI_filepath, CAB_embedded_name])
            out_CAB_filepath = os.path.join(package_dir, CAB_embedded_name)
            with open(out_CAB_filepath, "wb") as CAB_file_obj:
                CAB_file_obj.write(CAB_file_contents)


def unpack_payloads(payloads, package_dir, unpack_dir):
    package_key = os.path.basename(package_dir)
    for payload in payloads:
        payload_name = vsdownload.get_payload_name(payload)
        payload_file = os.path.join(package_dir, payload_name)
        if payload_name.lower().endswith((".vsix", ".zip", ".msi")):
            payload_file_ID = os.path.join(package_key, payload_name)
            print("Unpacking: %s" % payload_file_ID)
        if payload_name.lower().endswith((".vsix", ".zip")):
            # Apparently "ZipFile.extractall()" does more sanitization
            #     than "shutil.unpack_archive()".
            with zipfile.ZipFile(payload_file, 'r') as ZIP_file_obj:
                ZIP_file_obj.extractall(unpack_dir)
        if payload_name.lower().endswith(".msi"):
            subprocess.check_call(
                ["msiextract", "-C", unpack_dir, payload_file],
                stdout=subprocess.DEVNULL)


def unquote_filepaths(main_dir):
    dirs_to_create = set()
    move_dest_src = {}
    dirs_to_remove = []
    for root, dirs, files in os.walk(main_dir, topdown=False):
        for name in files:
            fpath = os.path.join(root, name)
            fpath_rel_main = os.path.relpath(fpath, main_dir)
            if "%" in fpath_rel_main:
                unq_fpath_rel_main = urllib.parse.unquote(fpath_rel_main)
                unq_fpath = os.path.join(main_dir, unq_fpath_rel_main)
                unq_parent_dir = os.path.dirname(unq_fpath)
                dirs_to_create.add(unq_parent_dir)
                move_dest_src[unq_fpath] = fpath
        for name in dirs:
            dpath = os.path.join(root, name)
            dpath_rel_main = os.path.relpath(dpath, main_dir)
            if "%" in dpath_rel_main:
                dirs_to_remove.append(dpath)
    for dir_to_create in dirs_to_create:
        os.makedirs(dir_to_create, exist_ok=True)
    for dest_filepath, src_filepath in move_dest_src.items():
        os.replace(src_filepath, dest_filepath)
    for dir_to_remove in dirs_to_remove:
        os.rmdir(dir_to_remove)


# In the original "vsdownload.py", .vsix filepaths are unquoted
#     by renaming with "shutil.move()".
# It's possible to extract directly
#     with "ZipFile.open()" then "shutil.copyfileobj()"
#     but then there is a need to implement filepath sanitization.
# There is no easy way to unquote filepaths when extracting .msi.
# So unquoting all paths after extraction.
def unpack_packages(packages, download_dir, unpack_dir):
    os.makedirs(unpack_dir, exist_ok=True)
    for package in packages:
        package_key = vsdownload.get_package_key(package)
        package_dir = os.path.join(download_dir, package_key)
        payloads = package["payloads"]
        extract_required_embedded_CABs(payloads, package_dir)
        unpack_payloads(payloads, package_dir, unpack_dir)
    unquote_filepaths(unpack_dir)


def main(packages, options):
    download_packages(packages, options)
    if not options["skip_unpack"]:
        unpack_packages(
            packages, options["download_dir"], options["unpack_dir"])
