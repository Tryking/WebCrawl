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

BASE_ULR = 'https://www.toutiao.com/'

NAME = 'news_toutiao'

script = """
function main(splash, args)
    local ok, reason = splash:go(args.url)
    splash:wait(math.random(1, 2))
    html  = splash:html()
    old_html = ""
    flush_times = args.flush_times --这里是下拉次数，就好像操作浏览器一样每次下拉就会加载新的内容
    i = 0
    while(html ~= old_html) -- 当下拉得到的新页面与原来的相同，就认为它已经没有新的内容了，此时就返回
    do
        splash:runjs([[window.scrollTo(0, document.body.scrollHeight)]]) -- 执行js下拉页面
            splash:wait(math.random(1, 2)) -- 这里一定要等待，否则可能会来不及加载，根据我的实验只要大于1s就可以得到下拉加载的新内容，可能具体值需要根据不同的网络环境
            if (flush_times ~= 0 and i == flush_times) then -- 当达到设置下拉上限并且不为0时推出，这里下拉次数为0表示一直下拉直到没有新内容
                print("即将退出循环")
               break
            end
        html = splash:html()
        i = i + 1
    end
    
    return {
        html = splash:html(),
    }
end
"""


class ToutiaoSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'toutiao_spider'
    allowed_domains = ['toutiao.com']
    start_urls = ['https://www.toutiao.com/']
    HOST = 'https://www.toutiao.com'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_monitor = DbMonitor()

    def start_requests(self):
        url = BASE_ULR
        yield SplashRequest(url=url, callback=self.parse,
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
        category = response.xpath('//div[@ga_event="left-channel-click"]/ul/li/a')
        result = dict()
        for item in category:
            url = item.xpath('./@href').extract_first()
            name = item.xpath('./span/text()').extract_first()
            # 不是今日头条的站内新闻
            if 'javascript' not in url and 'www' not in url:
                if url and self.HOST not in url:
                    url = self.HOST + url
                result[name] = url
        # 更多页的内容
        category = response.xpath('//div[@class="wchannel-more-layer"]/ul/li/a')
        for item in category:
            url = item.xpath('./@href').extract_first()
            name = item.xpath('./span/text()').extract_first()
            if 'javascript' not in url and 'www' not in url:
                if url and self.HOST not in url:
                    url = self.HOST + url
                result[name] = url

        for item in result:
            yield SplashRequest(url=result[item], callback=self.parse_article_list,
                                # 必须有此属性，否则无法执行lua脚本
                                endpoint='execute',
                                meta={'article_type': item},
                                args={
                                    # optional; parameters passed to Splash HTTP API
                                    'lua_source': script,
                                    'flush_times': 10,
                                    # 'url' is prefilled from request url
                                    # 'http_method' is set to 'POST' for POST requests
                                    # 'body' is set to request body for POST requests
                                },
                                # endpoint='render.json',  # optional; default is render.html
                                # splash_url='<url>',  # optional; overrides SPLASH_URL
                                slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,  # optional
                                )

    def parse_article_list(self, response):
        articles = response.xpath('//div[@class="rbox-inner"]')
        if len(articles) == 0:
            articles = response.xpath('//div[@class ="single-mode-rbox-inner"]')

        for article in articles:
            source_from = article.xpath('.//a[contains(@class, "source")]/text()').extract_first()
            source_from = self.get_clean_name(source_from)
            title = article.xpath('./div[@class="title-box"]/a/text()').extract_first()
            if not self.db_monitor.match_article(name='news_toutiao', author=source_from, title=title):
                url = article.xpath('./div[@class="title-box"]/a/@href').extract_first()
                if self.HOST not in url:
                    url = self.HOST + url
                yield SplashRequest(url=url, callback=self.parse_article,
                                    meta={'article_author': source_from, 'article_type': response.meta['article_type'], 'article_title': title},
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
        title = response.xpath('//h1[@class="article-title"]/text()').extract_first()
        if title:
            title = title.strip()
        title = response.meta['article_title']
        content = response.xpath('//div[@class="article-content"]')
        content = content.xpath('string(.)').extract_first()
        item = NewsItem()
        item['name'] = NAME
        item['article_title'] = title
        item['article_author'] = response.meta['article_author']
        item['article_type'] = response.meta['article_type']
        item['article_content'] = content
        yield item

    def get_clean_name(self, original_title):
        return original_title.replace('⋅', '')
