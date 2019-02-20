"""
汉辞网 http://www.hydcd.com/ 的成语爬取

http://www.hydcd.com/cy/fkccy/images/CF91100-50.png
"""
import os

import requests
from lxml import etree

IMG_URL_BASE = 'http://www.hydcd.com/cy/fkccy/'
first_url = 'http://www.hydcd.com/cy/fkccy/index.htm'
other_url = 'http://www.hydcd.com/cy/fkccy/index%s.htm'
SAVE_PATH = 'datas'
if not os.path.isdir(SAVE_PATH):
    os.makedirs(SAVE_PATH)
urls = [first_url]
for i in range(2, 11):
    urls.append(other_url % i)

for url in urls:
    result = requests.get(url)
    content = str(result.content, 'gbk')
    html = etree.HTML(content)
    items = html.xpath('//*[@id="table1"]//tr/td/p/img')
    for item in items:
        word = item.xpath('@alt')
        if len(word) > 0:
            word = word[0]
        src = item.xpath('@src')
        if len(src) > 0:
            src = src[0]
            image_url = IMG_URL_BASE + src
            image_result = requests.get(url=image_url)
            with open(os.path.join(SAVE_PATH, word + '.png'), 'wb') as file:
                file.write(image_result.content)
        print(word, src)
