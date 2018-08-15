# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PornhubItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class MyItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    # 文件保存的子文件（在 IMAGES_STORE 指定下的子文件中）
    save_sub_dir = scrapy.Field()
