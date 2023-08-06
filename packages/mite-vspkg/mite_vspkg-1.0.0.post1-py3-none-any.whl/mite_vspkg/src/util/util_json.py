import contextlib
import json
import os


def load_JSON(filepath):
    with contextlib.suppress(FileNotFoundError):
        with open(filepath, "r") as file_obj:
            return json.load(file_obj)
    return {}


def dump_JSON(data, out_file):
    out_dir = os.path.dirname(out_file)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    tmp_file = out_file + ".tmp"
    with open(tmp_file, "w") as tmp_file_obj:
        json.dump(data, tmp_file_obj, ensure_ascii=False)
    os.replace(tmp_file, out_file)
