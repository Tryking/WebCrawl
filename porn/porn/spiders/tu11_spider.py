"""
百度搜索 beauty leg
http://www.tu11.com/
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

"""
爬取时间长会限制IP
2018-08-21 06:58:31 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/exception_count': 7119,
 'downloader/exception_type_count/twisted.internet.error.TimeoutError': 7102,
 'downloader/exception_type_count/twisted.web._newclient.ResponseFailed': 17,
 'downloader/request_bytes': 9546975,
 'downloader/request_count': 25400,
 'downloader/request_method_count/GET': 25400,
 'downloader/response_bytes': 3407215525,
 'downloader/response_count': 18281,
 'downloader/response_status_count/200': 15474,
 'downloader/response_status_count/301': 2,
 'downloader/response_status_count/404': 277,
 'downloader/response_status_count/500': 2526,
 'downloader/response_status_count/504': 2,
 'dupefilter/filtered': 19608,
 'file_count': 13060,
 'file_status_count/downloaded': 13060,
 'finish_reason': 'shutdown',
 'finish_time': datetime.datetime(2018, 8, 20, 22, 58, 31, 357909),
 'httperror/response_ignored_count': 1,
 'httperror/response_ignored_status_count/500': 1,
 'item_scraped_count': 2298,
 'log_count/DEBUG': 40812,
 'log_count/INFO': 519,
 'log_count/WARNING': 1132,
 'memusage/max': 1029222400,
 'memusage/startup': 95383552,
 'request_depth_max': 26,
 'response_received_count': 15713,
 'retry/count': 8808,
 'retry/max_reached': 839,
 'retry/reason_count/500 Internal Server Error': 2519,
 'retry/reason_count/504 Gateway Time-out': 2,
 'retry/reason_count/twisted.internet.error.TimeoutError': 6271,
 'retry/reason_count/twisted.web._newclient.ResponseFailed': 16,
 'scheduler/dequeued': 4906,
 'scheduler/dequeued/disk': 4906,
 'scheduler/enqueued': 7617,
 'scheduler/enqueued/disk': 7617,
 'start_time': datetime.datetime(2018, 8, 20, 14, 28, 40, 30561)}

"""
# xingganmeinvxiezhen 美女图片
# meituisiwatupian   丝袜美腿
CATEGORY = ['xingganmeinvxiezhen', 'meituisiwatupian']


class Tu11Spider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'tu11_spider'
    allowed_domains = ['tu11.com']
    start_urls = ['http://www.tu11.com/']
    HOST = 'http://www.tu11.com'

    def start_requests(self):
        for category in CATEGORY:
            url = self.HOST + '/' + category
            yield scrapy.Request(url=url, callback=self.parse, meta={'category': category}, headers=get_headers())

    def parse(self, response):
        urls = response.xpath('//ul/li/div[@class="shupic"]/a/@href').extract()
        for url in urls:
            if self.HOST not in url:
                url = self.HOST + url
            yield scrapy.Request(url=url, callback=self.parse_album,
                                 meta={'category': response.meta['category']}, headers=get_headers())
        # 多页
        other_pages = response.xpath('//div[@class="pageinfo"]/li/a/@href').extract()
        for other_page in other_pages:
            yield scrapy.Request(url=other_page, callback=self.parse,
                                 meta={'category': response.meta['category']}, headers=get_headers())

    def parse_album(self, response):
        image_detail_urls = response.xpath('//div[@class="nry"]/p/img/@src').extract()
        if image_detail_urls and len(image_detail_urls) > 0:
            item = MyItem()
            item['referer'] = response.request.url
            item['image_urls'] = image_detail_urls
            item['save_sub_dir'] = response.meta['category']
            yield item
        # 多页
        other_pages = response.xpath('//div[contains(@class,"dede_pages")]/ul/li/a/@href').extract()
        for other_page in other_pages:
            url = other_page
            if self.HOST not in other_page:
                url = response.request.url.rsplit('/', 1)[0] + '/' + other_page
            yield scrapy.Request(url=url, callback=self.parse_album,
                                 meta={'category': response.meta['category']}, headers=get_headers())
