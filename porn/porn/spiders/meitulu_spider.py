"""
百度搜索 beauty leg
https://www.meitulu.com/
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

"""
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
            yield scrapy.Request(url=other_page, callback=self.parse_category,
                                 meta={'category': response.meta['category']}, headers=get_headers())
