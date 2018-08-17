# -*- coding: utf-8 -*-
"""
http://www.zzcartoon.com
"""
import scrapy
from ..items import MyItem
from ..libs.common import *

"""
2018年8月17日16:45:13 运行一次

2018-08-17 16:44:13 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/exception_count': 78,
 'downloader/exception_type_count/twisted.internet.error.TimeoutError': 69,
 'downloader/exception_type_count/twisted.web._newclient.ResponseFailed': 8,
 'downloader/exception_type_count/twisted.web._newclient.ResponseNeverReceived': 1,
 'downloader/request_bytes': 7267017,
 'downloader/request_count': 17616,
 'downloader/request_method_count/GET': 17616,
 'downloader/response_bytes': 7771649571,
 'downloader/response_count': 17538,
 'downloader/response_status_count/200': 14394,
 'downloader/response_status_count/404': 20,
 'downloader/response_status_count/500': 3124,
 'dupefilter/filtered': 26,
 'file_count': 13996,
 'file_status_count/downloaded': 13996,
 'finish_reason': 'shutdown',
 'finish_time': datetime.datetime(2018, 8, 17, 8, 44, 13, 718150),
 'httperror/response_ignored_count': 20,
 'httperror/response_ignored_status_count/404': 20,
 'item_scraped_count': 392,
 'log_count/CRITICAL': 8,
 'log_count/DEBUG': 33247,
 'log_count/INFO': 376,
 'log_count/WARNING': 154,
 'request_depth_max': 2,
 'response_received_count': 14555,
 'retry/count': 3058,
 'retry/max_reached': 144,
 'retry/reason_count/500 Internal Server Error': 2983,
 'retry/reason_count/twisted.internet.error.TimeoutError': 66,
 'retry/reason_count/twisted.web._newclient.ResponseFailed': 8,
 'retry/reason_count/twisted.web._newclient.ResponseNeverReceived': 1,
 'scheduler/dequeued': 501,
 'scheduler/dequeued/memory': 501,
 'scheduler/enqueued': 534,
 'scheduler/enqueued/memory': 534,
 'start_time': datetime.datetime(2018, 8, 17, 2, 50, 15, 68851)}
"""


class ZzcartoonSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'zzcartoon_spider'
    allowed_domains = ['zzcartoon.com']
    start_urls = ['http://www.zzcartoon.com/']
    HOST = 'http://www.zzcartoon.com'

    def parse(self, response):
        urls = response.xpath('//div[@class="list_albums"]/a/@href').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_album, meta={'proxy': get_proxy()}, headers=get_headers())
        # 多页
        next_page_url = response.xpath('//div[@class="article"]/nav/a/@href').extract()
        for page in next_page_url:
            if page:
                next_url = self.HOST + '/albums' + page
                yield scrapy.Request(url=next_url, callback=self.parse, meta={'proxy': get_proxy()}, headers=get_headers())

    def parse_album(self, response):
        # 这个获取逇是图片的详情页面，在这里面再获取图片的比较高清的图
        image_detail_urls = response.xpath('//div[@class="zoom-gallery"]/a/@href').extract()
        if image_detail_urls and len(image_detail_urls) > 0:
            item = MyItem()
            item['referer'] = response.request.url
            item['image_urls'] = image_detail_urls
            yield item
