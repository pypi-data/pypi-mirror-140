import os
import subprocess

from mite_vspkg.lib import vsdownload


# https://docs.microsoft.com/en-us/windows/win32/msi/media-table
def get_Media_MSI(MSI_file):
    # parsed_Media_MSI = [
    #     {
    #         "DiskId": ...,
    #         "LastSequence": ...,
    #         "DiskPrompt": ...,
    #         "Cabinet": ...,
    #         "VolumeLabel": ...,
    #         "Source": ...,
    #     }
    # ]
    parsed_Media_MSI = []
    raw_Media_MSI = subprocess.check_output(
        ["msiinfo", "export", MSI_file, "Media"], text=True)
    columns_MSI = [
        "DiskId",
        "LastSequence",
        "DiskPrompt",
        "Cabinet",
        "VolumeLabel",
        "Source",
    ]
    lines_with_headers = raw_Media_MSI.splitlines()
    # First 3 lines are headers.
    lines = lines_with_headers[3:]
    for line in lines:
        line_values = line.split("\t")
        parsed_Media_MSI.append(dict(zip(columns_MSI, line_values)))
    return parsed_Media_MSI


def get_filelist_MSI(MSI_file):
    raw_filelist = subprocess.check_output(
        ["msiextract", "-l", MSI_file], text=True)
    return raw_filelist.splitlines()


def get_CAB_info_MSI(MSI_file):
    CABs_embedded = []
    CABs_required = []
    Media_MSI = get_Media_MSI(MSI_file)
    for media_line in Media_MSI:
        if media_line["Cabinet"]:
            # https://docs.microsoft.com/en-us/windows/win32/msi/cabinet
            # .cab starting with "#" is embedded inside the .msi.
            if media_line["Cabinet"].startswith("#"):
                CABs_embedded.append(media_line["Cabinet"][1:])
            else:
                CABs_required.append(media_line["Cabinet"])
    return (CABs_embedded, CABs_required)


def get_CAB_info(payloads, pkg_dir):
    # Some necessary .cab files are embedded inside other .msi files.
    # https://docs.microsoft.com/en-us/windows/win32/msi/media-table
    # CAB_info = {
    #     "CABs": {<CAB name>: {"url": ..., "size": ...}},
    #     "CABsEmbedded": {<CAB name>: [<MSI payload name>]},
    #     "CABsRequiredPerMSI": {<MSI payload name>: [<CAB name>]},
    # }
    CAB_info = {"CABs": {}, "CABsEmbedded": {}, "CABsRequiredPerMSI": {}}
    for payload in payloads:
        payload_name = vsdownload.get_payload_name(payload)
        payload_file = os.path.join(pkg_dir, payload_name)
        if payload_name.lower().endswith(".cab"):
            CAB_info["CABs"][payload_name] = {
                "url": payload["url"],
                "size": payload["size"],
            }
        if payload_name.lower().endswith(".msi"):
            CABs_embedded, CABs_required = get_CAB_info_MSI(payload_file)
            for CAB in CABs_embedded:
                if CAB not in CAB_info["CABsEmbedded"]:
                    CAB_info["CABsEmbedded"][CAB] = []
                CAB_info["CABsEmbedded"][CAB].append(payload_name)
            CAB_info["CABsRequiredPerMSI"].update(
                {payload_name: CABs_required})
    return CAB_info


def get_required_CABs_for_MSI(payload_name, CAB_info):
    CABs_req = {}
    CABs_embedded_req = {}
    if payload_name.lower().endswith(".msi"):
        for CAB_req in CAB_info["CABsRequiredPerMSI"][payload_name]:
            if CAB_req in CAB_info["CABs"]:
                CABs_req[CAB_req] = CAB_info["CABs"][CAB_req]
            elif CAB_req in CAB_info["CABsEmbedded"]:
                CABs_embedded_req[CAB_req] = CAB_info["CABsEmbedded"][CAB_req]
    return (CABs_req, CABs_embedded_req)
