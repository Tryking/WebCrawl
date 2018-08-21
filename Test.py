import re
# -!- coding: utf-8 -!-
import requests

BASE_URL = 'https://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=y&_sug_type_=&w=01019900&sut=5243&sst0=1534837995239&lkt=0,0,0'
keywords = ['爱']
get = requests.get(url=BASE_URL % keywords[0])
print(get.status_code)
with open('test__', mode='a+', encoding='utf-8')as f:
    f.write(str(get.content, encoding='utf-8'))

#
# findall = re.findall(r'<script>var props=(.*)</script>', s)
# print(findall)
