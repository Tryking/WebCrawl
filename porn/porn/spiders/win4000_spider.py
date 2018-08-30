"""
百度搜索 明星写真
http://www.win4000.com/
"""
import scrapy

from ..items import MyItem
from ..libs.common import *

"""


"""


class MingxingSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'win4000_spider'
    allowed_domains = ['win4000.com']
    start_urls = ['http://www.win4000.com/mt/starlst_0_2_1.html']
    HOST = 'http://www.win4000.com'

    def parse(self, response):
        items = response.xpath('//div[@class="Left_bar"]/div[contains(@class,"list_cont")]/div[@class="tab_tj"]//ul/li/a')
        for item in items:
            title = item.xpath('./p/text()').extract_first()
            url = item.xpath('./@href').extract_first()
            if self.HOST not in url:
                url = self.HOST + url
            yield scrapy.Request(url=url, meta={'person': title}, callback=self.parse_person, headers=get_headers())
        # 多页
        other_pages = response.xpath('//div[@class="Left_bar"]/div[contains(@class,"pages")]/div/a/@href').extract()
        for other_page in other_pages:
            if self.HOST not in other_page:
                other_page = self.HOST + other_page
            yield scrapy.Request(url=other_page, callback=self.parse, headers=get_headers())

    def parse_person(self, response):
        items = response.xpath('//div[@class="Left_bar"]//div[@class="tab_box"]//ul/li/a/@href').extract()
        for item in items:
            if self.HOST not in item:
                item = self.HOST + item
            yield scrapy.Request(url=item, meta={'person': response.meta['person']}, callback=self.parse_album, headers=get_headers())

    def parse_album(self, response):
        image_detail_urls = response.xpath('//ul[@id="scroll"]/li/a/img/@src').extract()
        if image_detail_urls and len(image_detail_urls) > 0:
            image_urls = list()
            # todo：这里返回的是静态无法查看图片，使用代理也是，待解决
            for image_url in image_detail_urls:
                if 'win4000' not in image_url:
                    image_url = self.HOST + image_url
                image_url = image_url.replace('_130_170', '')
                image_urls.append(image_url)
            item = MyItem()
            save_sub_dir = get_standard_file_name(response.meta['person'])
            item['referer'] = response.request.url
            item['image_urls'] = image_urls
            item['save_sub_dir'] = save_sub_dir
            yield item
