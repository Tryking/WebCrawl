import logging
import os
import subprocess
import time

import schedule

"""
定时启动 豆瓣 爬虫任务 脚本
"""
RUN_PATH = 'douban'

logging.basicConfig(filename=str(os.path.split(__file__)[1].split(".")[0]) + ".log", level=logging.INFO,
                    format='%(asctime)s %(name)-6s %(levelname)-8s %(message)s')


def run_douban_crawl():
    logging.info('task start...')
    task = subprocess.Popen(args=['python', 'start.py'], cwd=RUN_PATH)
    task.wait()
    logging.info('task end...')


# 每周二 20:05 开启
schedule.every().tuesday.at('20:05').do(run_douban_crawl)
logging.info('schedule running...')
while True:
    schedule.run_pending()
    time.sleep(5)
