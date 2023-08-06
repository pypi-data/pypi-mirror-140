import itertools

from mite_vspkg.src.util import util_const

from mite_vspkg.lib import vsdownload


def get_possible_MSI_combos(MSIs_lists):
    return list({frozenset(c) for c in itertools.product(*MSIs_lists)})


def get_light_req_MSIs(mite_payloads_info, payload_name):

    def prioritize_MSI_combo(MSI_combo):
        total_size = 0
        for MSI in MSI_combo:
            total_size += mite_payloads_info[MSI]["size"]
        return total_size

    # required_MSIs = {<MSI payload name>: [<CAB name>]}
    # Same CAB name may appear in different MSIs.
    required_MSIs = {}
    if "CABsEmbedded" in mite_payloads_info[payload_name]:
        CABs_embedded = mite_payloads_info[payload_name]["CABsEmbedded"]
        possible_MSI_combos = get_possible_MSI_combos(CABs_embedded.values())
        possible_MSI_combos.sort(key=prioritize_MSI_combo)
        lightest_MSI_combo = possible_MSI_combos[0]
        for embedded_CAB, MSIs_with_CAB in CABs_embedded.items():
            for MSI_with_CAB in MSIs_with_CAB:
                if MSI_with_CAB in lightest_MSI_combo:
                    if MSI_with_CAB not in required_MSIs:
                        required_MSIs[MSI_with_CAB] = []
                    required_MSIs[MSI_with_CAB].append(embedded_CAB)
    return required_MSIs


def get_payload_URLs(mite_payloads_info, payload_name):
    payload_URLs = [mite_payloads_info[payload_name]["url"]]
    if "CABs" in mite_payloads_info[payload_name]:
        for CAB_info in mite_payloads_info[payload_name]["CABs"].values():
            payload_URLs.append(CAB_info["url"])
    required_MSIs = get_light_req_MSIs(mite_payloads_info, payload_name)
    for required_MSI in required_MSIs.keys():
        payload_URLs.append(mite_payloads_info[required_MSI]["url"])
    return payload_URLs


def get_payload_size(mite_payloads_info, payload_name):
    base_payload_size = mite_payloads_info[payload_name]["size"]
    total_payload_size = base_payload_size
    if "CABs" in mite_payloads_info[payload_name]:
        for CAB_info in mite_payloads_info[payload_name]["CABs"].values():
            total_payload_size += CAB_info["size"]
    required_MSIs = get_light_req_MSIs(mite_payloads_info, payload_name)
    for required_MSI in required_MSIs.keys():
        total_payload_size += mite_payloads_info[required_MSI]["size"]
    return (base_payload_size, total_payload_size)


def format_payload(mite_payloads_info, payload_name):
    base_size, total_size = get_payload_size(mite_payloads_info, payload_name)
    base_size_str = vsdownload.format_size(base_size)
    total_size_str = vsdownload.format_size(total_size)
    return "%s (%s; %s)" % (payload_name, base_size_str, total_size_str)


def files_per_pkg(packages):
    packages_info_str = ""
    for package in packages:
        mite_payloads_info = package["mitePayloadsInfo"]
        package_formatted = vsdownload.format_package(package)
        package_header_str = ""
        package_header_str += "\n"
        package_header_str += "#" * util_const.OUT_DELIM_LEN + "\n"
        package_header_str += package_formatted + "\n"
        payloads_info_str = ""
        for pl_name, pl_info in mite_payloads_info.items():
            pl_formatted = format_payload(mite_payloads_info, pl_name)
            pl_URLs = get_payload_URLs(mite_payloads_info, pl_name)
            payload_header_str = ""
            payload_header_str += "#" * util_const.OUT_DELIM_LEN + "\n"
            payload_header_str += pl_formatted + "\n"
            for pl_URL in pl_URLs:
                payload_header_str += pl_URL + "\n"
            payload_header_str += "-" * util_const.OUT_DELIM_LEN + "\n"
            files_info_str = ""
            for filename in pl_info["files"]:
                files_info_str += filename + "\n"
            if files_info_str:
                payloads_info_str += payload_header_str + files_info_str
        if payloads_info_str:
            packages_info_str += package_header_str + payloads_info_str
    print(packages_info_str)


def get_filepattern(filename, file_filter):
    for regex in file_filter["whitelist"]:
        if regex.match(filename):
            return regex.pattern
    return ""


def pkgs_per_filepattern(packages, file_filter):
    pkgs_per_filepattern = {}
    for package in packages:
        mite_payloads_info = package["mitePayloadsInfo"]
        pkg_formatted = vsdownload.format_package(package)
        added_filepatterns = set()
        for payload_info in mite_payloads_info.values():
            for filename in payload_info["files"]:
                filepattern = get_filepattern(filename, file_filter)
                if filepattern and filepattern not in added_filepatterns:
                    added_filepatterns.add(filepattern)
                    if filepattern not in pkgs_per_filepattern:
                        pkgs_per_filepattern[filepattern] = []
                    pkgs_per_filepattern[filepattern].append(pkg_formatted)
    pkgs_per_filepattern_str = ""
    for filepattern, pkg_strings in pkgs_per_filepattern.items():
        filepattern_header_str = ""
        filepattern_header_str += "\n"
        filepattern_header_str += "#" * util_const.OUT_DELIM_LEN + "\n"
        filepattern_header_str += filepattern + "\n"
        filepattern_header_str += "-" * util_const.OUT_DELIM_LEN + "\n"
        pkgs_str = ""
        for pkg_string in pkg_strings:
            pkgs_str += pkg_string + "\n"
        pkgs_per_filepattern_str += filepattern_header_str + pkgs_str
    print(pkgs_per_filepattern_str)


def URLs_per_filepattern(packages, file_filter):
    # URLs_collections_per_pattern = {
    #     <file pattern>: [{"package": ..., "payload": ..., "URLs": [...]}]
    # }
    URLs_collections_per_pattern = {}
    for package in packages:
        mite_payloads_info = package["mitePayloadsInfo"]
        pkg_formatted = vsdownload.format_package(package)
        for pl_name, payload_info in mite_payloads_info.items():
            pl_formatted = format_payload(mite_payloads_info, pl_name)
            pl_URLs = get_payload_URLs(mite_payloads_info, pl_name)
            added_filepatterns = set()
            for filename in payload_info["files"]:
                filepattern = get_filepattern(filename, file_filter)
                if filepattern and filepattern not in added_filepatterns:
                    added_filepatterns.add(filepattern)
                    if filepattern not in URLs_collections_per_pattern:
                        URLs_collections_per_pattern[filepattern] = []
                    URLs_collections_per_pattern[filepattern].append(
                        {
                            "package": pkg_formatted,
                            "payload": pl_formatted,
                            "URLs": pl_URLs,
                        }
                    )
    URLs_per_file_str = ""
    for filepattern, URLs_collections in URLs_collections_per_pattern.items():
        filepattern_header_str = ""
        filepattern_header_str += "\n"
        filepattern_header_str += "#" * util_const.OUT_DELIM_LEN + "\n"
        filepattern_header_str += filepattern + "\n"
        URLs_info_str = ""
        for URLs_collection in URLs_collections:
            URLs_collection_header_str = ""
            URLs_collection_header_str += "-" * util_const.OUT_DELIM_LEN + "\n"
            URLs_collection_header_str += URLs_collection["package"] + "\n"
            URLs_collection_header_str += URLs_collection["payload"] + "\n"
            URLs_str = ""
            for URL in URLs_collection["URLs"]:
                URLs_str += URL + "\n"
            URLs_info_str += URLs_collection_header_str + URLs_str
        URLs_per_file_str += filepattern_header_str + URLs_info_str
    print(URLs_per_file_str)


def embedded_CABs(packages):
    # CAB_pl_per_pl_per_pkg = {
    #     <pkg_formatted>: {
    #         <pl_formatted>: {
    #             <CAB_pl_formatted>: {"URL": ...}
    #         }
    #     }
    # }
    CAB_pl_per_pl_per_pkg = {}
    for package in packages:
        mite_payloads_info = package["mitePayloadsInfo"]
        pkg_formatted = vsdownload.format_package(package)
        for pl_name in mite_payloads_info.keys():
            pl_formatted = format_payload(mite_payloads_info, pl_name)
            req_MSIs = get_light_req_MSIs(mite_payloads_info, pl_name)
            for req_MSI, embedded_CABs in req_MSIs.items():
                CAB_pl_formatted = format_payload(mite_payloads_info, req_MSI)
                if pkg_formatted not in CAB_pl_per_pl_per_pkg:
                    CAB_pl_per_pl_per_pkg[pkg_formatted] = {}
                if pl_formatted not in CAB_pl_per_pl_per_pkg[pkg_formatted]:
                    CAB_pl_per_pl_per_pkg[pkg_formatted][pl_formatted] = {}
                CAB_payload_URL = mite_payloads_info[req_MSI]["url"]
                CAB_pl_per_pl_per_pkg[pkg_formatted][pl_formatted].update(
                    {
                        CAB_pl_formatted: {
                            "URL": CAB_payload_URL,
                            "embedded_CABs": embedded_CABs,
                        }
                    }
                )
    CAB_pl_per_pl_per_pkg_str = ""
    for pkg_formatted, CAB_pl_per_pl in CAB_pl_per_pl_per_pkg.items():
        package_header_str = ""
        package_header_str += "\n"
        package_header_str += "#" * util_const.OUT_DELIM_LEN + "\n"
        package_header_str += pkg_formatted + "\n"
        CAB_pl_per_pl_str = ""
        for pl_formatted, CAB_payloads in CAB_pl_per_pl.items():
            payload_header_str = ""
            payload_header_str += "#" * util_const.OUT_DELIM_LEN + "\n"
            payload_header_str += pl_formatted + "\n"
            CAB_payloads_info_str = ""
            for CAB_pl_formatted, CAB_payload_info in CAB_payloads.items():
                CAB_payloads_info_str += "-" * util_const.OUT_DELIM_LEN + "\n"
                CAB_payloads_info_str += CAB_pl_formatted + "\n"
                CAB_payloads_info_str += CAB_payload_info["URL"] + "\n"
                for embedded_CAB in CAB_payload_info["embedded_CABs"]:
                    CAB_payloads_info_str += embedded_CAB + "\n"
            CAB_pl_per_pl_str += payload_header_str + CAB_payloads_info_str
        CAB_pl_per_pl_per_pkg_str += package_header_str + CAB_pl_per_pl_str
    print(CAB_pl_per_pl_per_pkg_str)


def errors_per_pkg(packages):
    errors_str = ""
    for package in packages:
        package_formatted = vsdownload.format_package(package)
        package_errors_str = ""
        package_errors_str += "\n"
        package_errors_str += package_formatted + "\n"
        for error_msg in package["miteErrors"]:
            package_errors_str += error_msg + "\n"
        errors_str += package_errors_str
    print(errors_str)
