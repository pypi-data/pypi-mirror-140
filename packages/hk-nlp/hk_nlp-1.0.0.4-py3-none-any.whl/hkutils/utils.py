import os
import zipfile
import json


def read_json(path):
    with open(path, 'r', encoding='utf-8') as r:
        return json.load(r)


def write_json(path, content):
    with open(path, 'w', encoding='utf-8') as w:
        json.dump(content, w)


def chk_dir_and_mkdir(fullpath):
    if not os.path.basename(fullpath):
        fullpath = os.path.join(fullpath, 'temp.py')
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


def extract_file(path, out_dir):
    with zipfile.ZipFile(path, 'r') as zf:
        zf.extractall(out_dir)
