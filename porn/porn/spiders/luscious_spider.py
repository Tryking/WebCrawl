"""
https://luscious.net/
"""
import scrapy

from ..items import MyItem
from ..libs.common import *


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
