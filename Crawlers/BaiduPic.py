import re
import requests
from db.DBOperator import DBUrl

download_pic_index = 0

IMG_EXTENSIONS = [
    '.jpg', '.JPG', '.jpeg', '.JPEG',
    '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
]


def Find(url, limit):
    List = []
    print('正在检测图片总数，请稍等.....')
    t = 0
    s = 0
    while t < 6000:
        Url = url + str(t)
        try:
            Result = requests.get(Url, timeout=7)
        except BaseException:
            t = t + 60
            continue
        else:
            result = Result.text
            pic_url = re.findall('"objURL":"(.*?)",', result, re.S)  # 先利用正则表达式找到图片url
            s += len(pic_url)
            if len(pic_url) == 0:
                break
            else:
                List.append(pic_url)
                t = t + 60
        if s > limit:
            break
    return List, s


def goToFind(keys, limit):
    for key in keys:

        url = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=' + key + '&pn='
        html_url_list, pic_count = Find(url, limit)
        html_length = str(len(html_url_list))
        dbUrl = DBUrl(key)
        for u_index, urls in enumerate(html_url_list):
            length = str(len(urls))
            for index, url in enumerate(urls):
                if not dbUrl.addURL(url):
                    print("\033[35m\r["+str(u_index+1)+"/"+html_length+"-->"+str(index+1)+"/"+length+"] URL已存在："+url+"\033[0m", end="", flush=True)
                else:
                    print("\033[35m\r[" + str(u_index + 1) + "/" + html_length + "-->" + str(
                        index + 1) + "/" + length + "] \033[0m", end="", flush=True)







if __name__ == '__main__':  # 主函数入口
    # 关键词
    # keys = ["篮球赛", "足球赛", "烧烤摊", "运动会", "毕业照"]

    # keys = ["动漫形象女生", "动漫形象男生"]
    keys = ["动漫形象阿姨", "动漫形象老师", "动漫形象领导"]

    # 下载最多不超过多少张图片
    limit = 6000

    goToFind(keys, limit)

