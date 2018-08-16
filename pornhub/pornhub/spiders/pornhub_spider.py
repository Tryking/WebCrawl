# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver

from items import MyItem
from libs.common import *

# 初始获取资源URL （https://www.pornhub.com/albums/straight?search=female）
BASE_URL = 'https://www.pornhub.com/albums/%s?search=%s'
# 模型 misc-miscellaneous（混杂的）
SEGMENTS = ['female', 'straight', 'male', 'gay', 'transgender', 'misc', 'uncategorized']
# 分类
TAGS = ['Tits', 'Ass', 'Pussy', 'Amateur', 'Dick', 'Hot', 'Teen', 'Hentai', 'Sex', 'Boobs', 'Babe', 'Cum', 'Blonde', 'Blowjob', 'Anal', 'Black',
        'Brunette', 'Asian', 'MILF', 'Cumshot', 'Pornstar', 'Hardcore', 'Celebrity', 'Lesbian', 'Ebony', 'Fetish', 'BBW', 'Masturbation',
        'Facial', 'Tribute', 'BDSM']


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
        # browser.get(url=url)
        # time.sleep(10)
        # urls = browser.find_elements_by_xpath('//li[contains(@class,"photoAlbumListContainer")]/div/a')
        # for url in urls:
        #     url = url.get_attribute('href')
        #     yield scrapy.Request(url=url, callback=self.parse, meta={'proxy': '127.0.0.1:1087'})

        for segment in SEGMENTS:
            for tag in TAGS:
                url = BASE_URL % (segment, tag.lower())
                yield scrapy.Request(url=url, callback=self.parse, meta={'proxy': get_proxy(), 'save_sub_dir': segment + '-' + tag.lower()})

    def parse(self, response):
        save_sub_dir = response.meta['save_sub_dir']
        urls = response.xpath('//li[contains(@class,"photoAlbumListContainer")]/div/a/@href').extract()
        for url in urls:
            url = self.HOST + url
            yield scrapy.Request(url=url, callback=self.parse_album, meta={'proxy': get_proxy(), 'save_sub_dir': save_sub_dir}, dont_filter=True)
        # 下一页
        next_page_url = response.xpath(
            '//div[contains(@class,"container")]//li[contains(@class,"page_next")]/a[contains(@class,"orangeButton")]/@href').extract_first()
        if next_page_url:
            next_url = self.HOST + next_page_url
            yield scrapy.Request(url=next_url, callback=self.parse, meta={'proxy': get_proxy(), 'save_sub_dir': save_sub_dir}, dont_filter=True)

    def parse_album(self, response):
        # 这个获取的直接就是图片的链接，但是质量比较低
        # image_hrefs = response.xpath('//li[contains(@class,"photoAlbumListContainer")]/div/@data-bkg').extract()
        # urls = list()
        # for url in image_hrefs:
        #     # TODO 把括号移除，这样下载的才是原图（移除括号后下载不了，可能是服务器做了限制）
        #     #  https://dl.phncdn.com/pics/albums/006/542/202/102689682/(m=bKaz0Np)(mh=waVqbkwB3QiO7vdV)original_102689682.jpg
        #     # url = remove_bracket(url)
        #     urls.append(url)
        # item = MyItem()
        # item['referer'] = response.request.url
        # item['image_urls'] = urls
        # item['save_sub_dir'] = 'straight'
        # yield item

        save_sub_dir = response.meta['save_sub_dir']

        # 这个获取逇是图片的详情页面，在这里面再获取图片的比较高清的图
        image_detail_urls = response.xpath('//li[contains(@class,"photoAlbumListContainer")]/div/a/@href').extract()
        for url in image_detail_urls:
            url = self.HOST + url
            yield scrapy.Request(url=url, callback=self.parse_image_detail, meta={'proxy': get_proxy(), 'save_sub_dir': save_sub_dir},
                                 dont_filter=True)

        # 下一页
        next_page_url = response.xpath(
            '//div[contains(@class,"container")]//li[contains(@class,"page_next")]/a[contains(@class,"orangeButton")]/@href').extract_first()
        if next_page_url:
            next_url = self.HOST + next_page_url
            yield scrapy.Request(url=next_url, callback=self.parse_album, meta={'proxy': get_proxy(), 'save_sub_dir': save_sub_dir}, dont_filter=True)

    def parse_image_detail(self, response):
        save_sub_dir = response.meta['save_sub_dir']
        # 实际上只有一个，这里为了使用image_urls
        image_urls = response.xpath('//*[@id="photoImageSection"]/div[contains(@class,"centerImage")]//img/@src').extract()
        if image_urls and len(image_urls) > 0:
            item = MyItem()
            item['referer'] = response.request.url
            item['image_urls'] = image_urls
            item['save_sub_dir'] = save_sub_dir
            yield item
