"""
百度搜索 明星写真
http://www.mingxing.com/tuku
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

"""


"""
TYPES = ['mxxz.html', 'shz.html', 'hdxz.html', '']
BASE_URL = 'http://www.mingxing.com/tuku/index/type/%s'


class MingxingSpider(scrapy.Spider):
    # if not os.path.exists('logs'):
    #     os.mkdir('logs')
    # init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    # init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'mingxing_spider'
    allowed_domains = ['mingxing.com']
    start_urls = ['http://www.mingxing.com/tuku']
    HOST = 'http://www.mingxing.com'

    def start_requests(self):
        for _type in TYPES:
            url = BASE_URL % _type
            yield scrapy.Request(url=url, meta={}, callback=self.parse, headers=get_headers())

    def parse(self, response):
        _type = response.xpath('//a[@class="on"]/text()').extract_first()
        items = response.xpath('//div[@class="inn"]/ul/li')
        for item in items:
            title = item.xpath('./a/@title').extract_first()
            url = item.xpath('./a/@href').extract_first()
            if self.HOST not in url:
                url = self.HOST + url
            yield scrapy.Request(url=url, meta={'_type': _type, 'title': title}, callback=self.parse_album, headers=get_headers())
        # 多页
        other_pages = response.xpath('//div[@class="pages"]//a/@href').extract()
        for other_page in other_pages:
            if self.HOST not in other_page:
                other_page = self.HOST + other_page
            yield scrapy.Request(url=other_page, callback=self.parse, headers=get_headers())

    def parse_album(self, response):
        image_detail_urls = response.xpath(
            '//div[contains(@class,"stills_big")]/div[@class="swiper-wrapper"]/div[contains(@class,swiper-slide)]/div/img/@src').extract()
        if image_detail_urls and len(image_detail_urls) > 0:
            image_urls = list()
            for image_url in image_detail_urls:
                # if self.HOST not in image_url:
                #     image_url = self.HOST + image_url
                image_urls.append(image_url)
            item = MyItem()
            save_sub_dir = os.path.join(response.meta['_type'], get_standard_file_name(response.meta['title']))
            item['referer'] = response.request.url
            item['image_urls'] = image_urls
            item['save_sub_dir'] = save_sub_dir
            yield item
