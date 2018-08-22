"""
百度搜索 beauty leg
http://www.tgirl.cc/
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

"""
"""


class TGirlSpider(scrapy.Spider):
    # if not os.path.exists('logs'):
    #     os.mkdir('logs')
    # init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    # init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'tgirl_spider'
    allowed_domains = ['tgirl.cc']
    start_urls = ['http://www.tgirl.cc/']
    HOST = 'http://www.tgirl.cc'

    def parse(self, response):
        category = response.xpath('//div[@class="topnav"]/ul[@class="menu"]/li/a')
        for item in category:
            item_name = item.xpath('./text()').extract_first()
            item_url = item.xpath('./@href').extract_first()
            if self.HOST not in item_url:
                item_url = self.HOST + item_url
            yield scrapy.Request(url=item_url, callback=self.parse_category,
                                 meta={'category': item_name}, headers=get_headers())

    def parse_category(self, response):
        urls = response.xpath('//ul[@id="post_container"]/li/div/a/@href').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_album,
                                 meta={'category': response.meta['category']}, headers=get_headers())

        # 多页
        other_pages = response.xpath('//div[@class="pagination"]/a/@href').extract()
        for other_page in other_pages:
            yield scrapy.Request(url=other_page, callback=self.parse_category,
                                 meta={'category': response.meta['category']}, headers=get_headers())

    def parse_album(self, response):
        image_detail_urls = response.xpath('//div[@id="post_content"]/p/img/@src').extract()
        if image_detail_urls and len(image_detail_urls) > 0:
            item = MyItem()
            item['referer'] = response.request.url
            item['image_urls'] = image_detail_urls
            item['save_sub_dir'] = response.meta['category']
            yield item
