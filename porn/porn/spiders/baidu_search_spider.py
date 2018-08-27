# -*- coding: utf-8 -*-
"""
百度搜索图片Spider（根据链接文件下载）
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

Files = ['女人.txt']


class BaiduSearchSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'baidu_search_spider'
    allowed_domains = ['baidu.com']
    start_urls = ['https://image.baidu.com/']
    HOST = 'https://image.baidu.com'

    def parse(self, response):
        for file in Files:
            urls = list()
            with open(file=file, mode='r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    url = line.strip()
                    urls.append(url)
            item = MyItem()
            item['image_urls'] = urls
            item['save_sub_dir'] = file.replace('.txt', '')
            yield item
