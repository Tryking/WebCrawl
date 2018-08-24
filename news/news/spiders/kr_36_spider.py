# -*- coding: utf-8 -*-
"""
36 Kr 新闻爬取
http://36kr.com/
"""

import scrapy
import scrapy_splash
from scrapy_splash import SplashRequest

from ..items import NewsItem
from ..libs.common import *
from ..libs.db import *

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

NAME = 'kr36'


class Kr36Spider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'kr_36_spider'
    allowed_domains = ['36kr.com']
    start_urls = ['http://36kr.com/']
    HOST = 'http://36kr.com'

    def __init__(self):
        self.db_monitor = DbMonitor()

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
            user_info = data['user_info']
            user_info = json.loads(user_info)
            article_author = user_info['nickname']
            article_type = data['column_name']
            article_url = ARTICLE_URL % article_id
            # 没有匹配记录时才继续添加
            if not self.db_monitor.match_article(name=NAME, author=article_author, title=article_title):
                yield SplashRequest(url=article_url, callback=self.parse_article,
                                    meta={'article_type': article_type, 'article_author': article_author},
                                    args={
                                        # optional; parameters passed to Splash HTTP API
                                        'wait': 0.5,

                                        # 'url' is prefilled from request url
                                        # 'http_method' is set to 'POST' for POST requests
                                        # 'body' is set to request body for POST requests
                                    },
                                    # endpoint='render.json',  # optional; default is render.html
                                    # splash_url='<url>',  # optional; overrides SPLASH_URL
                                    slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,  # optional
                                    )

    def parse_article(self, response):
        # 解析文章
        title = response.xpath('//div[@class="mobile_article"]/h1/text()').extract_first()
        content = response.xpath('//section[@class="textblock"]')
        content = content.xpath('string(.)').extract_first()
        item = NewsItem()
        item['name'] = NAME
        item['article_title'] = title
        item['article_author'] = response.meta['article_author']
        item['article_type'] = response.meta['article_type']
        item['article_content'] = content
        yield item
