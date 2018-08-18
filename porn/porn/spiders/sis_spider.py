# -*- coding: utf-8 -*-
"""
https://www.fanqianglu.com/free/cnnovel/  提供网址

sis文学网  https://b.sis.la/
"""
import scrapy
from ..libs.common import *

"""
2018-08-18 17:09:17 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/exception_count': 1,
 'downloader/exception_type_count/twisted.internet.error.TimeoutError': 1,
 'downloader/request_bytes': 112441,
 'downloader/request_count': 281,
 'downloader/request_method_count/GET': 281,
 'downloader/response_bytes': 5182726,
 'downloader/response_count': 280,
 'downloader/response_status_count/200': 280,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2018, 8, 18, 9, 9, 17, 978818),
 'log_count/DEBUG': 327,
 'log_count/INFO': 13,
 'memusage/max': 165904384,
 'memusage/startup': 95772672,
 'request_depth_max': 2,
 'response_received_count': 280,
 'retry/count': 1,
 'retry/reason_count/twisted.internet.error.TimeoutError': 1,
 'scheduler/dequeued': 281,
 'scheduler/dequeued/disk': 281,
 'scheduler/enqueued': 281,
 'scheduler/enqueued/disk': 281,
 'start_time': datetime.datetime(2018, 8, 18, 9, 4, 4, 883440)}
"""

SAVE_DIR = 'texts' + os.path.sep + 'sis'


class Abc111Spider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    name = 'sis_spider'
    allowed_domains = ['b.sis.la']
    start_urls = ['https://b.sis.la/']
    HOST = 'https://b.sis.la'

    def parse(self, response):
        type_urls = response.xpath('//div[@id="widget-panel"]/ul/li/a/@href').extract()
        for url in type_urls:
            if self.HOST not in url:
                url = self.HOST + url
            yield scrapy.Request(url=url, callback=self.parse_title_list, dont_filter=True, headers=get_headers())

    def parse_title_list(self, response):
        articles = response.xpath('//td[@class="entry-content"]/a')
        for article in articles:
            url = article.xpath('./@href').extract_first()
            title = article.xpath('./text()').extract_first()
            if title:
                category = 'default'
                title_txt = 'default'
                if len(title.split('/')) > 1:
                    category = title.split('/')[1]
                    title_txt = title.split('/')[0]
                if self.HOST not in url:
                    url = self.HOST + url
                yield scrapy.Request(url=url, callback=self.parse_article,
                                     meta={'category': category, 'title': title_txt}, headers=get_headers())
        next_page_url = response.xpath('//a[text()="下頁"]/@href').extract_first()
        if next_page_url:
            if self.HOST not in next_page_url:
                next_page_url = self.HOST + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_title_list, headers=get_headers())

    def parse_article(self, response):
        category = response.meta['category']
        title = response.meta['title']
        # 解析文章
        article_title = response.xpath('//header[@class="entry-header"]/h1/text()').extract_first()
        article_texts = response.xpath('//main/article/div[@class="entry-content"]/p/text()').extract()
        if not article_title:
            article_title = 'default'
        article_title = get_standard_file_name(article_title)
        if not os.path.exists(SAVE_DIR + os.path.sep + category):
            os.makedirs(SAVE_DIR + os.path.sep + category)
        if article_texts and len(article_texts) > 0:
            with open(SAVE_DIR + os.path.sep + category + os.path.sep + article_title + '.txt', mode='a+', encoding='utf-8') as f:
                for article_text in article_texts:
                    f.write(article_text)
                    f.write('\n')
