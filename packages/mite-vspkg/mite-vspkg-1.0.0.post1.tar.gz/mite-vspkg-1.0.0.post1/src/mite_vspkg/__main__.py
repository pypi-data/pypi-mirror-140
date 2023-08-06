import os
import sys
import urllib.parse

from mite_vspkg.src.util import util_args
from mite_vspkg.src.util import util_enum
from mite_vspkg.src.util import util_filter
from mite_vspkg.src.util import util_json
from mite_vspkg.src.util import util_load_cfg
from mite_vspkg.src.util import util_vsmanifest

from mite_vspkg.src.func import func_check_files
from mite_vspkg.src.func import func_download_unpack
from mite_vspkg.src.func import func_parse_out
from mite_vspkg.src.func import func_print_deps
from mite_vspkg.src.func import func_print_sel

from mite_vspkg.lib import vsdownload


def get_packages_from_installer_manifest(manifest_options):
    manifest = util_vsmanifest.get_installer_manifest(manifest_options)
    # In the original "vsdownload.py", "packages" is a dict {<id>: [<package>]}
    # This "packages" is just a list of all packages.
    packages = manifest["packages"]
    return packages


def main(argv):
    work_dir, config_name = util_args.parse(argv)
    root_dir = os.path.dirname(__file__)
    cfg_module = util_load_cfg.load_cfg(root_dir, work_dir, config_name)

    if (cfg_module.mode == util_enum.mode.PRINT_DEPS_VSDOWNLOAD
            or cfg_module.mode == util_enum.mode.PRINT_REV_DEPS_VSDOWNLOAD):
        packages = get_packages_from_installer_manifest(cfg_module.manifest)
        if cfg_module.mode == util_enum.mode.PRINT_DEPS_VSDOWNLOAD:
            func_print_deps.print_deps(packages,
                                       cfg_module.pkg_filter,
                                       cfg_module.dep_filter)
        if cfg_module.mode == util_enum.mode.PRINT_REV_DEPS_VSDOWNLOAD:
            func_print_deps.print_deps(packages,
                                       cfg_module.pkg_filter,
                                       cfg_module.dep_filter,
                                       reverse=True)

    if (cfg_module.mode == util_enum.mode.PRINT_SEL_PKGS_VSDOWNLOAD
            or cfg_module.mode == util_enum.mode.PRINT_SEL_PKGS_RAW
            or cfg_module.mode == util_enum.mode.PRINT_SEL_PKGS_TRAITS
            or cfg_module.mode == util_enum.mode.DOWNLOAD_AND_UNPACK
            or cfg_module.mode == util_enum.mode.CHECK_FILES):
        packages = get_packages_from_installer_manifest(cfg_module.manifest)
        util_filter.filter_payloads(packages, cfg_module.pl_filter)
        packages = util_filter.filter_packages(packages,
                                               cfg_module.pkg_filter,
                                               cfg_module.dep_filter)
        if cfg_module.mode == util_enum.mode.PRINT_SEL_PKGS_VSDOWNLOAD:
            vsdownload.print_sel_pkgs(packages)
        if cfg_module.mode == util_enum.mode.PRINT_SEL_PKGS_RAW:
            func_print_sel.pkgs_raw(packages)
        if cfg_module.mode == util_enum.mode.PRINT_SEL_PKGS_TRAITS:
            func_print_sel.pkgs_traits(packages, cfg_module.traits_to_print)
        if cfg_module.mode == util_enum.mode.DOWNLOAD_AND_UNPACK:
            func_download_unpack.main(packages, cfg_module.download_unpack)
        if cfg_module.mode == util_enum.mode.CHECK_FILES:
            func_check_files.main(packages, cfg_module.check_files)

    if (cfg_module.mode == util_enum.mode.PARSE_OUT_FILES_PER_PKG
            or cfg_module.mode == util_enum.mode.PARSE_OUT_PKGS_PER_FILEPATTERN
            or cfg_module.mode == util_enum.mode.PARSE_OUT_URLS_PER_FILEPATTERN
            or cfg_module.mode == util_enum.mode.PARSE_OUT_EMBEDDED_CABS):
        packages = util_json.load_JSON(cfg_module.parse_out["out_file"])
        packages = util_filter.filter_packages(packages,
                                               cfg_module.pkg_filter,
                                               cfg_module.dep_filter)
        packages = [p for p in packages if "mitePayloadsInfo" in p]
        if cfg_module.parse_out["unquote_filenames"]:
            for package in packages:
                for payload_info in package["mitePayloadsInfo"].values():
                    payload_info["files"] = [urllib.parse.unquote(f)
                                             for f in payload_info["files"]]
        file_filter = cfg_module.parse_out["file_filter"]
        util_filter.filter_files(packages, file_filter)
        if cfg_module.mode == util_enum.mode.PARSE_OUT_FILES_PER_PKG:
            func_parse_out.files_per_pkg(packages)
        if cfg_module.mode == util_enum.mode.PARSE_OUT_PKGS_PER_FILEPATTERN:
            func_parse_out.pkgs_per_filepattern(packages, file_filter)
        if cfg_module.mode == util_enum.mode.PARSE_OUT_URLS_PER_FILEPATTERN:
            func_parse_out.URLs_per_filepattern(packages, file_filter)
        if cfg_module.mode == util_enum.mode.PARSE_OUT_EMBEDDED_CABS:
            func_parse_out.embedded_CABs(packages)

    if cfg_module.mode == util_enum.mode.PARSE_OUT_ERRORS_PER_PKG:
        packages = util_json.load_JSON(cfg_module.parse_out["out_file"])
        packages = util_filter.filter_packages(packages,
                                               cfg_module.pkg_filter,
                                               cfg_module.dep_filter)
        packages = [p for p in packages if "miteErrors" in p]
        func_parse_out.errors_per_pkg(packages)


if __name__ == "__main__":
    main(sys.argv)
