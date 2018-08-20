"""
百度搜索 beauty leg
http://www.beautylegmm.com/
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

"""

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
