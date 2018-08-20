"""
https://hentaifox.com/
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

"""
2018年08月19日07:44:41

爬取49601个项目(有9.7w张图片)，程序卡死。
"""


class HentaifoxSpider(scrapy.Spider):
    # if not os.path.exists('logs'):
    #     os.mkdir('logs')
    # init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    # init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'hentaifox_spider'
    allowed_domains = ['hentaifox.com']
    start_urls = ['https://hentaifox.com/']
    HOST = 'https://hentaifox.com'

    def parse(self, response):
        urls = response.xpath('//div[contains(@class,"item")]/a/@href').extract()
        for url in urls:
            url = self.HOST + url
            yield scrapy.Request(url=url, callback=self.parse_album, meta={'proxy': get_proxy()}, headers=get_headers())
        # 多页
        other_pages = response.xpath('//div[contains(@class,"pagination")]/a/@href').extract()
        for other_page in other_pages:
            other_page = 'https:' + other_page
            yield scrapy.Request(url=other_page, callback=self.parse, meta={'proxy': get_proxy()}, headers=get_headers())

    def parse_album(self, response):
        # save_sub_dir = response.xpath('//*[@id="content"]//div[@class="info"]/h1/text()').extract_first()
        image_detail_urls = response.xpath('//div[@class="gallery"]/div/a/img/@src').extract()
        if not image_detail_urls:
            image_detail_urls = response.xpath('//div[@class="gallery"]/div/a/img/@data-src').extract()
        # if not save_sub_dir:
        #     save_sub_dir = 'default'
        # save_sub_dir = get_standard_file_name(save_sub_dir)
        if image_detail_urls and len(image_detail_urls) > 0:
            image_urls = list()
            for image_url in image_detail_urls:
                if 'https' not in image_url:
                    image_url = 'https:' + image_url
                # 把 t 去掉，图片比较高清
                image_url = image_url.replace('t.jpg', '.jpg')
                image_urls.append(image_url)
            item = MyItem()
            item['referer'] = response.request.url
            item['image_urls'] = image_urls
            # item['save_sub_dir'] = save_sub_dir
            yield item
