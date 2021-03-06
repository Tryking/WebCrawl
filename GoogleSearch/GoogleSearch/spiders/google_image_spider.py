"""
Google 搜索图片Spider
"""
from items import MyItem
import os
import re

import scrapy
from libs.common import *


class GoogleImageSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + 'facetiae_spider' + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + 'facetiae_spider' + "_error.log")
    name = "google_image_spider"
    host = "https://www.google.com"

    def start_requests(self):
        urls = [
            'https://www.baidu.com'
        ]
        for url in urls:
            yield scrapy.Request(url=url, headers=get_headers(), callback=self.parse, errback=self.handle_failure)

    def parse(self, response):
        dirs = os.listdir('.')
        for file in dirs:
            if '_url' in file:
                with open(file=file, mode='r', encoding='utf-8') as f:
                    lines = f.readlines()
                    urls = list()
                    for line in lines:
                        urls.append(line.strip())
                    item = MyItem()
                    item['image_urls'] = urls
                    yield item

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
