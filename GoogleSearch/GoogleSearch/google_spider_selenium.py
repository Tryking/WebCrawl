#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
爬取 Google 搜索图片
"""
import json
import threading

import requests

from libs.common import *
from selenium import webdriver

GOOGLE_URL = 'https://www.google.com/search?q=%s&source=lnms&tbm=isch'
NUMBER_OF_SCROLLS = 4

KEY_WORDS = ['isis', 'terrorist', 'burqa', 'taliban', 'القاعدة', '基地组织', '伊斯兰国', '恐怖主义', 'black burqa', 'niqab', 'burqa full body',
             '塔利班', 'isis斩首', 'isis标志', '圣战', '伊斯兰', '宗教暴力', '恐怖分子', '罩袍', '本拉登', '萨达姆', '绿教', '伊斯兰殉教', '伊吉拉特',
             '宗教极端', '越南战争', '叙利亚 战争', '伊拉克 战争', '土耳其战争', '海湾战争', '美国911', '凡尔登绞肉机', '印尼 反华']


class DownloadConsumer(threading.Thread):
    """
    更新歌手线程，用于往数据库中更新数据
    """

    def __init__(self, thread_name, urls):
        threading.Thread.__init__(self)
        self.__module = self.__class__.__name__
        self.thread_name = thread_name
        self.urls = urls

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
        msg = "thread_name: %s, %s" % (self.thread_name, msg)
        self.write_file_log(msg, __module, 'debug')

    # error log
    def error(self, msg, func_name=''):
        __module = "%s.%s" % (self.__module, func_name)
        msg = "thread_name: %s, %s" % (self.thread_name, msg)
        self.write_file_log(msg, __module, 'error')

    def download_images(self, imgs):
        sess = requests.Session()
        if not os.path.exists('google_data'):
            os.mkdir('google_data')
        requests_proxies = {
            'http': 'http:127.0.0.1:1080',
            'https': 'https:127.0.0.1:1080',
        }
        i = 0
        for img in imgs:
            i += 1
            self.debug('%s - 第 %s / %s 个' % (self.thread_name, str(i), str(len(imgs))))
            img = img.split('"')[-1].replace('\\', '')
            try:
                response = sess.get(img, proxies=requests_proxies)
                if response.status_code == '200':
                    img_content = response.content
                    img_name = 'google_data' + os.path.sep + get_standard_file_name(img)
                    with open(img_name, 'wb') as f:
                        f.write(img_content)
                    self.debug('pic saved completed')
                else:
                    self.debug('pic download fail: %s - %s' % (str(response.status_code), str(img)))
            except Exception as e:
                self.error('pic download fail: %s - %s' % (str(response.status_code), str(img)))

        self.debug('%s - all pics saved' % self.thread_name)

    def run(self):
        try:
            self.download_images(self.urls)
        except Exception as e:
            self.error(str(e), get_current_func_name())


class Monitor:
    def __init__(self):
        try:
            self.module = self.__class__.__name__
        except Exception as e:
            self.error(str(e), get_current_func_name())

    @staticmethod
    def write_file_log(msg, module='', level='error'):
        filename = os.path.split(__file__)[1]
        if level == 'debug':
            logging.getLogger().debug('File:' + filename + ', ' + module + ': ' + msg)
        elif level == 'warning':
            logging.getLogger().warning('File:' + filename + ', ' + module + ': ' + msg)
        else:
            logging.getLogger().error('File:' + filename + ', ' + module + ': ' + msg)

    # 调试日志
    def debug(self, msg, func_name=''):
        module = "%s.%s" % (self.module, func_name)
        self.write_file_log(msg, module, 'debug')

    # 错误日志
    def error(self, msg, func_time=''):
        module = "%s.%s" % (self.module, func_time)
        self.write_file_log(msg, module, 'error')

    def get_google_search_image_url(self):
        PROXY = "127.0.0.1:1080"
        browser_options = webdriver.ChromeOptions()
        # 禁止加载图片
        prefs = {"profile.managed_default_content_settings.images": 2}
        browser_options.add_argument('--proxy-server={0}'.format(PROXY))
        browser_options.add_experimental_option("prefs", prefs)
        browser = webdriver.Chrome(chrome_options=browser_options)

        # 最大化页面，防止有的内容无法点击
        browser.maximize_window()
        try:
            for key_word in KEY_WORDS:
                browser.implicitly_wait(10)
                url = GOOGLE_URL % key_word
                browser.get(url)
                time.sleep(1)

                for _ in range(NUMBER_OF_SCROLLS):
                    for __ in range(5):
                        # multiple scrolls needed to show all 400 images
                        browser.execute_script("window.scrollBy(0, 1000000)")
                        time.sleep(2)
                    # to load next 400 images
                    time.sleep(5)
                    try:
                        browser.find_element_by_xpath('//*[@id="smb"]').click()
                    except Exception as e:
                        print("Process-{0} reach the end of page or get the maximum number of requested images".format(key_word))
                        break

                img_urls = list()
                imges = browser.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
                for img in imges:
                    img_url = json.loads(img.get_attribute('innerHTML'))["ou"]
                    # img_type = json.loads(img.get_attribute('innerHTML'))["ity"]
                    img_urls.append(img_url)
                with open(get_standard_file_name(key_word) + '_url.txt', mode='a+', encoding='utf-8') as f:
                    for img_url in img_urls:
                        f.write(str(img_url))
                        f.write('\n')

        except Exception as e:
            self.error(str(e), get_current_func_name())
            pass
        finally:
            browser.close()
            browser.quit()

    def main(self):
        try:
            # 搜索Google关键字的图片链接放到URL中
            # self.get_google_search_image_url()

            # 下载指定文件中的URL资源
            dirs = os.listdir('.')
            thread_list = list()
            for file in dirs:
                urls = list()
                if '_url' in file:
                    with open(file=file, mode='r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines:
                            urls.append(line.strip())
                    thread = DownloadConsumer('thread - %s' % str(file), urls)
                    thread_list.append(thread)
            # 开启线程
            for t in thread_list:
                t.start()
            for t in thread_list:
                t.join()
        except Exception as e:
            self.error(str(e), get_current_func_name())


if __name__ == '__main__':
    if not os.path.exists('logs'):
        os.mkdir('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG,
             logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    # 专门存储错误日志
    init_log(console_level=logging.ERROR, file_level=logging.ERROR,
             logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")
    monitor = Monitor()
    monitor.main()
