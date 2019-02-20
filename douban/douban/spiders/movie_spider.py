import json
import re

import scrapy

from ..items import MovieItem, CommentItem

# 电影列表链接
MOVIE_LIST_URL = 'https://movie.douban.com/j/search_subjects?type=movie&tag=热门&sort=recommend&page_limit=%s&page_start=%s'
# 电影评论链接，%s 为电影 id，limit 固定为20（不是20系统默认也会返回20） ?start=%s&limit=20&sort=new_score&status=P'
COMMENT_URL = 'https://movie.douban.com/subject/%s/comments'


class MovieSpider(scrapy.Spider):
    name = 'movie_spider'
    allowed_domains = ['douban.com']
    start_urls = ['']
    HOST = 'https://movie.douban.com'

    def start_requests(self):
        url = MOVIE_LIST_URL % (100, 0)
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
            yield scrapy.Request(url=COMMENT_URL % movie['id'], callback=self.parse_comment_page, meta={'movie': movie})

    # 解析电影详情页
    def parse_detail_page(self, response):
        result = response.text
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
            comment_user = comment.xpath('.//span[@class="comment-info"]/a/text()')
            # 'allstar10 rating'
            maybe_ratings = comment.xpath(
                './div[contains(@class,"comment")]//span[@class="comment-info"]/span[contains(@class,"rating")]/@class').extract_first()
            rating = None
            # 可能有的评论没有评分（没看过的不打评分）
            if maybe_ratings:
                maybe_ratings = re.findall('allstar(\d+?)0', maybe_ratings, re.I)
                # allstar10 1*  allstar20 2* allstar40 4*
                rating = maybe_ratings[0] if len(maybe_ratings) > 0 else None
            rating_time = comment.xpath('./div[contains(@class,"comment")]//span[contains(@class, "comment-time")]/@title').extract_first()
            comment_content = comment.xpath('./div[contains(@class,"comment")]//span[contains(@class, "short")]/text()').extract_first()
            comment_item['movie_title'] = movie['title']
            comment_item['movie_id'] = movie['id']
            comment_item['user'] = comment_user
            comment_item['rating'] = rating
            comment_item['rating_time'] = rating_time
            comment_item['content'] = comment_content
        next_url = response.xpath('//*[@id="paginator"]/a[@class="next"]/@href').extract_first()
        if next_url:
            yield scrapy.Request(url=COMMENT_URL % movie['id'] + next_url, callback=self.parse_comment_page, meta={'movie': movie})
