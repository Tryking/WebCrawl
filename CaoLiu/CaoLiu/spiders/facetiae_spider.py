"""
草榴社区 > 成人文学交流区
"""
import os
import re

import scrapy
from libs.common import *

SAVE_DIR = 'datas'


class FacetiaeSpider(scrapy.Spider):
    name = "facetiae_spider"
    host = "http://t66y.com"

    def start_requests(self):
        urls = [
            'http://www.t66y.com/thread0806.php?fid=20'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.handle_failure)

    def parse(self, response):
        urls = response.xpath('//*[contains(@class, "tr3 t_one")]//h3//@href').extract()
        for url in urls[:]:
            if 'htm_data' not in url:
                urls.remove(url)
                continue
            yield scrapy.Request(self.host + '/' + url, callback=self.parse_post, dont_filter=True)
        # 获取目录列表的下一页，添加到请求中
        next_pages = response.xpath('//*[contains(text(), "下一頁")]/@href').extract()
        if len(next_pages) >= 1:
            yield scrapy.Request(self.host + '/' + next_pages[0], callback=self.parse, errback=self.handle_failure, dont_filter=True)

    def parse_post(self, response):
        if not os.path.exists(SAVE_DIR):
            os.mkdir(SAVE_DIR)
        title = response.xpath('//*[@class="tr1 do_not_catch"]//h4/text()').extract_first()
        if not title:
            title = response.xpath('//*[@id="main"]/form/div[@class="t"]/table')
            title = title.xpath('string(.)').extract_first().strip()
        content = response.xpath('//div[@class="tpc_content do_not_catch"]').extract()
        ptime = response.xpath('(//*[@class="tr1"])[1]//*[@class="tipad"]//text()').extract()
        ptime = ''.join(ptime)
        if ptime:
            ptime = re.findall(r'(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2})', ptime)
        content = '\n'.join(content)
        if ptime:
            ptime = ptime[0]
        if title:
            file_name = SAVE_DIR + os.path.sep + get_standard_file_name(title)
        else:
            file_name = SAVE_DIR + os.path.sep + get_random_str(10)
        with open(file_name, mode='a+', encoding='utf-8') as f:
            f.write(content)
        # 获取帖子的下一页继续（有的帖子后面的也是文章）
        next_page_url = response.xpath('//*[contains(text(), "下一頁")]/@href').extract_first()
        if next_page_url:
            next_page_url = next_page_url.replace('../../../', '')
            self.logger.debug('下一页：%s' % next_page_url)
            yield scrapy.Request(self.host + '/' + next_page_url, callback=self.parse_post, errback=self.handle_failure,
                                 dont_filter=True)

    def handle_failure(self, failure):
        url = failure.request.url
        if 'page' in url:
            yield scrapy.Request(url, callback=self.parse, errback=self.handle_failure, dont_filter=True)
        else:
            yield scrapy.Request(url, callback=self.parse_post, errback=self.handle_failure, dont_filter=True)
