# -*- coding: utf-8 -*-
"""
http://www.zzcartoon.com
"""
import scrapy
from ..items import MyItem
from ..libs.common import *


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
