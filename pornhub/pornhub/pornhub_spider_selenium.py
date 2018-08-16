# -*- coding: utf-8 -*-
from selenium import webdriver

from libs.common import *

# 初始获取资源URL （https://www.pornhub.com/albums/straight?search=female）
BASE_URL = 'https://www.pornhub.com/albums/%s?search=%s'
# 模型 misc-miscellaneous（混杂的）
SEGMENTS = ['female']
# 分类
TAGS = ['Tits', 'Ass', 'Pussy', 'Amateur', 'Dick', 'Hot', 'Teen', 'Hentai', 'Sex', 'Boobs', 'Babe', 'Cum', 'Blonde', 'Blowjob', 'Anal', 'Black',
        'Brunette', 'Asian', 'MILF', 'Cumshot', 'Pornstar', 'Hardcore', 'Celebrity', 'Lesbian', 'Ebony', 'Fetish', 'BBW', 'Masturbation',
        'Facial', 'Tribute', 'BDSM']

PROXY = None
# 遇到错误后休息时长
EXCEPTION_SLEEP_INTERVAL = 10


class PornhubSpiderSelenium:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    init_log(console_level=logging.ERROR, file_level=logging.ERROR, logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")

    HOST = 'https://www.pornhub.com'
    save_file_name = 'default'
    if not os.path.exists('url_file'):
        os.mkdir('url_file')

    def __init__(self):
        self.__module = self.__class__.__name__
        self.browser = None

    def get_browser_chrome(self):
        if self.browser:
            self.browser.close()
            self.browser.quit()
        chrome_options = webdriver.ChromeOptions()
        # 无头浏览
        chrome_options.headless = True
        # 禁止加载图片
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_argument('--proxy-server={0}'.format(PROXY))
        chrome_options.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(chrome_options=chrome_options)

    def get_browser_phantomjs(self):
        if PROXY:
            service_args = [
                '--proxy=%s' % PROXY,  # 代理 IP：prot
                '--proxy-type=https',  # 代理类型：http/https
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

    def init_browser(self, force_init=False):
        try:
            if not self.browser or force_init:
                self.debug('>>> 初始化 browser ...')
                self.get_browser_phantomjs()
        except Exception as e:
            self.error(str(e), get_current_func_name())

    def start_requests(self):
        """
        开始获取请求
        """
        for segment in SEGMENTS:
            for tag in TAGS:
                try:
                    url = BASE_URL % (segment, tag.lower())
                    self.debug(
                        '>>> segment: %s , %s / %s >>> tag: %s , %s / %s' % (
                            segment, SEGMENTS.index(segment), len(SEGMENTS), tag, TAGS.index(tag), len(TAGS)))
                    self.save_file_name = 'url_file' + os.path.sep + segment + '-' + tag.lower()
                    self.init_browser()
                    self.browser.get(url=url)
                    self.handle_search(self.browser)
                except Exception as e:
                    self.error(str(e), get_current_func_name())
                    self.error('>>> segment: %s , %s / %s >>> tag: %s , %s / %s >>> 异常，等待后重新开始' % (
                        segment, SEGMENTS.index(segment), len(SEGMENTS), tag, TAGS.index(tag), len(TAGS)))
                    time.sleep(EXCEPTION_SLEEP_INTERVAL)
                    self.init_browser(force_init=True)

    def handle_search(self, browser):
        """
        处理首次搜索页
        :param browser:
        """
        # 搜索页
        url_elements = browser.find_elements_by_xpath('//li[contains(@class,"photoAlbumListContainer")]/div/a')
        urls = list()
        for url in url_elements:
            url = url.get_attribute('href')
            if 'http' not in url:
                url = self.HOST + url
            urls.append(url)
        for url in urls:
            try:
                self.debug('>>> 搜索页:  %s / %s ' % (urls.index(url), len(urls)))
                self.init_browser()
                self.browser.get(url=url)
                self.parse_album(browser)
            except Exception as e:
                self.error(str(e), get_current_func_name())
                self.error('>>> 搜索页:  %s / %s >>> 异常，等待重新开始' % (urls.index(url), len(urls)))
                time.sleep(EXCEPTION_SLEEP_INTERVAL)
                self.init_browser(force_init=True)

    def parse_album(self, browser):
        image_detail_urls = browser.find_elements_by_xpath('//li[contains(@class,"photoAlbumListContainer")]/div/a')
        urls = list()
        for url in image_detail_urls:
            url = url.get_attribute('href')
            if 'http' not in url:
                url = self.HOST + url
            urls.append(url)
        for url in urls:
            try:
                self.debug('>>> 结果页:  %s / %s ' % (urls.index(url), len(urls)))
                self.init_browser()
                self.browser.get(url=url)
                self.parse_image_detail(browser)
            except Exception as e:
                self.error(str(e), get_current_func_name())
                self.error('>>> 结果页:  %s / %s >>> 异常，等待重新开始' % (urls.index(url), len(urls)))
                time.sleep(EXCEPTION_SLEEP_INTERVAL)
                self.init_browser(force_init=True)

    def parse_image_detail(self, browser):
        try:
            img_url = browser.find_element_by_xpath('//*[@id="photoImageSection"]/div[contains(@class,"centerImage")]//img')
            if img_url:
                url = img_url.get_attribute('src')
                with open(self.save_file_name, mode='a+', encoding='utf-8') as f:
                    f.write(str(url))
                    f.write('\n')
        except Exception as e:
            self.error(str(e), get_current_func_name())

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
    spider = PornhubSpiderSelenium()
    spider.start_requests()
