from typing import Optional, Union, List, Dict
import zipfile
import json
import os


def read_json(path: str) -> Union[List, Dict]:
    with open(path, 'r', encoding='utf-8') as r:
        return json.load(r)


def write_json(path: str, content: Union[List, Dict]) -> None:
    with open(path, 'w', encoding='utf-8') as w:
        json.dump(content, w)


def chk_dir_and_mkdir(fullpath: str):
    dirs = [fullpath]
    while True:
        directory = os.path.dirname(dirs[0])
        if directory == dirs[0] or not directory:
            break
        if directory:
            dirs.insert(0, directory)
    for dir in dirs[:-1]:
        if not os.path.isdir(dir):
            os.mkdir(dir)


def extract_file(path: str, out_dir: str):
    with zipfile.ZipFile(path, 'r') as zf:
        zf.extractall(out_dir)


def get_all_path(dir_path: str, ext: Optional[str] = None):
    paths = []
    for d in os.listdir(dir_path):
        sub = os.path.join(dir_path, d)
        if os.path.isdir(sub):
            paths += get_all_path(sub)
        else:
            paths.append(sub)
    if ext:
        paths = [p for p in paths if p.endswith(ext)]
    return paths
