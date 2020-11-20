from crawlers.icrawler import Crawler

if __name__ == '__main__':
    savepath = "/home/letmesleep/data/demo"

    key = "特朗普"
    # or
    # key = ["特朗普", "川建国"]

    # baidu - 300   bing - 300  google - 300  --> total-900
    max_num = 300
    Crawler().findPic(key, savepath, max_num)
