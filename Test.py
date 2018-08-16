import requests

url = 'https://ci.phncdn.com/pics/albums/000/513/721/30461512/(m=e-yaaGqaa)(mh=739j3IZ81Z2uEfu4)original_30461512.jpg'
get = requests.get(url=url)
with open('test.jpg', mode='wb') as f:
    f.write(get.content)
