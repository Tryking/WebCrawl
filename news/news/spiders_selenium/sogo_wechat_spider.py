# -*- coding: utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
from news.news.libs.common import *

"""
Sogo 的 微信搜索
"""
"""
Bs4 文档：https://beautifulsoup.readthedocs.io/zh_CN/latest/
"""
# 遇到错误后休息时长
EXCEPTION_SLEEP_INTERVAL = 60


class SogoWechatSpiderSelenium:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    if not os.path.exists('datas'):
        os.mkdir('datas')

    HOST = 'https://weixin.sogou.com/'
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
        if get_proxy():
            chrome_options.add_argument('--proxy-server={0}'.format(get_proxy()))
        chrome_options.add_experimental_option("prefs", prefs)
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
        开始获取请求并处理搜索公众号结果
        """
        try:
            url = self.HOST
            url = 'https://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=y&_sug_type_=&w=01019900&sut=1292&sst0=1534838560197&lkt=1,1534838560083,1534838560083' % '人民日报'
            self.init_browser()
            self.browser.get(url=url)
            # 公众号列表
            subscriptions = self.browser.find_elements_by_xpath('//ul[@class="news-list2"]/li//div[@class="img-box"]/a')
            urls = list()
            for subscription in subscriptions:
                url = subscription.get_attribute('href')
                urls.append(url)
            for url in urls:
                self.handle_subscription(url)
        except Exception as e:
            self.error(str(e), get_current_func_name())
            time.sleep(EXCEPTION_SLEEP_INTERVAL)
            self.init_browser(force_init=True)

    def handle_subscription(self, url):
        """
        处理公众号
        """
        try:
            self.browser.get(url)
            # 公众号名称
            name = self.browser.find_element_by_xpath('//div[@class="profile_info"]/strong')
            name = name.text
            # 文章列表
            articles = self.browser.find_elements_by_xpath(
                '//div[@class="weui_msg_card"]/div[@class="weui_msg_card_bd"]/div[contains(@class, "weui_media_box")]//h4')
            article_urls = list()
            for article in articles:
                url = article.get_attribute('hrefs')
                if 'http://mp.weixin.qq.com' not in url:
                    url = 'http://mp.weixin.qq.com' + url
                article_urls.append(url)
            for article_url in article_urls:
                self.handle_article(article_url)
        except Exception as e:
            self.error(str(e), get_current_func_name())
            time.sleep(EXCEPTION_SLEEP_INTERVAL)
            self.init_browser(force_init=True)
            self.handle_subscription(url)

    def handle_article(self, url):
        """
        处理文章
        """
        try:
            self.browser.get(url)
            # 文章名称
            name = None
            try:
                name = self.browser.find_element_by_xpath('//h2[@class="rich_media_title"]')
            except Exception as e:
                # 没找到说明是转发的文章，需要找到阅读原文去寻找全文
                read_original = self.browser.find_element_by_link_text('阅读全文')
                read_original.click()
                name = self.browser.find_element_by_xpath('//h2[@class="rich_media_title"]')
            finally:
                # 此内容因违规无法查看（有这种异常）
                if name:
                    name = name.text
                    print(name)
                    # 文章内容
                    soup = BeautifulSoup(self.browser.page_source, 'lxml')
                    file_name = 'datas' + os.path.sep + get_standard_file_name(name) + '.html'
                    with open(file=file_name, mode='a+', encoding='utf-8') as f:
                        f.write(str(soup.prettify()))

                    content = soup.select_one('#js_content')
                    if len(content) > 0:
                        file_name = 'datas' + os.path.sep + get_standard_file_name(name)
                        with open(file=file_name, mode='a+', encoding='utf-8') as f:
                            for child in content.stripped_strings:
                                f.write(str(repr(child)).strip('\''))
                                f.write('\n')

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
    spider = SogoWechatSpiderSelenium()
    spider.start_requests()
