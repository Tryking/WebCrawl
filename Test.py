import re
# -!- coding: utf-8 -!-
import numpy as np
import requests

# url = 'http://mp.weixin.qq.com/profile?src=3&timestamp=1534934117&ver=1&signature=Ek4PhlS3l5co0DN61nuiL7woaxOx9ve8VOClzbFtOkoLSCO96Ety4iPxGfPD1NGy0INc5mjRJMoJ*xIPW3G4Wg=='
#
# for i in range(20):
#     result = requests.get(url=url)
#     with open('test.txt', mode='a+', encoding='utf-8') as f:
#         f.write(result.text)
#         print(result.text)

VOCAB = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
VOCAB_LENGTH = len(VOCAB)
CAPTCHA_LENGTH = 2
text = '23'
vector = np.zeros(CAPTCHA_LENGTH * VOCAB_LENGTH)
print(vector)
for i, c in enumerate(text):
    print(i, c)
    index = i * VOCAB_LENGTH + VOCAB.index(c)
    print(index)
    vector[index] = 1
print(vector)
