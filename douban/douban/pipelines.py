# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

from scrapy.conf import settings
from .libs.common import get_update_time, get_before_date
from .items import MovieItem, CommentItem


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
        if isinstance(item, MovieItem):
            """
            # 电影名
            title = scrapy.Field()
            # 电影 id
            id = scrapy.Field()
            # 电影详情页
            url = scrapy.Field()
            # 电影评分
            rate = scrapy.Field()
            # 电影导演
            directors = scrapy.Field()
            # 电影编剧
            writers = scrapy.Field()
            # 电影主演
            actors = scrapy.Field()
            # 电影类型
            movie_types = scrapy.Field()
            # 评论人数
            rating_people = scrapy.Field()
            # 评论个数
            rating_num = scrapy.Field()
            """
            self.db['movie'].update_one(
                filter={'movie_title': item['title'], 'movie_id': item['id']},
                update={'$set': {'url': item['url'], 'rate': item['rate'], 'directors': item['directors'],
                                 'writers': item['writers'], 'actors': item['actors'], 'movie_types': item['movie_types'],
                                 'rating_people': item['rating_people'], 'rating_num': item['rating_num'],
                                 'update_time': get_update_time(), 'update_date': get_before_date(before_day=0)}},
                upsert=True)
        elif isinstance(item, CommentItem):
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
                update={'$set': {'user': item['user'], 'rating': item['rating'], 'content': item['content'], 'rating_time': item['rating_time'],
                                 'comment_type': item['comment_type'], 'update_time': get_update_time(),
                                 'update_date': get_before_date(before_day=0)}},
                upsert=True)
        return item
