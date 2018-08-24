#!/usr/bin/python
# -*- coding: utf-8 -*-
import math
import os

"""
未完成，有问题，提示文件找不到
"""
# 一个文件夹存多少文件
import shutil

FILE_BATCH = 10000


def make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def list_files(path):
    return [f for f in os.listdir(path=path) if os.path.isfile(os.path.join(path, f))]


def find_move_file():
    base_dir = 'part'
    dirs = list_files('.')
    print(len(dirs))
    # 创建文件夹
    for i in range(int(math.ceil(len(dirs) / FILE_BATCH))):
        dir = base_dir + '-' + str(i)
        print(dir)
        make_dir(dir)
    # 移动文件
    for i in range(0, len(dirs), FILE_BATCH):
        start = i
        stop = min(i + FILE_BATCH, len(dirs))
        file_save_dir = base_dir + '-' + str(math.ceil(i / FILE_BATCH))
        for j in (start, stop):
            print(dirs[j])
            shutil.move(dirs[j], os.path.join(file_save_dir, dirs[j]))

    print(len(dirs))


find_move_file()
