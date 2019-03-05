import subprocess
import time

import schedule

"""
定时启动 豆瓣 爬虫任务 脚本
"""
RUN_PATH = 'douban'


def run_douban_crawl():
    print('task start')
    task = subprocess.Popen(args=['python', 'start.py'], cwd=RUN_PATH)
    task.wait()
    print('task end')


# 每周二 19:32 开启
schedule.every().tuesday.at('19:32').do(run_douban_crawl)
while True:
    schedule.run_pending()
    time.sleep(5)
