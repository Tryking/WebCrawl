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

# LOGIN_URL = 'https://accounts.douban.com/j/mobile/login/basic'
#
#
# def login():
#     headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
#                'host': 'accounts.douban.com', 'Referer': 'https://accounts.douban.com/passport/login_popup?login_source=anony'}
#     data = {'name': '13257788084', 'password': 'db123456', 'remember': False}
#     response = requests.post(url=LOGIN_URL, data=data, headers=headers)
#     cookies = response.cookies
#
#
#
# login()

for i in range(0, 10000, 20):
    print(i)
