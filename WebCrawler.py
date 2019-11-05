from Crawlers import BaiduPic


class WebCrawler:

    @staticmethod
    def goToFind(keys, limit=8000):

        baidu_list = BaiduPic.goToFind(keys, limit)

