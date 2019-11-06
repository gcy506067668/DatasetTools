import os
import requests
from db.URLDatabase import DBAPI
from concurrent.futures import ThreadPoolExecutor


class Download:

    def __init__(self, savepath):
        self.imageToDownload = DBAPI.getDownload()
        self.IMG_EXTENSIONS = [
            '.jpg', '.JPG', '.jpeg', '.JPEG',
            '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
        ]
        self.savepath = savepath
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        pass

    def downloadByKeys(self, keys, savepath):
        image_urls = DBAPI.selectByLabels(keys)
        for index, url in enumerate(image_urls):
            self._dowmload(url, savepath, index)
        pass

    def download(self, urls=None):
        if not urls:
            for index, url in enumerate(self.imageToDownload):
                self._dowmload(url, self.savepath, index)
        else:
            for index, url in enumerate(urls):
                self._dowmload(url, self.savepath, index)
        pass

    def __download(self, urls, t_num):
        length = str(len(urls))
        for index, url in enumerate(urls):
            self._dowmload(url, os.path.join(self.savepath, t_num), index)
            print('\033[35m\rThread ' + t_num + ':[' + str(index + 1) + '/' + length + '] 正在下载图片，图片地址:' + str(
                url) + "\033[0m", end='', flush=True)
        pass

    def downloadMulThread(self, thread_num=1):
        cut_result = []
        urls = self.imageToDownload
        length = int(len(urls) / thread_num)
        for index in range(thread_num):
            if index != thread_num - 1:
                cut_result.append(urls[index * length:(index + 1) * length])
            else:
                cut_result.append(urls[index * length:len(urls)])
        with ThreadPoolExecutor(thread_num) as executor:
            for index, t_item in enumerate(cut_result):
                executor.submit(self.__download, urls=t_item, t_num=str(index))

    def _dowmload(self, url, savepath, id):
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        try:
            if url is not None:
                pic = requests.get(url, timeout=3)

        except BaseException:
            DBAPI.downloadFaild(url)
            print('\033[31m\r错误，当前图片无法下载：\033[0m'+url)
            return False, ""

        else:
            filetail = "." + url.split(".")[-1]

            if any(filetail == extension for extension in self.IMG_EXTENSIONS):
                download_file_path = 'pic_' + str(id) + filetail
            else:

                for extension in self.IMG_EXTENSIONS:
                    if extension in url:
                        download_file_path = 'pic_' + str(id) + extension
                        break
                    else:
                        download_file_path = "unknow_" + str(id) + ".jpg"

            download_file_path = os.path.join(savepath, download_file_path)
            fp = open(download_file_path, 'wb')
            fp.write(pic.content)
            fp.close()
            DBAPI.downloadSuccess(url, download_file_path)
            return True, download_file_path
