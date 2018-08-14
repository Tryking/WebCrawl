#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
爬取 javfor 网站的封面图
"""
from datetime import date

import requests
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from libs.common import *
from selenium import webdriver
from lxml import etree

JAVFOR_URL = 'https://javfor.me/'
SAVE_DIR = 'javfor_datas'


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

    def get_data(self):
        # 进入浏览器设置
        # options = webdriver.ChromeOptions()
        # # 设置中文
        # options.add_argument('lang=zh_CN.UTF-8')
        # # 更换头部
        # options.add_argument(
        #     'user-agent="Mozilla/5.0 (iPod; U; CPU iPhone OS 2_1 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20"')
        browser = webdriver.Chrome(chrome_options=None)

        # 最大化页面，防止有的内容无法点击
        browser.maximize_window()
        try:
            browser.implicitly_wait(10)
            browser.get(JAVFOR_URL)
            time.sleep(1)
            # 将滚动条移动到页面的底部
            for i in range(20000):
                # js = "window.scrollTo(0, document.body.scrollHeight)"
                # browser.execute_script(js)
                # 按 Down 键
                ActionChains(browser).key_down(Keys.DOWN).perform()
                time.sleep(0.1)
                if i % 100 == 0:
                    self.debug('第 %s / 20000 次' % str(i))
                    time.sleep(10)
            content = browser.page_source
            html = etree.HTML(content)
            img_urls = html.xpath('//div[@id="list-new"]//div[@class="video-img"]/a/img/@src')
            with open('url.txt', mode='a+', encoding='utf-8') as f:
                for img_url in img_urls:
                    f.write(str(img_url))
                    f.write('\n')



        except Exception as e:
            self.error(str(e), get_current_func_name())
            pass
        finally:
            browser.close()
            browser.quit()

    def get_img(self):
        """
        https://cdn.hdporn4.me/javforme_img/108775/1-400.jpg
        https://cdn.hdporn4.me/javforme_img/108773/1-400.jpg
        https://cdn.hdporn4.me/javforme_img/108772/1-400.jpg
        https://cdn.hdporn4.me/javforme_img/108770/1-400.jpg
        https://cdn.hdporn4.me/javforme_img/108771/1-400.jpg
        """
        with open('url.txt', mode='r', encoding='utf-8')as f:
            if not os.path.exists(SAVE_DIR):
                os.mkdir(SAVE_DIR)
            lines = f.readlines()
            sess = requests.Session()
            times = 0
            for line in lines:
                times = times + 1
                start = time.time()
                url = line.strip()
                file_name = SAVE_DIR + os.path.sep + get_standard_file_name(url)
                print(url)
                result = sess.get(url=url)
                if result.status_code == 200:
                    with open(file_name, mode='wb') as f:
                        f.write(result.content)
                else:
                    self.error('url: %s ,访问失败：%s' % (url, str(result.status_code)))
                cost = round((time.time() - start), 2)
                self.debug('第 %s / %s 个，耗时： %s s' % (str(times), str(len(lines)), str(cost)))

    def main(self):
        try:
            self.get_img()
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
