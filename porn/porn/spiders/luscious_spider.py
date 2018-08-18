"""
https://luscious.net/
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

"""
{'downloader/exception_count': 2198,
 'downloader/exception_type_count/twisted.internet.error.TimeoutError': 1748,
 'downloader/exception_type_count/twisted.web._newclient.ResponseFailed': 1,
 'downloader/exception_type_count/twisted.web._newclient.ResponseNeverReceived': 449,
 'downloader/request_bytes': 28346569,
 'downloader/request_count': 60877,
 'downloader/request_method_count/GET': 60877,
 'downloader/response_bytes': 6832528352,
 'downloader/response_count': 58679,
 'downloader/response_status_count/200': 58651,
 'downloader/response_status_count/404': 4,
 'downloader/response_status_count/504': 24,
 'dupefilter/filtered': 388,
 'file_count': 28246,
 'file_status_count/downloaded': 28243,
 'file_status_count/uptodate': 3,
 'finish_reason': 'shutdown',
 'finish_time': datetime.datetime(2018, 8, 18, 23, 27, 16, 587532),
 'item_scraped_count': 28431,
 'log_count/DEBUG': 129715,
 'log_count/ERROR': 10,
 'log_count/INFO': 1179,
 'log_count/WARNING': 186,
 'memusage/max': 291438592,
 'memusage/startup': 95256576,
 'request_depth_max': 11,
 'response_received_count': 58655,
 'retry/count': 2041,
 'retry/max_reached': 181,
 'retry/reason_count/504 Gateway Time-out': 24,
 'retry/reason_count/twisted.internet.error.TimeoutError': 1573,
 'retry/reason_count/twisted.web._newclient.ResponseFailed': 1,
 'retry/reason_count/twisted.web._newclient.ResponseNeverReceived': 443,
 'scheduler/dequeued': 30656,
 'scheduler/dequeued/disk': 30656,
 'scheduler/enqueued': 30895,
 'scheduler/enqueued/disk': 30895,
 'start_time': datetime.datetime(2018, 8, 18, 8, 3, 53, 671866)}
"""


class LusciousSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'luscious_spider'
    allowed_domains = ['luscious.net']
    start_urls = ['https://luscious.net/c/futanari/']
    HOST = 'https://luscious.net'

    def parse(self, response):
        urls = response.xpath('//ul[contains(@class,"album_page")]/li//div[@class="item_cover"]/a/@href').extract()
        for url in urls:
            url = self.HOST + url
            yield scrapy.Request(url=url, callback=self.parse_album, meta={'proxy': get_proxy()}, headers=get_headers())
        # 多页
        other_pages = response.xpath('//div[@class="pagination-wrapper"]/ol/li/a/@href').extract()
        for other_page in other_pages:
            if self.HOST not in other_page:
                other_page = self.HOST + other_page
            yield scrapy.Request(url=other_page, callback=self.parse, meta={'proxy': get_proxy()}, headers=get_headers())

    def parse_album(self, response):
        save_sub_dir = response.xpath('//article[@class="content_box"]/ul/li/h2/text()').extract_first()
        image_detail_urls = response.xpath('//div[@id="thumbs_wrapper"]//div[contains(@class,"item")]/a/@href').extract()
        if image_detail_urls and len(image_detail_urls) > 0:
            if not save_sub_dir:
                save_sub_dir = 'default'
            save_sub_dir = get_standard_file_name(save_sub_dir)
            for image_detail_url in image_detail_urls:
                if self.HOST not in image_detail_url:
                    image_detail_url = self.HOST + image_detail_url
                yield scrapy.Request(url=image_detail_url, callback=self.parse_image,
                                     meta={'proxy': get_proxy(), 'save_sub_dir': save_sub_dir}, headers=get_headers())

    def parse_image(self, response):
        save_sub_dir = response.meta['save_sub_dir']
        img_url = response.xpath('//div[@class="single_image"]/div/a/img/@src').extract_first()
        if img_url:
            image_urls = list()
            image_urls.append(img_url)
            item = MyItem()
            item['referer'] = response.request.url
            item['image_urls'] = image_urls
            item['save_sub_dir'] = save_sub_dir
            yield item
