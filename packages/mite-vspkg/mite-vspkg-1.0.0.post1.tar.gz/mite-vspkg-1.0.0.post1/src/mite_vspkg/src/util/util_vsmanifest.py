import contextlib
import json
import os
import sys
import time
import urllib.parse
import urllib.request

from mite_vspkg.src.util import util_json


def check_URL_local(URL):
    return not urllib.parse.urlparse(URL).scheme


# cache_info = {<type>: {<URL>: {"name": ..., "update_time_ns": ...}}}
def get_manifest_cache_info(manifest_cache_dir):
    cache_info_filepath = os.path.join(manifest_cache_dir, "info.json")
    return util_json.load_JSON(cache_info_filepath)


def save_manifest_cache_info(new_cache_info, manifest_cache_dir):
    cache_info_filepath = os.path.join(manifest_cache_dir, "info.json")
    util_json.dump_JSON(new_cache_info, cache_info_filepath)


def clear_expired_cache(cache_options):
    if not cache_options["skip_cache"]:
        new_cache_info = {}
        cache_info = get_manifest_cache_info(cache_options["dir"])
        cur_time_ns = time.time_ns()
        for manifest_type, type_cache_info in cache_info.items():
            cache_dir = os.path.join(cache_options["dir"], manifest_type)
            for URL, URL_cache_info in type_cache_info.items():
                manifest_name = URL_cache_info["name"]
                manifest_filepath = os.path.join(cache_dir, manifest_name)
                update_time_ns = URL_cache_info["update_time_ns"]
                update_delta_ns = cur_time_ns - update_time_ns
                if update_delta_ns < cache_options["expire_delta_ns"]:
                    if os.path.isfile(manifest_filepath):
                        if manifest_type not in new_cache_info:
                            new_cache_info[manifest_type] = {}
                        new_cache_info[manifest_type][URL] = URL_cache_info
                else:
                    with contextlib.suppress(FileNotFoundError):
                        os.remove(manifest_filepath)
        save_manifest_cache_info(new_cache_info, cache_options["dir"])


def get_cache_filepaths(cache_options):
    # manifest_cache = {<URL>: <filepath>}
    manifest_cache = {}
    if not cache_options["skip_cache"]:
        cache_info = get_manifest_cache_info(cache_options["dir"])
        for manifest_type, manifest_cache_info in cache_info.items():
            cache_dir = os.path.join(cache_options["dir"], manifest_type)
            for URL, URL_cache_info in manifest_cache_info.items():
                cache_path = os.path.join(cache_dir, URL_cache_info["name"])
                manifest_cache[URL] = cache_path
    return manifest_cache


def create_cache(data, URL, base_cache_name, manifest_type, cache_options):
    if not cache_options["skip_cache"]:
        cur_time_ns = time.time_ns()
        cur_time_str = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        cache_name = base_cache_name + "_" + cur_time_str
        cache_info = get_manifest_cache_info(cache_options["dir"])
        if manifest_type not in cache_info:
            cache_info[manifest_type] = {}
        cache_info[manifest_type][URL] = {
            "name": cache_name,
            "update_time_ns": cur_time_ns,
        }
        save_manifest_cache_info(cache_info, cache_options["dir"])
        cache_dir = os.path.join(cache_options["dir"], manifest_type)
        cache_path = os.path.join(cache_dir, cache_name)
        util_json.dump_JSON(data, cache_path)


def get_manifest_from_URL(URL, opts):
    cache_filepaths = get_cache_filepaths(opts["cache"])
    if URL in cache_filepaths:
        URL = cache_filepaths[URL]
    if check_URL_local(URL):
        data = util_json.load_JSON(URL)
    else:
        print("Fetching %s" % URL)
        with urllib.request.urlopen(URL, timeout=opts["timeout"]) as response:
            raw_data = response.read()
        data = json.loads(raw_data)
        manifest_type = data["info"]["manifestType"]
        manifest_version = data["info"]["productDisplayVersion"]
        print("Got %s manifest for %s" % (manifest_type, manifest_version))
        base_cache_name = "%s.%s" % (manifest_type, manifest_version)
        create_cache(data, URL, base_cache_name, manifest_type, opts["cache"])
    return data


def get_installer_manifest(options):
    channel_URL = options["channel_URL"]
    installer_URL = options["installer_URL"]
    clear_expired_cache(options["cache"])
    if not installer_URL:
        channel = get_manifest_from_URL(channel_URL, options)
        for item in channel["channelItems"]:
            if "type" in item and item["type"] == "Manifest":
                installer_URL = item["payloads"][0]["url"]
        if not installer_URL:
            sys.exit("Unable to find an intaller manifest.")
    installer = get_manifest_from_URL(installer_URL, options)
    return installer
