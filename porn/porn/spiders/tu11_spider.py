"""
百度搜索 beauty leg
http://www.tu11.com/
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

"""

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
