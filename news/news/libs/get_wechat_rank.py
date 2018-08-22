"""
获取微信公众号排名

微播易：http://top.weiboyi.com
"""
import json
import os

import requests
from common import get_standard_file_name, get_headers

"""
period_type: week / month
category_id: 可以从 result['data']['categoryNotes'] 下获取
period_id：201833（0806-0812），201834（0813-0819）周  月的直接就是月份
rank_type: commercial_rank（营销价值），hasoriginal_snbt_rank（原创能力）
"""
FIRST_URL = 'http://top.weiboyi.com/hwranklist/wechat/get-ranking-list?period_id=201808&period_type=month&category_id=0&rank_type=hasoriginal_snbt_rank'
BASE_URL = 'http://top.weiboyi.com/hwranklist/wechat/get-ranking-list?period_id=201808&period_type=month&category_id=%s&rank_type=hasoriginal_snbt_rank'


def get_category():
    """
    获取分类id
    :return:
    """
    result = requests.get(FIRST_URL, headers=get_headers())
    return_result = list()
    if result.ok and result.status_code == 200:
        result = json.loads(result.text)
        for item in result['data']['categoryNotes']:
            category_id = item['category_id']
            name = item['name']
            return_result.append({'category_id': category_id, 'name': name})
    return return_result


def get_rank_data(url):
    result = requests.get(url, headers=get_headers())
    return_result = list()
    if result.ok and result.status_code == 200:
        result = json.loads(result.text)
        for item in result['data']['rankingList']:
            nick_name = item['wechat_nickname']
            wechat_id = item['wechat_id']
            return_result.append({'nick_name': nick_name, 'wechat_id': wechat_id})
            print(nick_name, wechat_id)
    return return_result


def main():
    if not os.path.exists('datas'):
        os.mkdir('datas')
    category = get_category()
    for item in category:
        url = BASE_URL % item['category_id']
        print('\n\n')
        print(item['name'])
        result = get_rank_data(url=url)
        with open('datas' + os.path.sep + get_standard_file_name(item['name']), mode='a+', encoding='utf-8')as f:
            for data in result:
                f.write(data['nick_name'])
                f.write('\n')


if __name__ == '__main__':
    main()
