import json
import logging
import os
import re

import requests
import scrapy

from ..libs.db import DbMonitor
from ..libs.common import init_log
from ..items import MovieItem, CommentItem

# 电影分类
TAGS = ["热门", "最新", "经典", "可播放", "豆瓣高分", "冷门佳片", "华语", "欧美", "韩国", "日本", "动作", "喜剧", "爱情", "科幻", "悬疑", "恐怖", "治愈"]
# TAGS = ['热门']
# 电影列表链接
MOVIE_LIST_URL = 'https://movie.douban.com/j/search_subjects?type=movie&tag=%s&sort=recommend&page_limit=%s&page_start=%s'
# 电影评论链接，%s 为电影 id，limit 固定为20（不是20系统默认也会返回20） ?start=%s&limit=20&sort=new_score&status=P'
COMMENT_URL = 'https://movie.douban.com/subject/%s/comments'
# 登录地址
LOGIN_URL = 'https://accounts.douban.com/j/mobile/login/basic'


class MovieSpider(scrapy.Spider):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG,
             logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR,
             logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    name = 'movie_spider'
    allowed_domains = ['douban.com']
    start_urls = ['']
    HOST = 'https://movie.douban.com'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.cookies = self.get_login_cookies()
        self.db = DbMonitor()

    # 登录豆瓣
    @staticmethod
    def get_login_cookies():
        headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
            'host': 'accounts.douban.com', 'Referer': 'https://accounts.douban.com/passport/login_popup?login_source=anony'}
        data = {'name': '13257788084', 'password': 'db', 'remember': False}
        response = requests.post(url=LOGIN_URL, data=data, headers=headers)
        return response.cookies

    def start_requests(self):
        for tag in TAGS:
            url = MOVIE_LIST_URL % (tag, 500, 0)
            yield scrapy.Request(url=url, callback=self.parse)

    # 解析热门电影列表
    def parse(self, response):
        result = response.text
        result = json.loads(result, encoding='utf-8')
        for item in result['subjects']:
            movie = MovieItem()
            movie['id'] = item['id']
            movie['title'] = item['title']
            movie['url'] = item['url']
            movie['rate'] = item['rate']
            # yield scrapy.Request(url=movie.url, callback=self.parse_detail_page, meta={'movie': movie})

            comment_counts = self.db.count_match_movie_comments(movie=movie)
            # 小于 221 说明只爬过不受限内容，登录后也只是能爬500条
            if comment_counts < 500:
                yield scrapy.Request(url=COMMENT_URL % movie['id'], callback=self.parse_comment_page, meta={'movie': movie})

    # 解析电影详情页
    def parse_detail_page(self, response):
        movie = response.meta['movie']
        rating_people = response.xpath('//*[@class="rating_people"]/span/text()')
        rating_num = response.xpath('//*[contains(@class,"rating_num")]/text()')
        movie_infos = response.xpath('//*[@id="info"]/span')
        movie_info_dict = {}
        movie_types = []
        for movie_info in movie_infos:
            info_type = movie_info.xpath('./span/text()').extract_first()
            if info_type in ['导演', '编剧', '主演']:
                info_detail = movie_info.xpath('./span/a/text()').extract()
                movie_info_dict[info_type] = info_detail
            if movie_info.xpath('./@property').extract_first() == 'v:genre':
                movie_types.append(movie_info.xpath('./text()').extract_first())
        movie_info_dict['类型'] = movie_types

    # 解析电影短评页
    def parse_comment_page(self, response):
        # result = response.text
        movie = response.meta['movie']
        comments = response.xpath('//*[contains(@class,"comment-item")]')
        for comment in comments:
            comment_item = CommentItem()
            comment_id = comment.xpath('./@data-cid').extract_first()
            comment_user = comment.xpath('.//span[@class="comment-info"]/a/text()').extract_first()
            # 'allstar10 rating'
            maybe_ratings = comment.xpath(
                './div[contains(@class,"comment")]//span[@class="comment-info"]/span[contains(@class,"rating")]/@class').extract_first()
            rating = None
            # 可能有的评论没有评分（没看过的不打评分）
            if maybe_ratings:
                maybe_ratings = re.findall('allstar(\d+?)0', maybe_ratings, re.I)
                # allstar10 1*  allstar20 2* allstar40 4*
                rating = maybe_ratings[0] if len(maybe_ratings) > 0 else None
            rating_time = comment.xpath(
                './div[contains(@class,"comment")]//span[contains(@class, "comment-time")]/@title').extract_first()
            comment_content = comment.xpath(
                './div[contains(@class,"comment")]//span[contains(@class, "short")]/text()').extract_first()
            comment_item['comment_id'] = comment_id
            comment_item['movie_title'] = movie['title']
            comment_item['movie_id'] = movie['id']
            comment_item['user'] = comment_user
            comment_item['rating'] = rating
            comment_item['rating_time'] = rating_time
            comment_item['content'] = comment_content
            yield comment_item
        next_url = response.xpath('//*[@id="paginator"]/a[@class="next"]/@href').extract_first()
        if next_url:
            yield scrapy.Request(url=COMMENT_URL % movie['id'] + next_url, callback=self.parse_comment_page,
                                 meta={'movie': movie})
