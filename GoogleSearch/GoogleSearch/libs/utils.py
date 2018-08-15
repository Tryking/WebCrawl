import os

import imghdr
from PIL import Image


def check_file_suffix(file_name, suffix):
    """
    检查文件的后缀是否为指定后缀
    :param file_name:
    :param suffix:
    :return:
    """
    rsplit = str(file_name).rsplit('.', 1)
    return rsplit[len(rsplit) - 1] == suffix


def check_img_file():
    """
    检测某文件夹下不合法的图像文件，并将其进行删除，
    检测图像后缀名不合法的文件，修改其后缀名
    :return:
    """
    # 要检测的文件夹
    path = '../google_data'
    dirs = os.listdir(path)
    i = 0
    for file in dirs:
        i += 1
        file_path = path + os.path.sep + file
        print(i, '/', len(dirs))
        try:
            a = Image.open(file_path)
            status = a.verify()
            img_type = imghdr.what(file_path)
            is_suffix = check_file_suffix(file_name=file_path, suffix=img_type)
            if not is_suffix:
                os.rename(file_path, file_path + '.' + img_type)
                print('修改名称为： %s ' % (file_path + '.' + img_type))
            print(is_suffix)
            print(img_type)
            print(status, file)
        except Exception as e:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print('False, Remove', file_path)
                except:
                    pass
            pass


if __name__ == '__main__':
    check_img_file()
