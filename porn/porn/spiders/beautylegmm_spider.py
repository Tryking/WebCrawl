"""
百度搜索 beauty leg
http://www.beautylegmm.com/
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

"""
scrapy.statscollectors 2018-08-21 01:30:31,848 INFO     Dumping Scrapy stats:
{'downloader/exception_count': 119,
 'downloader/exception_type_count/twisted.internet.error.TimeoutError': 119,
 'downloader/request_bytes': 2689992,
 'downloader/request_count': 6849,
 'downloader/request_method_count/GET': 6849,
 'downloader/response_bytes': 2391781834,
 'downloader/response_count': 6730,
 'downloader/response_status_count/200': 6497,
 'downloader/response_status_count/302': 231,
 'downloader/response_status_count/404': 2,
 'dupefilter/filtered': 1051,
 'file_count': 4843,
 'file_status_count/downloaded': 4833,
 'file_status_count/uptodate': 10,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2018, 8, 20, 17, 30, 31, 847556),
 'item_scraped_count': 1537,
 'log_count/DEBUG': 13231,
 'log_count/ERROR': 2,
 'log_count/INFO': 142,
 'log_count/WARNING': 192,
 'memusage/max': 339357696,
 'memusage/startup': 53850112,
 'request_depth_max': 17,
 'response_received_count': 6680,
 'retry/count': 110,
 'retry/max_reached': 9,
 'retry/reason_count/twisted.internet.error.TimeoutError': 110,
 'scheduler/dequeued': 1729,
 'scheduler/dequeued/memory': 1729,
 'scheduler/enqueued': 1729,
 'scheduler/enqueued/memory': 1729,
 'start_time': datetime.datetime(2018, 8, 20, 15, 16, 21, 204907)}

"""


class BeautyLegMmSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'beautylegmm_spider'
    allowed_domains = ['beautylegmm.com']
    start_urls = ['http://www.beautylegmm.com/']
    HOST = 'http://www.beautylegmm.com'

    def parse(self, response):
        urls = response.xpath('//div[@class="post_weidaopic"]/a/@href').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_album, headers=get_headers())
        # 多页
        other_pages = response.xpath('//ol[@class="page-navigator"]/li/a/@href').extract()
        for other_page in other_pages:
            yield scrapy.Request(url=other_page, callback=self.parse, headers=get_headers())

    def parse_album(self, response):
        image_detail_urls = response.xpath('//div[@class="post"]/a/@href').extract()
        if image_detail_urls and len(image_detail_urls) > 0:
            image_urls = list()
            for image_url in image_detail_urls:
                if self.HOST not in image_url:
                    image_url = self.HOST + image_url
                image_url = image_url.replace('t.jpg', '.jpg')
                image_urls.append(image_url)
            item = MyItem()
            item['referer'] = response.request.url
            item['image_urls'] = image_urls
            yield item
