# -*- coding: utf-8 -*-
"""
sogou wechat 公众号爬取

未完成（使用splash请求多了会报错）
"""

import scrapy
import scrapy_splash
from scrapy_splash import SplashRequest

from ..libs.common import *
from ..libs.db import *

NAME = 'sogou_wechat'
BASE_URL = 'https://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=y&_sug_type_=&' \
           'w=01019900&sut=1292&sst0=1534838560197&lkt=1,1534838560083,1534838560083'


class SogouWechatSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'sogou_wechat_spider'
    allowed_domains = ['sogou.com', 'weixin.qq.com']
    start_urls = ['']
    HOST = 'https://wp.weixin.qq.com'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_monitor = DbMonitor()
        self.proxy = get_available_ip_proxy()

    def start_requests(self):
        keyword = '好'
        url = BASE_URL % keyword
        yield SplashRequest(url=url, callback=self.parse,
                            meta={'keyword': keyword},
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

    def parse(self, response):
        # 公众号列表
        subscriptions = response.xpath('//ul[@class="news-list2"]/li//div[@class="img-box"]/a/@href').extract()

        for subscription in subscriptions:
            yield SplashRequest(url=subscription, callback=self.parse_subscription,
                                meta={'keyword': response.meta['keyword']},
                                args={
                                    # optional; parameters passed to Splash HTTP API
                                    'wait': 0.5,
                                    'proxy':self.proxy,
                                    # 'url' is prefilled from request url
                                    # 'http_method' is set to 'POST' for POST requests
                                    # 'body' is set to request body for POST requests
                                },
                                # endpoint='render.json',  # optional; default is render.html
                                # splash_url='<url>',  # optional; overrides SPLASH_URL
                                slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,  # optional
                                )
        # 其他页面
        other_pages = response.xpath('//div[@id="pagebar_container"]/a[contains(@id,"sogou_page")]/@href').extract()
        for other_page in other_pages:
            yield SplashRequest(url=other_page, callback=self.parse,
                                meta={'keyword': response.meta['keyword']},
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

    def parse_subscription(self, response):
        # 公众号名称
        wechat_name = response.xpath('//div[@class="profile_info"]/strong[@class="profile_nickname"]/text()').extract_first()
        # 有的公众号没有显示Id
        wechat_id = response.xpath('//div[@class="profile_info"]/p[@class="profile_account"]/text()').extract_first()
        # 文章列表
        articles = response.xpath(
            '//div[@class="weui_msg_card"]/div[@class="weui_msg_card_bd"]/div[contains(@class, "weui_media_box")]//h4/@hrefs').extract()
        for article in articles:
            yield SplashRequest(url=article, callback=self.parse_article,
                                meta={'keyword': response.meta['keyword']},
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
        name = response.xpath('//h2[@class="rich_media_title"]').extract_first()
        publish_time = response.xpath('//em[id="publish_time"]').extract_first()
        print('哈哈')
