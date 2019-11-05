import re
import requests
from urllib import error
from bs4 import BeautifulSoup
import os

download_pic_index = 0

IMG_EXTENSIONS = [
    '.jpg', '.JPG', '.jpeg', '.JPEG',
    '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
]


def Find(url):
    List = []
    print('正在检测图片总数，请稍等.....')
    t = 101
    s = 0
    while t < 1000:
        Url = url + str(t)
        try:
            Result = requests.get(Url, timeout=7)
        except BaseException:
            t = t + 1
            continue
        else:
            result = Result.text
            pic_url = re.findall('srcset="(.*?)"', result, re.S)  # 先利用正则表达式找到图片url
            s += len(pic_url)
            if len(pic_url) == 0:
                break
            else:
                List.append(pic_url)
                t = t + 1
    return List, s


def dowmloadPicture(url_list, savepath, limit):
    global download_pic_index

    if not os.path.exists(savepath):
        os.mkdir(savepath)

    for eachhtml in url_list:
        for picurl in eachhtml:

            print('正在下载第' + str(download_pic_index + 1) + '张图片，图片地址:' + str(picurl))
            try:
                if picurl is not None:
                    pic = requests.get(picurl, timeout=7)
                else:
                    continue
            except BaseException:
                print('错误，当前图片无法下载')
                continue
            else:
                filetail = "." + picurl.split(".")[-1]

                if any(filetail == extension for extension in IMG_EXTENSIONS):
                    download_file_path = 'pic_' + str(download_pic_index) + filetail
                else:
                    download_file_path = 'pic_' + str(download_pic_index) + '.' + "jpg"

                download_file_path = os.path.join(savepath, download_file_path)
                fp = open(download_file_path, 'wb')
                fp.write(pic.content)
                fp.close()
                download_pic_index += 1
                if download_pic_index >= limit:
                    return


def goToFind(savepath, limit):
    url = 'https://safebooru.donmai.us/posts?page='
    url_list, pic_count = Find(url)
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    dowmloadPicture(url_list, os.path.join(savepath), limit)


if __name__ == '__main__':  # 主函数入口
    # https://safebooru.donmai.us/posts?page=2
    # 文件保存位置
    savepath = "/media/letmesleep/LENOVO/datasets/cartoon_dataset"

    #下载最多不超过多少张图片
    limit = 30000

    goToFind(savepath, limit)

    print("total " + str(download_pic_index) + " pictures")

