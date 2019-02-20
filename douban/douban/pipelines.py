# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

from scrapy.conf import settings
from .libs.common import get_update_time, get_before_date


class DoubanPipeline(object):
    def __init__(self):
        host = settings["MONGODB_HOST"]
        port = settings["MONGODB_PORT"]
        user = settings["MONGODB_USER"]
        pwd = settings["MONGODB_PWD"]
        db_name = settings["MONGODB_DB"]

        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client[db_name]
        if user and user != '':
            self.db.authenticate(name=user, password=pwd)

    def process_item(self, item, spider):
        """
        # 评论 id
        comment_id = scrapy.Field()
        # 电影名
        movie_title = scrapy.Field()
        # 电影 id
        movie_id = scrapy.Field()
        # 评论人
        user = scrapy.Field()
        # 评分
        rating = scrapy.Field()
        # 评价内容
        content = scrapy.Field()
        # 评价时间
        rating_time = scrapy.Field()
        """
        self.db['movie_comment'].update_one(
            filter={'movie_title': item['movie_title'], 'movie_id': item['movie_id'], 'comment_id': item['comment_id']},
            update={'$set': {'user': item['user'], 'rating': item['rating'],
                             'content': item['content'], 'rating_time': item['rating_time'],
                             'update_time': get_update_time(), 'update_date': get_before_date(before_day=0)}},
            upsert=True)
        return item
