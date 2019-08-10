import argparse
from tqdm.auto import tqdm
import requests
import tempfile
import os


def _download_from_url(url, path):
    """

    :param url: 下载的路径
    :param path: 将下载的数据存放在哪里
    :return:
    """
    """Download file"""
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
    chunk_size = 16 * 1024
    total_size = int(r.headers.get('Content-length', 0))
    with open(path, "wb") as file, \
            tqdm(total=total_size, unit='B', unit_scale=1, desc=path.split('/')[-1]) as t:
        for chunk in r.iter_content(chunk_size):
            if chunk:
                file.write(chunk)
                t.update(len(chunk))

def _check_output_dir(output):
    """
    检查output路径是否是合法的folder，如果该路径不存在，就创建

    :param output:
    :return:
    """
    if os.path.isdir(output):
        pass
    elif os.path.isfile(output):
        raise RuntimeError("You are passing a file.")
    else:
        os.makedirs(output, exist_ok=True)


def _uncompress(src, dst):
    import zipfile
    import gzip
    import tarfile
    import os

    def unzip(src, dst):
        with zipfile.ZipFile(src, 'r') as f:
            f.extractall(dst)

    def ungz(src, dst):
        with gzip.open(src, 'rb') as f, open(dst, 'wb') as uf:
            length = 16 * 1024  # 16KB
            buf = f.read(length)
            while buf:
                uf.write(buf)
                buf = f.read(length)

    def untar(src, dst):
        with tarfile.open(src, 'r:gz') as f:
            f.extractall(dst)

    fn, ext = os.path.splitext(src)
    _, ext_2 = os.path.splitext(fn)
    if ext == '.zip':
        unzip(src, dst)
    elif ext == '.gz' and ext_2 != '.tar':
        ungz(src, dst)
    elif (ext == '.gz' and ext_2 == '.tar') or ext_2 == '.tgz':
        untar(src, dst)
    else:
        raise ValueError('unsupported file {}'.format(src))

def _download(output, suffix, url):
    """
    下载脚本，
    :param output: 将解压后的内容放在哪里
    :param suffix: 下载的数据的后缀是什么
    :param url: 下载地址
    :return:
    """
    if os.path.isdir(output):
        pass
    elif os.path.isfile(output):
        raise RuntimeError("You are passing a file.")
    else:
        os.makedirs(output, exist_ok=True)
    fd, temp_filename = tempfile.mkstemp(suffix=suffix)  # 先下载到temporay目录，防止下载失败
    try:
        print(f"Downloading from {url} to {temp_filename}.")
        _download_from_url(url, temp_filename)
        print("Finish downloading, start to uncompressing")
        _uncompress(temp_filename, output)
    finally:
        os.remove(temp_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download SST data, and unzip train.txt, test.txt. dev.txt.")
    parser.add_argument('-o', '--output', required=True, type=str, help="Folder to save train.txt, dev.txt, test.txt")

    args = parser.parse_args()

    url = 'https://nlp.stanford.edu/sentiment/trainDevTestTrees_PTB.zip'

    output = args.output

    # 检查output
    _check_output_dir(output)

    # 下载, 并解压到output
    _download(output, '.zip', url)


