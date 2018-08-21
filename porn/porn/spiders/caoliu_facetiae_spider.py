"""
草榴社区 > 成人文学交流区
"""
import os
import re

import scrapy
from ..libs.common import *

SAVE_DIR = 'datas'
# 这些帖子虽然满足条件，但是不获取
DONOT_FETCH_POST = ['■■■ 來訪者必看的內容 - 使你更快速上手 <隨時更新> ■■■',
                    '文區版規 / 文區督查貼(2014.01.17更新)', '关于论坛的搜索功能',
                    '发帖前必读', '文学区违规举报专贴-----置頂版規有新更新（藍色）']


class FacetiaeSpider(scrapy.Spider):
    # if not os.path.exists('logs'):
    #     os.mkdir('logs')
    # init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + 'facetiae_spider' + ".log")
    # init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + 'facetiae_spider' + "_error.log")
    name = "caoliu_facetiae_spider"
    host = "http://t66y.com"

    def start_requests(self):
        urls = [
            'http://www.t66y.com/thread0806.php?fid=20'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.handle_failure)

    def parse(self, response):
        titles = response.xpath('//*[contains(@class, "tr3 t_one")]//h3')
        for title in titles:
            text = title.xpath('.//text()').extract_first()
            url = title.xpath('.//@href').extract_first()
            if not url or 'htm_data' not in url or text in DONOT_FETCH_POST:
                continue
            else:
                yield scrapy.Request(self.host + '/' + url, meta={'title': text, 'page': 1}, callback=self.parse_post, dont_filter=True)
        # 获取目录列表的下一页，添加到请求中
        next_pages = response.xpath('//*[contains(text(), "下一頁")]/@href').extract()
        if len(next_pages) >= 1:
            yield scrapy.Request(self.host + '/' + next_pages[0], callback=self.parse, errback=self.handle_failure, dont_filter=True)

    def parse_post(self, response):
        title = response.meta['title']
        page = response.meta['page']
        if not os.path.exists(SAVE_DIR):
            os.mkdir(SAVE_DIR)
        if not title:
            title = response.xpath('//*[@class="tr1 do_not_catch"]//h4/text()').extract_first()
        if not title:
            title = response.xpath('//*[@id="main"]/form/div[@class="t"]/table')
            title = title.xpath('string(.)').extract_first().strip()
        self.debug('title: %s, page: %s' % (str(title), str(page)))
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
            self.debug('下一页：%s' % next_page_url)
            yield scrapy.Request(self.host + '/' + next_page_url, meta={'title': title, 'page': page + 1}, callback=self.parse_post,
                                 errback=self.handle_failure,
                                 dont_filter=True)

    def handle_failure(self, failure):
        url = failure.request.url

    @staticmethod
    def write_file_log(msg, level='error'):
        filename = os.path.split(__file__)[1]
        if level == 'debug':
            logging.getLogger().debug('File:' + filename + ': ' + msg)
        elif level == 'warning':
            logging.getLogger().warning('File:' + filename + ': ' + msg)
        else:
            logging.getLogger().error('File:' + filename + ': ' + msg)

    # 调试日志
    def debug(self, msg):
        self.write_file_log(msg, 'debug')

    # 错误日志
    def error(self, msg):
        self.write_file_log(msg, 'error')
