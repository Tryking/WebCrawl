"""
任务调度
"""

import datetime
import os
import subprocess
import time

import schedule

from libs.common import *

TASK_PATH = '/home/ReincarnationEyes/PycharmProjects/news/news'


class Master(object):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG,
             logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR,
             logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    def __init__(self):
        self.__module = self.__class__.__name__

    @staticmethod
    def write_file_log(msg, __module='', level='error'):
        filename = os.path.split(__file__)[1]
        if level == 'debug':
            logging.getLogger().debug('File:' + filename + ', ' + __module + ': ' + msg)
        elif level == 'warning':
            logging.getLogger().warning('File:' + filename + ', ' + __module + ': ' + msg)
        else:
            logging.getLogger().error('File:' + filename + ', ' + __module + ': ' + msg)

    # debug log
    def debug(self, msg, func_name=''):
        __module = "%s.%s" % (self.__module, func_name)
        self.write_file_log(msg, __module, 'debug')

    # error log
    def error(self, msg, func_name=''):
        __module = "%s.%s" % (self.__module, func_name)
        self.write_file_log(msg, __module, 'error')

    def init_kr36_crawl(self):
        """
        启动Kr36爬虫脚本
        """
        try:
            self.debug('Kr36 爬虫开始')
            jinritoutiao_spider = subprocess.Popen(args=['scrapy', 'crawl', 'kr_36_spider'], cwd=TASK_PATH)
            jinritoutiao_spider.wait()
            self.debug('Kr36 爬虫结束')
        except Exception as e:
            self.error(str(e), get_current_func_name())

    def init_toutiao_crawl(self):
        """
        启动今日头条爬虫脚本
        """
        try:
            self.debug('头条 爬虫开始')
            jinritoutiao_spider = subprocess.Popen(args=['scrapy', 'crawl', 'toutiao_spider'], cwd=TASK_PATH)
            jinritoutiao_spider.wait()
            self.debug('头条 爬虫结束')
        except Exception as e:
            self.error(str(e), get_current_func_name())

    def main(self):
        self.debug('>>>>>>>>>>running<<<<<<<<<<')
        try:
            schedule.every(60).minutes.do(self.init_kr36_crawl)
            schedule.every(20).minutes.do(self.init_toutiao_crawl())
            while True:
                schedule.run_pending()
                time.sleep(1)
        except Exception as e:
            self.error(str(e), get_current_func_name())


if __name__ == '__main__':
    master = Master()
    master.main()
