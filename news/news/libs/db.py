"""
数据库操作
"""
import pymongo

from ..settings import *


class DbMonitor:
    def __init__(self):
        host = MONGODB_HOST
        port = MONGODB_PORT
        user = MONGODB_USER
        pwd = MONGODB_PWD
        db_name = MONGODB_DBNAME

        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client[db_name]
        if user and user != '':
            self.db.authenticate(name=user, password=pwd)

    def match_article(self, name, author, title):
        """
        查找库中是否有匹配的文章记录
        """
        record = self.db[name].find_one(filter={'article_author': author, 'article_title': title})
        if record:
            return True
        else:
            return False
