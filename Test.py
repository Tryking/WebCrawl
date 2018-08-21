import re
# -!- coding: utf-8 -!-
import requests

url = 'http://36kr.com/p/5149206.html'
get = requests.get(url=url)
print(get.status_code)
with open('test__', mode='a+', encoding='utf-8')as f:
    f.write(str(get.content, encoding='utf-8'))

#
# findall = re.findall(r'<script>var props=(.*)</script>', s)
# print(findall)
