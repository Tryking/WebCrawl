# -*- coding: utf-8 -*-
"""
https://www.fanqianglu.com/free/cnnovel/  提供网址

绅士风度  http://abc111.cc/article/index
"""
import scrapy
from ..libs.common import *

"""
2018年8月17日16:18:38

在服务器爬取
"""

SAVE_DIR = 'texts' + os.path.sep + 'abc111'


class Abc111Spider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    name = 'abc111_spider'
    allowed_domains = ['abc111.cc']
    start_urls = ['http://abc111.cc/article/index']
    HOST = 'http://abc111.cc'

    def parse(self, response):
        urls = response.xpath('//a[@class="article-link"]/@href').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_article, headers=get_headers())
        # 多页
        next_page_url = response.xpath('//a[contains(text(),"下一页")]/@href').extract_first()
        if next_page_url:
            if self.HOST not in next_page_url:
                next_page_url = self.HOST + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse, meta={'proxy': get_proxy()}, headers=get_headers())

    def parse_article(self, response):
        # 解析文章
        article_title = response.xpath('//div[@class="content"]/h1/text()').extract_first()
        article_texts = response.xpath('//div[@class="content"]/div/div/p/text()').extract()
        if not article_title:
            article_title = 'default'
        article_title = get_standard_file_name(article_title)
        if article_texts and len(article_texts) > 0:
            with open(SAVE_DIR + os.path.sep + article_title + '.txt', mode='a+', encoding='utf-8') as f:
                for article_text in article_texts:
                    f.write(article_text)
                    f.write('\n')
