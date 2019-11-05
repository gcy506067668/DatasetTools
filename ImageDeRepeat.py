from db.URLDatabase import DBAPI
import os, time
import cv2
import numpy as np
import math
from scipy.ndimage import uniform_filter, gaussian_filter
from skimage.util.dtype import dtype_range
from skimage.util.arraycrop import crop
from multiprocessing import Process, Array


# python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/17 12:03
# @Author  : dyt

def getfeature(img):
    win_size = 7  # backwards compatibility
    ux = [[0 for i in range(5)] for j in range(len(img))]
    uxx = [[0 for i in range(5)] for j in range(len(img))]
    vx = [[0 for i in range(5)] for j in range(len(img))]
    for currIndex, X in enumerate(img):

        nch = X.shape[-1]
        for ch in range(nch):
            X = X.astype(np.float64)

            dmin, dmax = dtype_range[X.dtype.type]
            data_range = dmax - dmin

            ndim = X[..., ch].ndim

            NP = win_size ** ndim

            cov_norm = NP / (NP - 1)  # sample covariance

            filter_func = uniform_filter

            ux[currIndex][ch] = filter_func(X[..., ch], size=win_size)
            uxx[currIndex][ch] = filter_func(X[..., ch] * X[..., ch], size=win_size)

            vx[currIndex][ch] = cov_norm * (uxx[currIndex][ch] - ux[currIndex][ch] * ux[currIndex][ch])

    return ux, uxx, vx


def compare_ssim(img, X, Y, ch=-1, uxlist=None, uxxlist=None, vxlist=None, multichannel=True):
    if uxlist is None: uxlist, uxxlist, vxlist = getfeature(img)
    if multichannel:
        # loop over channels
        nch = img[X].shape[-1]
        mssim = np.empty(nch)

        for ch in range(nch):
            ch_result = compare_ssim(img, X, Y, ch, uxlist, uxxlist, vxlist, False)
            mssim[..., ch] = ch_result
        mssim = mssim.mean()

        return mssim

    imgx = img[X]
    imgy = img[Y]
    if ch >= 0:
        imgx = img[X][..., ch]
        imgy = img[Y][..., ch]

    win_size = 7  # backwards compatibility

    filter_func = uniform_filter
    imgx = imgx.astype(np.float64)
    imgy = imgy.astype(np.float64)

    cov_norm = 1.0208333333333333
    # compute (weighted) means
    ux = uxlist[X][ch]
    uy = uxlist[Y][ch]

    # compute (weighted) variances and covariances
    uxx = uxxlist[X][ch]
    uyy = uxxlist[Y][ch]
    uxy = filter_func(imgx * imgy, size=win_size)
    vx = vxlist[X][ch]
    vy = vxlist[Y][ch]
    vxy = cov_norm * (uxy - ux * uy)

    C1 = 6.502500000000001
    C2 = 58.522499999999994
    A1, A2, B1, B2 = ((2 * ux * uy + C1,
                       2 * vxy + C2,
                       ux ** 2 + uy ** 2 + C1,
                       vx + vy + C2))
    D = B1 * B2
    S = (A1 * A2) / D

    # to avoid edge effects will ignore filter radius strip around edges

    pad = 3
    # compute (weighted) mean of ssim
    mssim = crop(S, pad).mean()

    return mssim


def readall(data, deletelist):
    img = [0 for i in range(len(data))]
    for currIndex, filename in enumerate(data):
        if not os.path.exists(os.path.join(filename)):  # 若不存在则跳过
            deletelist[currIndex] = 1
            continue
        tmp = cv2.imread(os.path.join(filename))  # 读取图片
        if tmp is None:  # 若失败则跳过
            deletelist[currIndex] = 1
            continue
        tmp = cv2.resize(tmp, (46, 46), interpolation=cv2.INTER_CUBIC)  # 缩放图片
        img[currIndex] = tmp
    return img


def deleteall(data, deletelist):
    for index, i in enumerate(deletelist):
        if i == 1:
            try:
                delete(os.path.join(data[index]))  # 删除图片'''
            except BaseException:
                continue


def delete(filename):
    '''删除文件'''
    os.remove(filename)
    DBAPI.setDownloadFlagByFilepath(filename, DBAPI.DOWNLOAD_FLAG_REPEAT)
    print("del repeat:", filename)


def calculate(img, data, begin, end, label, deletelist, ux, uxx, vx):
    num = 0
    for currIndex in range(len(img)):  # 第一层循环 基准照片
        if not (currIndex >= begin and currIndex < end): continue  # 不属于本线程则跳过
        if deletelist[currIndex] == 1: continue  # 删除则跳过
        for currIndex2 in range(len(img)):  # 第二层循环 对比照片
            if currIndex < currIndex2:  # 排除以前比过的
                if deletelist[currIndex2] == 1: continue  # 删除则跳过
                ssim = compare_ssim(img, currIndex, currIndex2, uxlist=ux, uxxlist=uxx, vxlist=vx,
                                    multichannel=True)  # 求两张图片的相似度
                num = num + 1
                if ssim > 0.9:  # 相似度大于基准值
                    deletelist[currIndex2] = 1
        if currIndex % 10 == 0:
            deleteall(data, deletelist)  # 一边运行一边删除
        print("完成搜索", data[currIndex])
    print("process" + str(label) + " amount:" + str(num))


def deletesimilarity(pathlist):
    # 此处修改进程数 其他自动计算 不必修改
    processnum = 4

    data = pathlist  # 获取所有图片名字
    img = []
    loclength = [0 for i in range(processnum + 1)]  # 任务分割中间记录
    loc = [0 for i in range(processnum + 1)]  # 任务分割位置记录
    deletelist = Array('i', [0 for i in range(len(data))])  # 记录要删除的图片
    # deletelist=[0 for i in range(len(data))]#记录要删除的图片
    img = readall(data, deletelist)  # 读取所有图片
    ux, uxx, vx = getfeature(img)  # 获取特征
    num = len(img)
    t = []

    # 特殊算法求分割位置保证任务平均分配
    for i in range(processnum, -1, -1):
        if i == processnum:
            loclength[i] = num
        elif i == 0:
            loclength[i] = 0
        else:
            loclength[i] = int(loclength[i + 1] * (
                    (math.sqrt(1 + 8 * i * (loclength[i + 1] ** 2 + loclength[i + 1]) / 2) - 1) / (
                    math.sqrt(1 + 8 * (i + 1) * (loclength[i + 1] ** 2 + loclength[i + 1]) / 2) - 1)))
    for i in range(processnum + 1):
        loc[i] = num - loclength[processnum - i]
    print(loc)

    # 添加线程
    for i in range(processnum):
        t.append(Process(target=calculate, args=(img, data, loc[i], loc[i + 1], i, deletelist, ux, uxx, vx)))

    for i in range(processnum):
        t[i].start()
    for i in range(processnum):
        t[i].join()
    deleteall(data, deletelist)  # 删除图片

class DeRepeat:

    def __init__(self):
        self.image_urls, self.image_filepathes = DBAPI.getImageToDerepeat()
        pass

    def deRepeat(self):
        deletesimilarity(self.image_filepathes)
        for filepath in self.image_filepathes:
            DBAPI.setDownloadFlagByFilepath(filepath, DBAPI.DOWNLOAD_FLAG_NO_REPEAT)
        pass

    pass
