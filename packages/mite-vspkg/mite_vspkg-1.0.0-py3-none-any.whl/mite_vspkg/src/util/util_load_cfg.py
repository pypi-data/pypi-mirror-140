import importlib.util
import os
import re
import shutil
import sys


# https://stackoverflow.com/a/67692
def load_cfg_module(root_dir, work_dir, config_name=""):
    cfg_default_path = os.path.join(root_dir, "config.py.default")
    cfg_dir = os.path.join(work_dir, "config")
    if config_name:
        cfg_path = os.path.join(cfg_dir, config_name)
        if not os.path.isfile(cfg_path):
            sys.exit("Config doesn't exist: %s" % cfg_path)
    else:
        config_name = "config.py"
        cfg_path = os.path.join(cfg_dir, config_name)
        if not os.path.isfile(cfg_path):
            os.makedirs(cfg_dir, exist_ok=True)
            shutil.copyfile(cfg_default_path, cfg_path)
    cfg_spec = importlib.util.spec_from_file_location(
        "mite_vspkg_cfg_module", cfg_path)
    cfg_module = importlib.util.module_from_spec(cfg_spec)
    cfg_spec.loader.exec_module(cfg_module)
    return cfg_module


def compile_trait_list_regexes(raw_trait_list):
    trait_list = {}
    for trait, raw_regex_list in raw_trait_list.items():
        trait_list[trait] = []
        for raw_regex in raw_regex_list:
            trait_list[trait].append(re.compile(raw_regex))
    return trait_list


def process_pl_or_pkg_filter(raw_pl_or_pkg_filter):
    for white_regs in raw_pl_or_pkg_filter["trait_whitelist"].values():
        if not white_regs:
            white_regs.append(".*")
    pl_or_pkg_filter = {
        "trait_whitelist": compile_trait_list_regexes(
            raw_pl_or_pkg_filter["trait_whitelist"]),
        "trait_blacklist": compile_trait_list_regexes(
            raw_pl_or_pkg_filter["trait_blacklist"]),
        "size": raw_pl_or_pkg_filter["size"],
    }
    return pl_or_pkg_filter


def process_dep_filter(raw_dep_filter):
    dep_filter = {
        "skip_dependencies": raw_dep_filter["skip_dependencies"],
        "incl_type": raw_dep_filter["incl_type"],
        "prioritize": {
            k: {"regex": re.compile(v["regex"]), "weight": v["weight"]}
            for k, v in raw_dep_filter["prioritize"].items()
        },
        "pkg_filter": process_pl_or_pkg_filter(raw_dep_filter["pkg_filter"]),
    }
    return dep_filter


def process_file_filter(raw_file_filter):
    if not raw_file_filter["file_whitelist"]:
        raw_file_filter["file_whitelist"].append(".*")
    file_filter = {
        "whitelist": [re.compile(r) for r in
                      raw_file_filter["file_whitelist"]],
        "blacklist": [re.compile(r) for r in
                      raw_file_filter["file_blacklist"]],
    }
    return file_filter


def process_cfg(cfg_module):
    cfg_module.pkg_filter = process_pl_or_pkg_filter(cfg_module.raw_pkg_filter)
    cfg_module.dep_filter = process_dep_filter(cfg_module.raw_dep_filter)
    cfg_module.pl_filter = process_pl_or_pkg_filter(cfg_module.raw_pl_filter)
    cfg_module.parse_out["file_filter"] = process_file_filter(
        cfg_module.parse_out["raw_file_filter"])


def load_cfg(root_dir, work_dir, config_name):
    cfg_module = load_cfg_module(root_dir, work_dir, config_name)
    process_cfg(cfg_module)
    return cfg_module
