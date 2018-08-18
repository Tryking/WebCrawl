# -*- coding: utf-8 -*-
"""
https://69story.com/
"""
import scrapy
from ..libs.common import *

"""
2018年8月17日15:09:03 已跑过一遍

2018-08-17 15:04:16 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/exception_count': 31,
 'downloader/exception_type_count/twisted.internet.error.TimeoutError': 19,
 'downloader/exception_type_count/twisted.web._newclient.ResponseNeverReceived': 12,
 'downloader/request_bytes': 336985,
 'downloader/request_count': 824,
 'downloader/request_method_count/GET': 824,
 'downloader/response_bytes': 21423987,
 'downloader/response_count': 793,
 'downloader/response_status_count/200': 793,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2018, 8, 17, 7, 4, 16, 974834),
 'log_count/DEBUG': 825,
 'log_count/INFO': 32,
 'request_depth_max': 5,
 'response_received_count': 793,
 'retry/count': 31,
 'retry/reason_count/twisted.internet.error.TimeoutError': 19,
 'retry/reason_count/twisted.web._newclient.ResponseNeverReceived': 12,
 'scheduler/dequeued': 824,
 'scheduler/dequeued/memory': 824,
 'scheduler/enqueued': 824,
 'scheduler/enqueued/memory': 824,
 'start_time': datetime.datetime(2018, 8, 17, 6, 39, 25, 23286)}
"""
TYPE = ['wife', 'school', 'family', 'bdsm-abuse', 'sex-in-the-city']
SAVE_DIR = 'texts' + os.path.sep + '69story'


class StorySpider(scrapy.Spider):
    # if not os.path.exists('logs'):
    #     os.mkdir('logs')
    # init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    # init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    name = '69_story_spider'
    allowed_domains = ['69story.com']
    start_urls = ['https://69story.com/']
    HOST = 'https://69story.com'

    def start_requests(self):
        for _type in TYPE:
            url = self.HOST + '/' + _type
            yield scrapy.Request(url=url, callback=self.parse, headers=get_headers())

    def parse(self, response):
        urls = response.xpath('//table//tr/td[@class="entry-content"]/a/@href').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_article, meta={'proxy': get_proxy()}, headers=get_headers())
        # 多页
        next_page_url = response.xpath('//div[contains(@class, "nopadding")]/ul/li/a[text()="下頁"]/@href').extract_first()
        if next_page_url:
            yield scrapy.Request(url=next_page_url, callback=self.parse, meta={'proxy': get_proxy()}, headers=get_headers())

    def parse_article(self, response):
        # 这个获取逇是图片的详情页面，在这里面再获取图片的比较高清的图
        article_title = response.xpath('//header[@class="entry-header"]/h1[@class="entry-title"]/text()').extract_first()
        article_texts = response.xpath('//div[@class="entry-content"]/p/text()').extract()
        if not article_title:
            article_title = 'default'
        if article_texts and len(article_texts) > 0:
            with open(SAVE_DIR + os.path.sep + article_title + '.txt', mode='a+', encoding='utf-8') as f:
                for article_text in article_texts:
                    f.write(article_text)
                    f.write('\n')
