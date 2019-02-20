import re

import requests

# url = 'https://movie.douban.com/subject/30377703/comments?start=0&limit=30&sort=new_score&status=P'
# result = requests.get(url=url)
# print(result.status_code)
# with open('test.html', mode='a+', encoding='utf-8') as f:
#     f.write(result.text)

# s = [1, 2, 3]
# item = next((x for x in s if x > 2), None)
# print(item)
s = 'allstar10 rating'

findall = re.findall('allstar(\d+?)0', s, re.I)
print(findall)

s = 4
