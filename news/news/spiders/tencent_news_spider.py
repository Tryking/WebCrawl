# -*- coding: utf-8 -*-
"""
腾讯新闻爬取
https://new.qq.com/
"""

import scrapy
from news.news.spiders_selenium.libs.common import *


class StorySpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'tencent_news_spider'
    allowed_domains = ['new.qq.com']
    start_urls = ['https://mat1.gtimg.com/pingjs/ext2020/configF2017/5a9cf828.js']
    HOST = 'https://new.qq.com/'

    def parse(self, response):
        result = response.text
        split = result.split('=', 1)
        if len(split) > 1:
            split.split('')
            result = split[1]
            result = json.loads(result)
            category_urls = response.xpath('//ul[@id="main-list"]/li').extract()
            for url in category_urls:
                yield scrapy.Request(url=url, callback=self.parse_category, headers=get_headers())

    def parse_category(self, response):
        sub_categorys = response.xpath('//li[@class="item"]').extract()
        for sub_category in sub_categorys:
            category_txt = sub_category.response('./a/text()')
            category_url = sub_category.response('./a/@href')
            if self.HOST not in category_url:
                category_url = self.HOST + category_url
            yield scrapy.Request(url=category_url, callback=self.parse_sub_category, headers=get_headers())

    def parse_sub_category(self, response):
        articles = response.xpath('//ul[@class="list"]/li')
        for article in articles:
            url = article.xpath('./a/@href')
            yield scrapy.Request(url=url, callback=self.parse_article, headers=get_headers())

    def parse_article(self, response):
        article_title = response.xpath('//div[@class="LEFT"]/h1/text()').extract_first()
        article_contents = response.xpath('//div[@class="content-article"]/p').extract()
        article_title = get_standard_file_name(article_title)
        with open(file=article_title, mode='a+', encoding='utf-8') as f:
            for article_content in article_contents:
                f.write(str(article_content))
                f.write('\n')
