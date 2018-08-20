# -*- coding: utf-8 -*-
"""
36 Kr 新闻爬取
http://36kr.com/
"""
import json

import scrapy
from ..libs.common import *

# 频道:
# 23：大公司
# 221：消费
# 225：娱乐
# 218：前沿技术
# 219：汽车交通
# 208：区块链
# 103：捷能Get
CHANNEL = {'23': '大公司', '221': '消费', '225': '娱乐', '218': '前沿技术', '219': '汽车交通', '208': '区块链', '103': '技能Get'}

BASE_ULR = 'http://36kr.com/api/search-column/%s?per_page=%s&page=1'
ARTICLE_URL = 'http://36kr.com/p/%s.html'


class Kr36Spider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'kr_36_spider'
    allowed_domains = ['36kr.com']
    start_urls = ['http://36kr.com/']
    HOST = 'http://36kr.com'

    def start_requests(self):
        for channel in CHANNEL:
            url = BASE_ULR % (channel, 20)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # 解析频道
        result = str(response.body, encoding='utf-8')
        result = json.loads(result)

        for data in result['data']['items']:
            article_id = data['id']
            article_title = data['title']
            article_url = ARTICLE_URL % article_id
            yield scrapy.Request(url=article_url, callback=self.parse_article)

    def parse_article(self, response):
        # 解析文章
        result = str(response.body, encoding='utf-8')
        result = re.findall('<script>var props=(.*?)</script>', result)
        if len(result) > 0:
            result = json.loads(result[0])
        print('hh ')
