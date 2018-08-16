# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import json

import requests
from scrapy import signals

from settings import PROXY_URL
from .libs.common import *


class PornhubSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


logger = logging.getLogger(__name__)


class PornhubDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self):
        # 更新IP最小间隔时长（5分钟）
        self.get_proxy_interval = 5 * 60
        self.proxy_url = PROXY_URL
        self.proxys = list()
        self.need_get_proxy_interval = False
        self.last_update_proxy = 0

    """ 换Cookie """
    cookie = {
        'platform': 'pc',
        'ss': '643809513213537437',
        'bs': '%s',
        'RNLBSERVERID': 'ded6832',
        'g36FastPopSessionRequestNumber': '3',
        'FPSRN': '1',
        'performance_timing': 'other',
        'RNKEY': '1583773*1720513:3356536873: 2136892448:1'
    }

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        self.update_ip_proxys()
        if len(self.proxys) > 0:
            proxy = random.choice(self.proxys)
            spider.logger.info('使用代理>>>>>>>>>>' + proxy + '，剩余代理：' + str(len(self.proxys)))
            request.meta['proxy'] = proxy
        else:
            if request.meta.get('proxy'):
                del request.meta["proxy"]
            spider.logger.info('使用本地>>>>>>>>>>，剩余代理：' + str(len(self.proxys)))
        bs = ''
        for i in range(32):
            bs += chr(random.randint(97, 122))
        _cookie = json.dumps(self.cookie) % bs
        request.cookies = json.loads(_cookie)

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def update_ip_proxys(self):
        if self.need_get_proxy_interval or int(time.time() - self.last_update_proxy) > self.get_proxy_interval:
            proxys = requests.get(self.proxy_url).text
            proxys = json.loads(proxys)
            if len(proxys) < 50:
                # 小于50说明库里的IP不够用了，不能一直去访问获取，应该间隔5分钟后再去获取
                self.need_get_proxy_interval = True
            else:
                self.need_get_proxy_interval = False
            self.last_update_proxy = time.time()
            logger.info("更新IP池，获取IP数量为：%s" % str(len(proxys)))
            for proxy in proxys:
                if judge_legal_ip(proxy[0]):
                    proxy = 'https://%s:%s' % (proxy[0], proxy[1])
                self.proxys.append(proxy)
            self.proxys = list(set(self.proxys))
