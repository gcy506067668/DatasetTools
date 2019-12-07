import os
import cv2
import numpy as np
import math
from scipy.ndimage import uniform_filter, gaussian_filter
from skimage.util.dtype import dtype_range
from skimage.util.arraycrop import crop
from multiprocessing import Process, Array

from tqdm import tqdm


def getfeature(img):
    """获取图片特征"""
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


def compare_ssim(imgf, imgs, ch=-1, uxlist=None, uxxlist=None, vxlist=None, multichannel=True):
    """两张图片进行比较"""
    assert uxlist is not None
    uxf, uxs = uxlist
    uxxf, uxxs = uxxlist
    vxf, vxs = vxlist

    if multichannel:
        # loop over channels
        nch = imgf.shape[-1]
        mssim = np.empty(nch)

        for ch in range(nch):
            ch_result = compare_ssim(imgf, imgs, ch, uxlist, uxxlist, vxlist, False)
            mssim[..., ch] = ch_result
        mssim = mssim.mean()

        return mssim

    if ch >= 0:
        imgx = imgf[..., ch]
        imgy = imgs[..., ch]

    win_size = 7  # backwards compatibility

    filter_func = uniform_filter
    imgx = imgx.astype(np.float64)
    imgy = imgy.astype(np.float64)

    cov_norm = 1.0208333333333333
    # compute (weighted) means
    ux = uxf[ch]
    uy = uxs[ch]

    # compute (weighted) variances and covariances
    uxx = uxxf[ch]
    uyy = uxxs[ch]
    uxy = filter_func(imgx * imgy, size=win_size)
    vx = vxf[ch]
    vy = vxs[ch]
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
        # for index, item in enumerate(img):
        #     if item is 0 or item is None:
        #         print(data[index])

    return img


def deleteall(data, deletelist):
    for index, i in enumerate(deletelist):
        if i == 1:
            try:
                delete(os.path.join(data[index]))  # 删除图片'''
                pass
            except BaseException:
                continue
        # else:
        #     DBDownload().updateFlag(DBDownload.DOWNLOAD_FLAG_NO_SELFREPEAT, os.path.join(data[index]))


def delete(filename):
    '''删除文件'''
    os.remove(filename)
    print(" del: ", filename)


def calculate(img, data, begin, end, label, deletelist, ux, uxx, vx):
    num = 0

    for currIndex in range(len(img)):  # 第一层循环 基准照片
        if not (currIndex >= begin and currIndex < end): continue  # 不属于本线程则跳过
        if deletelist[currIndex] == 1: continue  # 删除则跳过
        for currIndex2 in range(len(img)):  # 第二层循环 对比照片
            if currIndex < currIndex2:  # 排除以前比过的
                if deletelist[currIndex2] == 1: continue  # 删除则跳过
                ssim = compare_ssim(img[currIndex], img[currIndex2], uxlist=(ux[currIndex], ux[currIndex2]),
                                    uxxlist=(uxx[currIndex], uxx[currIndex2]), vxlist=(vx[currIndex], vx[currIndex2]),
                                    multichannel=True)  # 求两张图片的相似度
                num = num + 1
                if ssim > 0.9:  # 相似度大于基准值
                    deletelist[currIndex2] = 1
        if currIndex % 10 == 0:
            deleteall(data, deletelist)  # 一边运行一边删除


def calculate2(img, data, label, deletelist, ux, uxx, vx):
    num = 0
    imgfirst, imgsecond = img
    deletelistfirst, deletelistscond = deletelist

    datafirst, datasecond = data
    uxf, uxs = ux
    uxxf, uxxs = uxx
    vxf, vxs = vx
    for currIndex in range(len(imgfirst)):  # 第一层循环 基准照片
        if deletelistfirst[currIndex] == 1: continue  # 删除则跳过

        for currIndex2 in range(len(imgsecond)):  # 第二层循环 对比照片
            if deletelistscond[currIndex2] == 1: continue  # 删除则跳过

            ssim = compare_ssim(imgfirst[currIndex], imgsecond[currIndex2], uxlist=(uxf[currIndex], uxs[currIndex2]),
                                uxxlist=(uxxf[currIndex], uxxs[currIndex2]), vxlist=(vxf[currIndex], vxs[currIndex2]),
                                multichannel=True)  # 求两张图片的相似度
            num = num + 1
            if ssim > 0.9:  # 相似度大于基准值

                deletelistscond[currIndex2] = 1


def deletesimilarity(*pathlist_list):
    for item in pathlist_list:
        if len(item) < 8:
            return
    # 此处修改进程数 其他自动计算 不必修改
    processnum = 4

    data = pathlist_list  # 获取所有图片名字

    loclength = [0 for i in range(processnum + 1)]  # 任务分割中间记录
    loc = [0 for i in range(processnum + 1)]  # 任务分割位置记录

    deletelist = []
    for i in data:
        deletelist.append(Array('i', [0 for i in range(len(i))]))  # 记录要删除的图片

    img = []
    for index, i in enumerate(data):
        img.append(readall(i, deletelist[index]))  # 读取所有图片

    ux = []
    uxx = []
    vx = []

    for i in img:
        uxtmp, uxxtmp, vxtmp = getfeature(i)  # 获取特征
        ux.append(uxtmp)
        uxx.append(uxxtmp)
        vx.append(vxtmp)

    # 处理每个列表之间的重复
    for indexfirst, first in enumerate(data):
        for indexsecond, second in enumerate(data):
            if indexfirst >= indexsecond and not len(data) == 1: continue

            num = len(img[indexfirst])

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

            pro = []
            if len(data) == 1:  # 处理自我查重
                # 添加线程
                for i in range(processnum):
                    pro.append(Process(target=calculate, args=(
                        img[0], data[0], loc[i], loc[i + 1], i, deletelist[0], ux[0], uxx[0], vx[0])))

                for i in range(processnum):
                    pro[i].start()
                for i in range(processnum):
                    pro[i].join()
            else:
                # 添加进程
                for i in range(processnum):
                    uxtmp = (ux[indexfirst][loc[i]:loc[i + 1]], ux[indexsecond])
                    uxxtmp = (uxx[indexfirst][loc[i]:loc[i + 1]], uxx[indexsecond])
                    vxtmp = (vx[indexfirst][loc[i]:loc[i + 1]], vx[indexsecond])

                    imgtmp = (img[indexfirst][loc[i]:loc[i + 1]], img[indexsecond])
                    datatmp = (data[indexfirst][loc[i]:loc[i + 1]], data[indexsecond])
                    deletelisttmp = [deletelist[indexfirst][loc[i]:loc[i + 1]], deletelist[indexsecond]]
                    # 开启进程
                    pro.append(Process(target=calculate2, args=(imgtmp, datatmp, i, deletelist, uxtmp, uxxtmp, vxtmp)))

                for i in range(processnum):
                    pro[i].start()
                for i in range(processnum):
                    pro[i].join()
                deleteall(data[indexfirst], deletelist[indexfirst])  # 删除图片
                deleteall(data[indexsecond], deletelist[indexsecond])  # 删除图片


IMG_EXTENSIONS = [
    '.jpg', '.JPG', '.jpeg', '.JPEG',
    '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
]


def is_image_file(filename):
    return any(filename.endswith(extension) for extension in IMG_EXTENSIONS)


def make_dataset(dir):
    images = []
    if not os.path.isdir(dir):
        return images
    for root, _, fnames in sorted(os.walk(dir)):
        for fname in fnames:
            if is_image_file(fname):
                path = os.path.join(root, fname)
                images.append(path)

    return images


if __name__ == '__main__':

    dirs = os.listdir("./")

    for index, item in enumerate(dirs):
        print("----------------------", end="")
        print(index, end="")
        print("----------------------")
        if index < 24:
            continue
        images = make_dataset("./" + item)
        if len(images) < 5:
            continue
        # p = Process(target=deletesimilarity, args=(images))
        # p.start
        deletesimilarity(images)

