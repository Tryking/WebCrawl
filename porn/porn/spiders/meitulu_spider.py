"""
百度搜索 beauty leg
https://www.meitulu.com/
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

"""
/CONCURRENT_REQUESTS = 20       DOWNLOAD_DELAY = 0.3 不会被限制/
scrapy.statscollectors 2018-08-23 19:16:25,775 INFO     Dumping Scrapy stats:
{'downloader/exception_count': 136,
 'downloader/exception_type_count/twisted.internet.error.TimeoutError': 135,
 'downloader/exception_type_count/twisted.web._newclient.ResponseFailed': 1,
 'downloader/request_bytes': 99682543,
 'downloader/request_count': 278354,
 'downloader/request_method_count/GET': 278354,
 'downloader/response_bytes': 71208036837,
 'downloader/response_count': 278218,
 'downloader/response_status_count/200': 278216,
 'downloader/response_status_count/404': 1,
 'downloader/response_status_count/502': 1,
 'dupefilter/filtered': 873701,
 'file_count': 212541,
 'file_status_count/downloaded': 212541,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2018, 8, 23, 11, 16, 25, 773075),
 'httperror/response_ignored_count': 1,
 'httperror/response_ignored_status_count/404': 1,
 'item_scraped_count': 47927,
 'log_count/DEBUG': 538824,
 'log_count/INFO': 1737,
 'log_count/WARNING': 1,
 'memusage/max': 338391040,
 'memusage/startup': 69754880,
 'request_depth_max': 790,
 'response_received_count': 278217,
 'retry/count': 137,
 'retry/reason_count/502 Bad Gateway': 1,
 'retry/reason_count/twisted.internet.error.TimeoutError': 135,
 'retry/reason_count/twisted.web._newclient.ResponseFailed': 1,
 'scheduler/dequeued': 65689,
 'scheduler/dequeued/disk': 65689,
 'scheduler/enqueued': 48810,
 'scheduler/enqueued/disk': 48810,
 'start_time': datetime.datetime(2018, 8, 22, 6, 28, 57, 752216)}
"""


class MeiTuLuSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'meitulu_spider'
    allowed_domains = ['meitulu.com']
    start_urls = ['https://www.meitulu.com/']
    HOST = 'https://www.meitulu.com'

    def parse(self, response):

        # 图集分类
        category = response.xpath('//ul[@id="tag_ul"]/li/a')
        for item in category:
            item_name = item.xpath('./text()').extract_first()
            item_url = item.xpath('./@href').extract_first()
            if self.HOST not in item_url:
                item_url = self.HOST + item_url
            yield scrapy.Request(url=item_url, callback=self.parse_category,
                                 meta={'category': item_name}, headers=get_headers())

        category = response.xpath('//ul[@class="menu"]/li/a')
        for item in category:
            item_name = item.xpath('./text()').extract_first()
            item_url = item.xpath('./@href').extract_first()
            if self.HOST not in item_url:
                item_url = self.HOST + item_url
            yield scrapy.Request(url=item_url, callback=self.parse_category,
                                 meta={'category': item_name}, headers=get_headers())

    def parse_category(self, response):
        urls = response.xpath('//ul[@class="img"]/li/a/@href').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_album,
                                 meta={'category': response.meta['category']}, headers=get_headers())

        # 多页
        other_pages = response.xpath('//div[@id="pages"]/a/@href').extract()
        for other_page in other_pages:
            if self.HOST not in other_page:
                other_page = self.HOST + other_page
            yield scrapy.Request(url=other_page, callback=self.parse_category,
                                 meta={'category': response.meta['category']}, headers=get_headers())

    def parse_album(self, response):
        image_detail_urls = response.xpath('//div[@class="content"]/center/img/@src').extract()
        if image_detail_urls and len(image_detail_urls) > 0:
            item = MyItem()
            item['referer'] = response.request.url
            item['image_urls'] = image_detail_urls
            item['save_sub_dir'] = response.meta['category']
            yield item
        # 多页
        other_pages = response.xpath('//div[@id="pages"]/a/@href').extract()
        for other_page in other_pages:
            if self.HOST not in other_page:
                other_page = self.HOST + other_page
            yield scrapy.Request(url=other_page, callback=self.parse_album,
                                 meta={'category': response.meta['category']}, headers=get_headers())
