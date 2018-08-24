# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

from scrapy.conf import settings
from .libs.common import get_udpate_time, get_before_date


class NewsPipeline(object):
    def __init__(self):
        host = settings["MONGODB_HOST"]
        port = settings["MONGODB_PORT"]
        user = settings["MONGODB_USER"]
        pwd = settings["MONGODB_PWD"]
        db_name = settings["MONGODB_DBNAME"]

        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client[db_name]
        if user and user != '':
            self.db.authenticate(name=user, password=pwd)

    def process_item(self, item, spider):
        """
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
        """
        if item['name'] == 'news_kr30':
            self.db['news_kr30'].update_one(filter={'article_title': item['article_title'], 'article_author': item['article_author']},
                                            update={'$set': {'article_content': item['article_content'], 'article_type': item['article_type'],
                                                             'update_time': get_udpate_time(), 'update_date': get_before_date(before_day=0)}},
                                            upsert=True)

        return item
