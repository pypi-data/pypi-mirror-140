import collections

from mite_vspkg.src.util import util_filter

from mite_vspkg.lib import vsdownload


def get_rev_deps_by_pkg_key(pkgs, dep_filter_prioritize):
    rev_deps_by_pkg_key = {}
    pkgs_by_ID = vsdownload.get_packages_by_ID(pkgs, dep_filter_prioritize)
    for pkg in pkgs:
        pkg_chip = pkg.get("chip", None)
        if "dependencies" in pkg:
            for raw_dep_ID, dep_info in pkg["dependencies"].items():
                dep_ID = vsdownload.get_real_dep_ID(raw_dep_ID, dep_info)
                deptype = vsdownload.get_trait_from_dep_info(
                    dep_info, "type", "")
                dep_chip = vsdownload.get_trait_from_dep_info(
                    dep_info, "chip", pkg.get("chip", None))
                dep_pkg = vsdownload.find_package(
                    pkgs_by_ID, dep_ID, dep_chip)
                if dep_pkg:
                    dep_pkg_key = vsdownload.get_package_key(dep_pkg)
                    if dep_pkg_key not in rev_deps_by_pkg_key:
                        rev_deps_by_pkg_key[dep_pkg_key] = {}
                    rev_deps_by_pkg_key[dep_pkg_key][pkg["id"]] = {
                        "type": deptype,
                        "chip": pkg_chip,
                    }
    return rev_deps_by_pkg_key


def str_from_deps_tree(deps_tree, global_indent=""):
    deps_tree_str = ""
    if deps_tree:
        last_item, last_tree = deps_tree.popitem()
        for item, tree in deps_tree.items():
            deps_tree_str += global_indent + "├─" + item + "\n"
            deps_tree_str += str_from_deps_tree(tree, global_indent + "│ ")
        deps_tree_str += global_indent + "└─" + last_item + "\n"
        deps_tree_str += str_from_deps_tree(last_tree, global_indent + "  ")
    return deps_tree_str


def print_deps_tree(deps_tree):
    deps_tree_str = ""
    for root_item, tree in deps_tree.items():
        deps_tree_str += root_item + "\n"
        deps_tree_str += str_from_deps_tree(tree)
    print(deps_tree_str)


def print_deps(packages, pkg_filter, dep_filter, reverse=False):
    init_packages = [
        pkg for pkg in packages
        if util_filter.check_pkg(pkg, pkg_filter)]
    potential_dep_pkgs = [
        pkg for pkg in packages
        if util_filter.check_pkg(pkg, dep_filter["pkg_filter"])]
    potential_dep_pkgs_by_ID = vsdownload.get_packages_by_ID(
        potential_dep_pkgs, dep_filter["prioritize"])
    if reverse:
        rev_deps_by_pkg_key = get_rev_deps_by_pkg_key(
            packages, dep_filter["prioritize"])
    total_deps_tree = collections.OrderedDict()
    for init_package in init_packages:
        if reverse:
            deps_tree = vsdownload.get_rev_deps_tree(potential_dep_pkgs_by_ID,
                                                     rev_deps_by_pkg_key,
                                                     init_package,
                                                     dep_filter["incl_type"])
        else:
            deps_tree = vsdownload.get_deps_tree(potential_dep_pkgs_by_ID,
                                                 init_package,
                                                 dep_filter["incl_type"])
        init_package_str = vsdownload.format_package(init_package)
        total_deps_tree[init_package_str] = deps_tree
    print_deps_tree(total_deps_tree)
