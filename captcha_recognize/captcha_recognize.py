from captcha.image import ImageCaptcha
from PIL import Image
import numpy as np

"""
https://cuiqingcai.com/5709.html
"""
# 验证码长度
CAPTCHA_LENGTH = 2

# 词表
VOCAB = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
VOCAB_LENGTH = len(VOCAB)


def generate_captcha(text='test'):
    """
    生成文本为 text 的验证码图片，并返回其对应的 Numpy 数组
    :param text:
    :return:
    """
    image = ImageCaptcha()
    captcha = image.generate(text)
    captcha_image = Image.open(captcha)
    captcha_image.show()
    # 保存图片
    captcha_image.save(text + '.jpg')

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


if __name__ == '__main__':
    vector = text2vec('1234')
    text = vec2text(vector)
    print(vector, text)
