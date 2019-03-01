# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 电影
class MovieItem(scrapy.Item):
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


# 评论信息
class CommentItem(scrapy.Item):
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
    # 评论类型
    comment_type = scrapy.Field()
