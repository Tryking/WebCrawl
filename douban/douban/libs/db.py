import pymongo
from scrapy.conf import settings


class DbMonitor:
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

    def count_match_movie_comments(self, movie):
        """
        获取特定电影的已存评论数
        # 评论 id
        comment_id = scrapy.Field()
        # 电影名
        movie_title = scrapy.Field()
        # 电影 id
        movie_id = scrapy.Field()
        """
        return self.db['movie_comment'].count(filter={'movie_title': movie['title'], 'movie_id': movie['id']})
