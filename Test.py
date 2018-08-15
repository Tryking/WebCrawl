import requests

url = ''
get = requests.get('https://i.ytimg.com/vi/hAclQLHNjmc/hqdefault.jpg')
print(get.content)
