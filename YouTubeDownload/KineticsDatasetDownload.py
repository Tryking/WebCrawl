"""
Kinetics 数据集下载

https://deepmind.com/research/open-source/open-source-datasets/kinetics/

"""
import logging
import os
import subprocess
from time import sleep

FILE_NAME = 'kinetics_train.csv'

SAVE_DIR = 'train'

logging.basicConfig(format='%(name)-6s %(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG,
                    filename=str(os.path.split(__file__)[1].split(".")[0]) + ".log")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: - %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
# 使用FileHandler输出到文件
fh = logging.FileHandler(str(os.path.split(__file__)[1].split(".")[0]) + ".log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
# 使用StreamHandler输出到屏幕
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
# 添加两个Handler
logger.addHandler(ch)
logger.addHandler(fh)

with open(file=FILE_NAME, mode='r', encoding='utf-8') as f:
    content = f.read()
    content = content.split('\n')
    id_set = set()
    for item in content:
        if len(item.split(',')) > 1 and item.split(',')[1] != '' and item.split(',')[1] != 'youtube_id':
            id_set.add(item.split(',')[1])

    for i, item in enumerate(id_set):
        # print(item)
        url = 'https://www.youtube.com/watch?v={}'.format(item)
        save_file = os.path.join(SAVE_DIR, item + '.mp4')
        if not os.path.isfile(save_file):
            logger.debug(', '.join([item, url, save_file]))
            task = subprocess.Popen(args=['youtube-dl', url, '-o', save_file])
            task.wait()
            logger.debug('{}/{} downloaded...sleep...'.format(i, len(id_set)))
            sleep(2)
        else:
            logger.debug('{}/{} has downloaded...ignore...'.format(i, len(id_set)))
