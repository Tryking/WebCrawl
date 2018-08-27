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
百度图片搜索
"""

# 遇到错误后休息时长
EXCEPTION_SLEEP_INTERVAL = 60

# 是否自动换IP（启动浏览器时更换IP）
IS_AUTO_CHANGE_IP = False

BASE_URL = 'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1535352159261_R&pv=' \
           '&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=%s'
SAVE_FILE_PATH = os.path.join('datas', 'jinritoutiao')

PHANTOMJS_SLEEP_TIME = 3

KEYWORDS = ['老人', '小孩', '成年人', '沙滩 人', '女人']


class BaiduSoiderSelenium:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    if not os.path.exists(SAVE_FILE_PATH):
        os.makedirs(SAVE_FILE_PATH)

    HOST = 'https://image.baidu.com'
    save_file_name = 'default'

    def __init__(self):
        self.__module = self.__class__.__name__
        self.browser = None

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
                self.get_browser_chrome()
        except Exception as e:
            self.error(str(e), get_current_func_name())

    def start_requests(self):
        """
        开始获取请求并处理搜索公众号结果
        """
        try:
            self.init_browser()
            for keyword in KEYWORDS:
                url = BASE_URL % keyword
                self.browser.get(url=url)

                # 向下拉更新
                for __ in range(30):
                    # multiple scrolls needed to show all 400 images
                    self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)

                # # 将滚动条移动到页面的底部（模拟按键 down）（在服务器上使用 Phantomjs 不管用）
                # for i in range(PRESS_DOWN_TIMES):
                #     ActionChains(self.browser).key_down(Keys.DOWN).perform()
                #     time.sleep(0.1)
                #     if i % 100 == 0:
                #         self.debug('第 %s / %s 次' % (str(i), str(PRESS_DOWN_TIMES)))
                #         time.sleep(2)

                items = list()
                detail_urls = self.browser.find_elements_by_xpath('//div[@class="imgpage"]/ul/li/div/a')
                for item in detail_urls:
                    url = item.get_attribute('href')
                    if self.HOST not in url:
                        url = self.HOST + url
                    items.append(url)

                for url in items:
                    # 处理图片详情
                    self.handle_item(url, keyword)
            self.close_browser()
        except Exception as e:
            self.error(str(e), get_current_func_name())
            time.sleep(EXCEPTION_SLEEP_INTERVAL)
            self.init_browser(force_init=True)
            self.start_requests()

    @staticmethod
    def get_clean_name(original_title):
        return original_title.replace('⋅', '')

    def handle_item(self, url, keyword):
        """
        处理原始图片
        """
        try:
            self.browser.get(url)
            # time.sleep(1)
            imgage_ori_url = self.browser.find_elements_by_xpath('//img[@id="hdFirstImgObj"]')
            if imgage_ori_url and len(imgage_ori_url) > 0:
                imgage_ori_url = imgage_ori_url[0].get_attribute('src')
                with open(keyword + '.txt', mode='a+', encoding='utf-8') as f:
                    f.write(imgage_ori_url)
                    f.write('\n')

        except Exception as e:
            self.error(str(e))

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
    spider = BaiduSoiderSelenium()
    spider.start_requests()
