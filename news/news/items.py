# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # 新闻名称
    name = scrapy.Field()
    # 新闻类型
    article_type = scrapy.Field()
    # 新闻标题
    article_title = scrapy.Field()
    # 新闻作者
    article_author = scrapy.Field()
    # 新闻内容
    article_content = scrapy.Field()
