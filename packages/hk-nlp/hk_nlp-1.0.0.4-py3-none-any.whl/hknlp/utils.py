import os
import zipfile
import json


def read_json(path):
    with open(path, 'r', encoding='utf-8') as r:
        return json.load(r)


def write_json(path, content, encoding='utf-8'):
    with open(path, 'w', encoding=encoding) as w:
        json.dump(content, w)


def read_text(path, encoding='utf-8'):
    with open(path, 'r', encoding=encoding) as r:
        return r.read()


def write_text(path, content, encoding='utf-8'):
    with open(path, 'w', encoding=encoding) as w:
        w.write(path, content)


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


def get_all_path(path, ext=None):
    all_path = []
    for d in os.listdir(path):
        sub = os.path.join(path, d)
        if os.path.isdir(sub):
            all_path += get_all_path(sub)
        else:
            _, tar_ext = os.path.splitext(sub)
            if ext and ext != tar_ext:
                continue
            all_path.append(sub)
    return all_path


def extract_file(path, out_dir):
    with zipfile.ZipFile(path, 'r') as zf:
        zf.extractall(out_dir)


if __name__ == "__main__":
    get_all_path("")