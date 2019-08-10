import argparse
from tqdm.auto import tqdm
import requests
import tempfile
import os
import random

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

def _download(output, suffix, url):
    """
    下载脚本，
    :param output: 将解压后的内容放在哪里
    :param suffix: 下载的数据的后缀是什么
    :param url: 下载地址
    :return:
    """
    fd, temp_filename = tempfile.mkstemp(suffix=suffix)  # 先下载到temporay目录，防止下载失败
    try:
        print(f"Downloading from {url} to {temp_filename}.")
        _download_from_url(url, temp_filename)
        print("Finish downloading, start to uncompressing")
        _uncompress(temp_filename, output)
    finally:
        os.remove(temp_filename)


def process(data_dir, output, seed=-1, ratio=0.1):
    def read_files(files, label):
        lines = []
        for file_name in files:
            with open(os.path.join(data_dir, file_name), 'r', encoding='utf-8') as f:
                for line in f:
                    lines.append('\t'.join([label, line]))
        return lines
    test_lines = []
    for label in ['neg', 'pos']:
        files = os.listdir(os.path.join(data_dir, 'test', label))
        test_lines.extend(read_files(files, label))
    tr_neg_lines = []
    tr_pos_lines = []
    files = os.listdir(os.path.join(data_dir, 'train', 'neg'))
    tr_neg_lines.extend(read_files(files, 'neg'))
    files = os.listdir(os.path.join(data_dir, 'train', 'pos'))
    tr_pos_lines.extend(read_files(files, 'pos'))
    if seed>-1:
        random.shuffle(tr_neg_lines)
        random.shuffle(tr_pos_lines)
    dev_lines = tr_neg_lines[:int(len(tr_neg_lines)*ratio)] + tr_pos_lines[:int(len(tr_pos_lines)*ratio)]
    random.shuffle(dev_lines)
    tr_lines = tr_neg_lines[int(len(tr_neg_lines)*ratio):] + tr_pos_lines[int(len(tr_pos_lines)*ratio):]
    random.shuffle(tr_lines)
    def _save_lines(lines, file_name):
        with open(os.path.join(output, file_name), 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line)
    _save_lines(test_lines, 'test.txt')
    _save_lines(tr_lines, 'train.txt')
    _save_lines(dev_lines, 'dev.txt')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download IMDB data, and generate train.txt, test.txt. dev.txt.")
    parser.add_argument('-o', '--output', required=True, type=str, help="Folder to save train.txt, dev.txt, test.txt")
    parser.add_argument('-s', '--seed', required=False, type=int, help="Seed to shuffle data.",
                        default=-1)
    parser.add_argument('-r', '--dev-ratio', required=False, type=float, help="How many data to split from train to "
                                                                              "be as dev.",
                        default=0.1)
    parser.add_argument('-k', '--keep', action='store_true', help='Keep raw data.', default=False)
    args = parser.parse_args()

    output = args.output
    seed = args.seed
    assert 0<args.dev_ratio<1
    if seed>-1:
        random.seed(seed)

    url = "http://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz"

    # 确认路径
    _check_output_dir(output)

    # 下载脚本
    _download(output, '.tar.gz', url)

    # 预处理
    data_dir = os.path.join(output, 'aclImdb')
    process(data_dir, output, seed, args.dev_ratio)

    if args.keep:
        import shutil
        shutil.rmtree(data_dir)
