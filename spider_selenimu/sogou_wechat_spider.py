# -*- coding: utf-8 -*-
import pymongo

from selenium import webdriver
from bs4 import BeautifulSoup
from libs.common import *
from libs.settings import MONGODB_HOST, MONGODB_PORT, MONGODB_USER, MONGODB_PWD, MONGODB_DBNAME
from selenium.webdriver import DesiredCapabilities

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

SOURCE_FILE = '不限分类'
BASE_URL = 'https://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=y&_sug_type_=&' \
           'w=01019900&sut=1292&sst0=1534838560197&lkt=1,1534838560083,1534838560083'

# 是否保存结果到本地
IS_SAVE_ARTICLE_TO_LOCAL = False


class SogouWechatSpiderSelenium:
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
        host = MONGODB_HOST
        port = MONGODB_PORT
        user = MONGODB_USER
        pwd = MONGODB_PWD
        db_name = MONGODB_DBNAME
        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client[db_name]
        if user and user != '':
            self.db.authenticate(name=user, password=pwd)

    def save_article(self, _id, _name, article_title, publish_time, article_content):
        """
        存储文件内容到Mongo
        """
        self.db['sogo_wechat_article'].update_one(filter={'wechat_id': _id, 'article_title': article_title},
                                                  update={'$set': {'wechat_name': _name, 'article_content': article_content,
                                                                   'publish_time': publish_time, 'update_time': get_udpate_time()}},
                                                  upsert=True)

    def match_article(self, _id, title):
        """
        查找库中是否有匹配的文章记录
        :param _id:
        :param title:
        :return:
        """
        record = self.db['sogo_wechat_article'].find_one(filter={'wechat_id': _id, 'article_title': title})
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
                self.get_browser_chrome()
        except Exception as e:
            self.error(str(e), get_current_func_name())

    def judge_is_wechat_verify(self, browser, url):
        """
        判断该当前微信网页是否在验证码网页（debug到有验证码的地方，出现了可以用于解除）
        :return:
        """
        items = browser.find_elements_by_xpath('//div[@class="weui_cells_tips"]')
        if len(items) > 0:
            # 出现了验证码页面
            if '验证码' in items[0].text:
                # TODO： 到了这里告警解决验证码问题
                # 重新启动浏览器，并访问给定url
                self.error('需要输入验证码，重启浏览器')
                self.init_browser(force_init=True)
                self.browser.get(url)
                return False
        return False

    def start_requests(self):
        """
        开始获取请求并处理搜索公众号结果
        """
        try:
            with open(SOURCE_FILE, mode='r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip('\n')
                    url = BASE_URL % line
                    self.init_browser()
                    self.browser.get(url=url)
                    # 公众号列表
                    subscriptions = self.browser.find_elements_by_xpath('//ul[@class="news-list2"]/li//div[@class="img-box"]/a')
                    urls = list()
                    for subscription in subscriptions:
                        url = subscription.get_attribute('href')
                        urls.append(url)

                    other_pages = self.browser.find_elements_by_xpath('//div[@id="pagebar_container"]/a[contains(@id,"sogou_page")]')
                    other_page_urls = list()
                    for other_page in other_pages:
                        url = other_page.get_attribute('href')
                        other_page_urls.append(url)

                    for url in urls:
                        self.handle_subscription(url)

                    # 处理其他页的公众号
                    for url in other_page_urls:
                        self.handle_other_page(url)
            self.close_browser()
        except Exception as e:
            self.error(str(e), get_current_func_name())
            time.sleep(EXCEPTION_SLEEP_INTERVAL)
            self.init_browser(force_init=True)

    def handle_other_page(self, url):
        """
        开始获取请求并处理搜索公众号结果（其他页面）
        """
        try:
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
            self.handle_other_page(url)

    def handle_subscription(self, url):
        """
        处理公众号
        """
        try:
            self.browser.get(url)
            self.judge_is_wechat_verify(self.browser, url)
            # 公众号名称
            wechat_name = None
            try:
                wechat_name = self.browser.find_element_by_xpath('//div[@class="profile_info"]/strong[@class="profile_nickname"]')
            except Exception as e:
                pass
            if wechat_name:
                wechat_name = wechat_name.text
            else:
                wechat_name = 'default_name'
            # 公众号ID
            wechat_id = None
            try:
                # 有的公众号没有显示Id
                wechat_id = self.browser.find_element_by_xpath('//div[@class="profile_info"]/p[@class="profile_account"]')
            except Exception as e:
                pass
            if wechat_id:
                wechat_id = wechat_id.text.replace('微信号: ', '')
            else:
                wechat_id = 'default_id'
            # 文章列表
            articles = self.browser.find_elements_by_xpath(
                '//div[@class="weui_msg_card"]/div[@class="weui_msg_card_bd"]/div[contains(@class, "weui_media_box")]//h4')
            article_urls = list()
            for article in articles:
                title = get_standard_file_name(article.text)
                # 库中没有时才进行下一步查找
                if not self.match_article(wechat_id, title):
                    url = article.get_attribute('hrefs')
                    if 'http://mp.weixin.qq.com' not in url:
                        url = 'http://mp.weixin.qq.com' + url
                    article_urls.append(url)
            for article_url in article_urls:
                self.handle_article(article_url, wechat_id, wechat_name)
        except Exception as e:
            self.error(str(e), get_current_func_name())
            time.sleep(EXCEPTION_SLEEP_INTERVAL)
            self.init_browser(force_init=True)
            self.handle_subscription(url)

    def handle_article(self, url, wechat_id, wechat_name):
        """
        处理文章
        """
        try:
            self.browser.get(url)
            self.judge_is_wechat_verify(self.browser, url=url)
            # 文章名称
            name = None
            publish_time = None
            try:
                name = self.browser.find_element_by_xpath('//h2[@class="rich_media_title"]')
                publish_time = self.browser.find_element_by_xpath('//em[id="publish_time"]')
            except Exception as e:
                try:
                    # 没找到说明是转发的文章，需要找到阅读原文去寻找全文
                    read_original = self.browser.find_element_by_link_text('阅读全文')
                    read_original.click()
                    name = self.browser.find_element_by_xpath('//h2[@class="rich_media_title"]')
                    publish_time = self.browser.find_element_by_xpath('//em[id="publish_time"]')
                except Exception as e:
                    # 此内容因违规无法查看（有这种异常）
                    return False
            finally:
                if name:
                    if publish_time:
                        publish_time = publish_time.text
                    else:
                        publish_time = 'default_time'
                    name = name.text
                    print(name)
                    # 文章内容
                    soup = BeautifulSoup(self.browser.page_source, 'lxml')
                    file_name = 'datas' + os.path.sep + get_standard_file_name(name) + '.html'
                    if IS_SAVE_ARTICLE_TO_LOCAL:
                        with open(file=file_name, mode='a+', encoding='utf-8') as f:
                            f.write(str(soup.prettify()))

                    content = soup.select_one('#js_content')
                    article_content = list()
                    if len(content) > 0:
                        article_title = get_standard_file_name(name)
                        file_name = 'datas' + os.path.sep + article_title
                        if IS_SAVE_ARTICLE_TO_LOCAL:
                            with open(file=file_name, mode='a+', encoding='utf-8') as f:
                                for child in content.stripped_strings:
                                    f.write(str(repr(child)).strip('\''))
                                    article_content.append(str(repr(child)).strip('\''))
                                    f.write('\n')
                        self.save_article(wechat_id, wechat_name, article_title, publish_time, '\n'.join(article_content))
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
    spider = SogouWechatSpiderSelenium()
    spider.start_requests()
