import os
import pickle
import random

from captcha.image import ImageCaptcha
from PIL import Image
import numpy as np
from config import *

"""
https://cuiqingcai.com/5709.html
"""


def generate_captcha(text='test'):
    """
    生成文本为 text 的验证码图片，并返回其对应的 Numpy 数组
    :param text:
    :return:
    """
    if not os.path.exists(CAPTCHA_IMAGE_SAVE_PATH):
        os.mkdir(CAPTCHA_IMAGE_SAVE_PATH)
    image = ImageCaptcha()
    captcha = image.generate(text)
    captcha_image = Image.open(captcha)
    # show the image
    # captcha_image.show()
    # 保存图片
    captcha_image.save(os.path.join(CAPTCHA_IMAGE_SAVE_PATH, text + '.jpg'))

    captcha_array = np.array(captcha_image)
    return captcha_array


def text2vec(text):
    if len(text) > CAPTCHA_LENGTH:
        return False
    vector = np.zeros(CAPTCHA_LENGTH * VOCAB_LENGTH)
    # enumerate 为遍历text，i为位置，c为数据
    for i, c in enumerate(text):
        index = i * VOCAB_LENGTH + VOCAB.index(c)
        vector[index] = 1
    return vector


def vec2text(vector):
    if not isinstance(vector, np.ndarray):
        vector = np.asarray(vector)
    vector = np.reshape(vector, [CAPTCHA_LENGTH, -1])
    text = ''
    for item in vector:
        text += VOCAB[np.argmax(item)]
    return text


def get_random_text():
    text = ''
    for i in range(CAPTCHA_LENGTH):
        text += random.choice(VOCAB)
    return text


def generate_data():
    data_x, data_y = [], []

    for i in range(DATA_LENGTH):
        text = get_random_text()
        captcha_array = generate_captcha(text)
        vector = text2vec(text)
        data_x.append(captcha_array)
        data_y.append(vector)

    # write data to pickle
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    x = np.asarray(data_x, np.float32)
    y = np.asarray(data_y, np.float32)
    with open(os.path.join(DATA_PATH, 'data.pkl'), 'wb')as f:
        pickle.dump(x, f)
        pickle.dump(y, f)


if __name__ == '__main__':
    pass
    # generate_data()
