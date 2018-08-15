import requests

url = 'https://cl.phncdn.com/pics/albums/015/955/552/192357462/original_192357462.jpg'
get = requests.get(url)
print(get.content)
