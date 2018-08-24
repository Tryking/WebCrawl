# -*- coding: utf-8 -*-
import os
import time

import pymongo

from selenium import webdriver
from bs4 import BeautifulSoup
from libs.common import *
from libs.settings import MONGODB_HOST, MONGODB_PORT, MONGODB_USER, MONGODB_PWD, MONGODB_DBNAME
from selenium.webdriver import DesiredCapabilities, ActionChains
from selenium.webdriver.common.keys import Keys

"""
Sogou 的 微信搜索
"""
"""
Bs4 文档：https://beautifulsoup.readthedocs.io/zh_CN/latest/
"""
# 遇到错误后休息时长
EXCEPTION_SLEEP_INTERVAL = 60

# 是否自动换IP（启动浏览器时更换IP）
IS_AUTO_CHANGE_IP = False

# 800次基本就能获取一天的量了，每天运行一次刚好
PRESS_DOWN_TIMES = 800
BASE_URL = 'https://www.toutiao.com/'
SAVE_FILE_PATH = os.path.join('datas', 'jinritoutiao')

DB_COLLECTION = 'jinritoutiao_article'

PHANTOMJS_SLEEP_TIME = 3


class ToutiaoSoiderSelenium:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    if not os.path.exists(SAVE_FILE_PATH):
        os.makedirs(SAVE_FILE_PATH)

    HOST = 'https://www.toutiao.com'
    save_file_name = 'default'

    def __init__(self):
        self.__module = self.__class__.__name__
        self.browser = None
        host = MONGODB_HOST
        port = MONGODB_PORT
        user = MONGODB_USER
        pwd = MONGODB_PWD
        db_name = MONGODB_DBNAME
        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client[db_name]
        if user and user != '':
            self.db.authenticate(name=user, password=pwd)

    def save_article(self, source_type, source, article_title, publish_time, article_content):
        """
        存储文件内容到Mongo
        """
        self.db[DB_COLLECTION].update_one(filter={'source': source, 'article_title': article_title},
                                          update={'$set': {'article_content': article_content, 'source_type': source_type,
                                                           'publish_time': publish_time, 'update_time': get_udpate_time(),
                                                           'update_date': get_before_date(before_day=0)}},
                                          upsert=True)

    def match_article(self, source='default', title='default'):
        """
        查找库中是否有匹配的文章记录
        """
        record = self.db[DB_COLLECTION].find_one(filter={'source': source, 'article_title': title})
        if record:
            return True
        else:
            return False

    def get_browser_chrome(self):
        if self.browser:
            self.browser.close()
            self.browser.quit()
        chrome_options = webdriver.ChromeOptions()
        # 无头浏览
        # chrome_options.headless = True
        # 禁止加载图片
        prefs = {"profile.managed_default_content_settings.images": 2}
        if IS_AUTO_CHANGE_IP:
            proxy_ip = get_available_ip_proxy()
            if proxy_ip:
                self.debug('使用代理IP：%s' % proxy_ip)
                chrome_options.add_argument('--proxy-server={0}'.format(proxy_ip))
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('user-agent="%s"' % get_user_agent())
        self.browser = webdriver.Chrome(chrome_options=chrome_options)

    def close_browser(self):
        if self.browser:
            self.browser.close()
            self.browser.quit()

    def get_browser_phantomjs(self):
        if self.browser:
            self.browser.close()
            self.browser.quit()
        service_args = None
        if IS_AUTO_CHANGE_IP:
            proxy_ip = get_available_ip_proxy()
            if proxy_ip:
                self.debug('使用代理IP：%s' % proxy_ip)
                service_args = [
                    '--proxy=%s' % proxy_ip,  # 代理 IP：prot
                    '--proxy-type=http',  # 代理类型：http/https
                    '--load-images=no',  # 关闭图片加载（可选）
                    '--disk-cache=yes',  # 开启缓存（可选）
                    '--ignore-ssl-errors=true'  # 忽略https错误（可选）
                ]
        if not service_args:
            service_args = [
                '--load-images=no',  # 关闭图片加载（可选）
                '--disk-cache=yes',  # 开启缓存（可选）
                '--ignore-ssl-errors=true'  # 忽略https错误（可选）
            ]
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = get_user_agent()
        self.browser = webdriver.PhantomJS(service_args=service_args, desired_capabilities=dcap)
        # 设置超时选项（get网页超时）
        self.browser.set_page_load_timeout(15)

    def init_browser(self, force_init=False):
        try:
            if not self.browser or force_init:
                self.debug('>>> 初始化 browser ...')
                self.get_browser_phantomjs()
        except Exception as e:
            self.error(str(e), get_current_func_name())

    def start_requests(self):
        """
        开始获取请求并处理搜索公众号结果
        """
        try:
            url = BASE_URL
            self.init_browser()
            self.browser.get(url=url)

            # 获取所有类型条目
            items = dict()
            category = self.browser.find_elements_by_xpath('//div[@ga_event="left-channel-click"]/ul/li/a')
            for item in category:
                url = item.get_attribute('href')
                name = item.find_element_by_xpath('./span')
                name = name.text
                if url and self.HOST in url:
                    items[name] = url

            # 获取更多条目
            category = self.browser.find_elements_by_xpath('//div[@class="wchannel-more-layer"]/ul/li/a')
            for item in category:
                url = item.get_attribute('href')
                name = item.find_element_by_xpath('./span')
                name = name.text
                if url and self.HOST in url:
                    items[name] = url

            for name, url in items.items():
                # 处理单个条目的文章列表
                self.handle_item(name, url)
            self.close_browser()
        except Exception as e:
            self.error(str(e), get_current_func_name())
            time.sleep(EXCEPTION_SLEEP_INTERVAL)
            self.init_browser(force_init=True)

    @staticmethod
    def get_clean_name(original_title):
        return original_title.replace('⋅', '')

    def handle_item(self, name, url):
        """
        处理文章列表
        """
        try:
            self.browser.get(url)
            # Phantomjs 不好识别
            time.sleep(PHANTOMJS_SLEEP_TIME)
            articles = self.browser.find_elements_by_xpath('//div[@class="rbox-inner"]')

            if not articles or len(articles) == 0:
                # 说明此页面不是标准内容页面，不处理
                self.debug('%s 不是标准页面，不爬取' % name)
                return False

            # 向下拉更新
            for __ in range(10):
                # multiple scrolls needed to show all 400 images
                self.browser.execute_script("window.scrollBy(0, 1000000)")
                time.sleep(2)

            # # 将滚动条移动到页面的底部（模拟按键 down）（在服务器上使用 Phantomjs 不管用）
            # for i in range(PRESS_DOWN_TIMES):
            #     ActionChains(self.browser).key_down(Keys.DOWN).perform()
            #     time.sleep(0.1)
            #     if i % 100 == 0:
            #         self.debug('第 %s / %s 次' % (str(i), str(PRESS_DOWN_TIMES)))
            #         time.sleep(2)

            articles = self.browser.find_elements_by_xpath('//div[@class="rbox-inner"]')
            urls = list()
            for article in articles:
                source_from = article.find_element_by_xpath('.//a[contains(@class, "source")]').text.strip()
                source_from = self.get_clean_name(source_from)
                title = article.find_element_by_xpath('./div[@class="title-box"]/a').text.strip()
                if not self.match_article(source=source_from, title=title):
                    url = article.find_element_by_xpath('./div[@class="title-box"]/a').get_attribute('href')
                    if self.HOST in url:
                        urls.append(url)
            # 遍历文章，获取内容
            for url in urls:
                self.handle_article(url=url, source_type=name)
        except Exception as e:
            self.error(str(e), get_current_func_name())
            time.sleep(EXCEPTION_SLEEP_INTERVAL)
            self.init_browser(force_init=True)

    def handle_article(self, url, source_type):
        """
        处理文章
        """
        try:
            self.browser.get(url)
            # Phantomjs 不好识别
            time.sleep(PHANTOMJS_SLEEP_TIME)
            # 文章名称
            name = None
            publish_from = 'default'
            publish_time = 'default'
            try:
                name = self.browser.find_element_by_xpath('//h1[@class="article-title"]')
                sources = self.browser.find_elements_by_xpath('//div[@class="article-sub"]/span')
                if sources and len(sources) >= 2:
                    if len(sources) == 2:
                        publish_from = sources[0].text.strip()
                        publish_time = sources[1].text.strip()
                    else:
                        publish_from = sources[1].text.strip()
                        publish_time = sources[2].text.strip()
                else:
                    try:
                        sources = self.browser.find_elements_by_xpath('//div[@class="articleInfo"]/span')
                        if sources and len(sources) >= 3:
                            publish_from = sources[1].text.strip()
                            publish_time = sources[2].text.strip()
                    except Exception as e:
                        pass
            except Exception as e:
                pass
            finally:
                if name:
                    name = name.text
                    print(name)
                    # 文章内容
                    soup = BeautifulSoup(self.browser.page_source, 'lxml')
                    file_name = SAVE_FILE_PATH + os.path.sep + get_standard_file_name(name) + '.html'
                    with open(file=file_name, mode='a+', encoding='utf-8') as f:
                        f.write(str(soup.prettify()))

                    content = soup.select_one('.article-content')
                    article_content = list()
                    if len(content) > 0:
                        article_title = name
                        file_name = SAVE_FILE_PATH + os.path.sep + os.path.sep + get_standard_file_name(name)
                        with open(file=file_name, mode='a+', encoding='utf-8') as f:
                            for child in content.stripped_strings:
                                f.write(str(repr(child)).strip('\''))
                                article_content.append(str(repr(child)).strip('\''))
                                f.write('\n')
                        self.save_article(source_type, publish_from, article_title, publish_time, '\n'.join(article_content))
        except Exception as e:
            self.error(str(e), get_current_func_name())
            time.sleep(EXCEPTION_SLEEP_INTERVAL)
            self.init_browser(force_init=True)

    @staticmethod
    def write_file_log(msg, __module='', level='error'):
        filename = os.path.split(__file__)[1]
        if level == 'debug':
            logging.getLogger().debug('File:' + filename + ', ' + __module + ': ' + msg)
        elif level == 'warning':
            logging.getLogger().warning('File:' + filename + ', ' + __module + ': ' + msg)
        else:
            logging.getLogger().error('File:' + filename + ', ' + __module + ': ' + msg)

    # debug log
    def debug(self, msg, func_name=''):
        __module = "%s.%s" % (self.__module, func_name)
        self.write_file_log(msg, __module, 'debug')

    # error log
    def error(self, msg, func_name=''):
        __module = "%s.%s" % (self.__module, func_name)
        self.write_file_log(msg, __module, 'error')


if __name__ == '__main__':
    spider = ToutiaoSoiderSelenium()
    spider.start_requests()
