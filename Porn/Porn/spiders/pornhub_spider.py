"""
https://www.pornhub.com 图片
"""

import scrapy
from libs.common import *

SAVE_DIR = 'pornhub_datas'


class PornhubSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + 'pornhub_spider' + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + 'pornhub_spider' + "_error.log")
    name = "pornhub_spider"
    host = "https://www.pornhub.com"

    def start_requests(self):
        urls = [
        
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.handle_failure)

    def parse(self, response):
        pass

    def parse_post(self, response):
        pass

    def handle_failure(self, failure):
        url = failure.request.url

    @staticmethod
    def write_file_log(msg, level='error'):
        filename = os.path.split(__file__)[1]
        if level == 'debug':
            logging.getLogger().debug('File:' + filename + ': ' + msg)
        elif level == 'warning':
            logging.getLogger().warning('File:' + filename + ': ' + msg)
        else:
            logging.getLogger().error('File:' + filename + ': ' + msg)

    # 调试日志
    def debug(self, msg):
        self.write_file_log(msg, 'debug')

    # 错误日志
    def error(self, msg):
        self.write_file_log(msg, 'error')
