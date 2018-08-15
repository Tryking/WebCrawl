# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver

from items import MyItem
from libs.common import *


class PornhubSpiderSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + 'facetiae_spider' + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + 'facetiae_spider' + "_error.log")

    name = 'pornhub_spider'
    allowed_domains = ['https://www.pornhub.com/']
    start_urls = ['https://www.pornhub.com/']
    HOST = 'https://www.pornhub.com'

    def start_requests(self):
        # chrome_options = webdriver.ChromeOptions()
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", prefs)
        # browser = webdriver.Chrome(chrome_options=chrome_options)
        #
        # # 最大化页面，防止有的内容无法点击
        # browser.maximize_window()
        url = 'https://www.pornhub.com/albums/straight'
        # browser.get(url=url)
        # time.sleep(10)
        # urls = browser.find_elements_by_xpath('//li[contains(@class,"photoAlbumListContainer")]/div/a')
        # for url in urls:
        #     url = url.get_attribute('href')
        #     yield scrapy.Request(url=url, callback=self.parse, meta={'proxy': '127.0.0.1:1087'})
        yield scrapy.Request(url=url, callback=self.parse_first, meta={'proxy': '127.0.0.1:1087'})

    def parse_first(self, response):
        urls = response.xpath('//li[contains(@class,"photoAlbumListContainer")]/div/a/@href').extract()
        for url in urls:
            url = self.HOST + url
            yield scrapy.Request(url=url, callback=self.parse, meta={'proxy': '127.0.0.1:1087'}, dont_filter=True)

    def parse(self, response):
        print(response.status)
        print('test')
        image_hrefs = response.xpath('//li[contains(@class,"photoAlbumListContainer")]/div/@data-bkg').extract()
        urls = list()
        for url in image_hrefs:
            # TODO 把括号移除，这样下载的才是原图
            #  https://dl.phncdn.com/pics/albums/006/542/202/102689682/(m=bKaz0Np)(mh=waVqbkwB3QiO7vdV)original_102689682.jpg
            urls.append(url)
        item = MyItem()
        item['image_urls'] = urls
        item['save_sub_dir'] = 'straight'
        yield item
