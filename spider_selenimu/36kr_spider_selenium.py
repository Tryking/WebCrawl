# -*- coding: utf-8 -*-
from selenium import webdriver

from news_selenimu.libs.common import *

# 遇到错误后休息时长
EXCEPTION_SLEEP_INTERVAL = 60


class Kr36SpiderSelenium:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    HOST = 'http://36kr.com/'
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
        # prefs = {"profile.managed_default_content_settings.images": 2}
        if get_proxy():
            chrome_options.add_argument('--proxy-server={0}'.format(get_proxy()))
        # chrome_options.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(chrome_options=chrome_options)

    def get_browser_phantomjs(self):
        if get_proxy():
            service_args = [
                '--proxy=%s' % get_proxy(),  # 代理 IP：prot
                '--proxy-type=http',  # 代理类型：http/https
                '--load-images=no',  # 关闭图片加载（可选）
                '--disk-cache=yes',  # 开启缓存（可选）
                '--ignore-ssl-errors=true'  # 忽略https错误（可选）
            ]
        else:
            service_args = [
                '--load-images=no',  # 关闭图片加载（可选）
                '--disk-cache=yes',  # 开启缓存（可选）
                '--ignore-ssl-errors=true'  # 忽略https错误（可选）
            ]
        if self.browser:
            self.browser.close()
            self.browser.quit()
        self.browser = webdriver.PhantomJS(service_args=service_args)
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
        开始获取请求
        """
        try:
            url = self.HOST
            self.init_browser()
            self.browser.get(url=url)
            self.handle_channel(self.browser)
        except Exception as e:
            self.error(str(e), get_current_func_name())
            time.sleep(EXCEPTION_SLEEP_INTERVAL)
            self.init_browser(force_init=True)

    def handle_channel(self, browser):
        """
        处理频道
        """
        # 频道
        channels = browser.find_elements_by_xpath('//ul[contains(@class,"stealth-scroll-bar")]/li')
        for channel in channels:
            channel.click()
            time.sleep(5)

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
    spider = Kr36SpiderSelenium()
    spider.start_requests()
