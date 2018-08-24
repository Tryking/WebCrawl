"""
数据库需要创建的索引
"""

# sogo_wechat_article
"""
# 一个微信号一个文章唯一，插入前查找时速度快
db.getCollection('sogo_wechat_article').createIndex({'wechat_id':1,'article_title': 1},{unique:true})
"""

# jinritoutiao_article
"""
# 一个来源一个文章唯一，插入前查找时速度快
db.getCollection('jinritoutiao_article').createIndex({'source':1,'article_title': 1},{unique:true})
"""
