# -*- coding: utf-8 -*-
"""
图片链接搜索Spider（根据链接文件下载）
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

Files = ['fall11_result30_10w.txt']


class FileUrlSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'file_url_spider'
    # allowed_domains = ['baidu.com']
    start_urls = ['https://image.baidu.com/']
    HOST = 'https://image.baidu.com'

    def parse(self, response):
        for file in Files:
            with open(file=file, mode='r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    type_url = line.split('\t')
                    if len(type_url) == 2:
                        _type = type_url[0].strip()
                        url = type_url[1].strip()
                        urls = [url]
                        item = MyItem()
                        item['image_urls'] = urls
                        item['save_sub_dir'] = _type
                        yield item
