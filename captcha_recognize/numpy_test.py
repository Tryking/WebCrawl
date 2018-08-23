"""
reshape
"""
import numpy as np


def reshape_test():
    vector = ((1, 2, 3), (4, 5, 6))
    asarray = np.asarray(vector)
    print(vector)
    print(asarray)
    asarray1 = asarray.reshape(3, 2)
    print(asarray1)
    asarray2 = np.reshape(asarray, [6, -99])
    print(asarray2)


def std_mean_test():
    x = [1, 2, 3, 4, 5]
    x = np.asarray(x)
    mean = x.mean()
    # standard deviation
    manual_cal_std = np.sqrt(((x - np.mean(x)) ** 2).sum() / x.size)
    print(manual_cal_std)
    # numpy.std() 求标准差的时候默认是除以 n 的，即是有偏的，np.std无偏样本标准差方式为 ddof = 1；
    std = x.std()
    print(mean, std)


if __name__ == '__main__':
    std_mean_test()
