import os
import requests
from db.DBOperator import DBDownload
from db.DBOperator import DBUrl
from concurrent.futures import ThreadPoolExecutor


class Download:

    def __init__(self, savepath):
        self.DBAPI = DBDownload()
        self.DBURL = DBUrl()
        self.imageToDownload = DBUrl().findAllToDownload()
        self.IMG_EXTENSIONS = [
            '.jpg', '.JPG', '.jpeg', '.JPEG',
            '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
        ]
        self.savepath = savepath
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        pass

    def __download(self, urls, t_num):
        try:
            length = str(len(urls))
            for index, url in enumerate(urls):

                i_savepath = self.savepath + "/" + str(url["u_label"], encoding='utf8')
                if not os.path.exists(self.savepath):
                    os.mkdir(self.savepath)

                self._dowmload(str(url["u_url"], encoding='utf8'), i_savepath + "/", str(url["u_id"]),
                               label=str(url["u_label"], encoding='utf8'))

                print('\033[35m\rThread ' + t_num + ':[' + str(index + 1) + '/' + length + '] 正在下载图片，图片地址:' +
                      str(url["u_url"], encoding='utf8') + "\033[0m", end='', flush=True)
        except Exception as err:
            print("----------------------------------")
            print(err)
        pass

    def downloadMulThread(self, thread_num=1):
        cut_result = []
        urls = self.imageToDownload
        self.__download(urls=urls, t_num=str(0))
        # length = int(len(urls) / thread_num)
        # for index in range(thread_num):
        #     if index != thread_num - 1:
        #         cut_result.append(urls[index * length:(index + 1) * length])
        #     else:
        #         cut_result.append(urls[index * length:len(urls)])
        # with ThreadPoolExecutor(thread_num) as executor:
        #     for index, t_item in enumerate(cut_result):
        #         executor.submit(self.__download, urls=t_item, t_num=str(index))


    def _dowmload(self, url, savepath, id, label=""):

        if not os.path.exists(savepath):
            os.mkdir(savepath)
        try:
            if url is not None:
                pic = requests.get(url, timeout=3)

        except BaseException:
            self.DBURL.updateFlag(url, DBUrl.URL_FLAG_DOWNLOAD_ERROR)
            print('\033[31m\r错误，当前图片无法下载：\033[0m' + url)
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
            self.DBAPI.addDownload(url, download_file_path, label)
            self.DBURL.updateFlag(url, DBUrl.URL_FLAG_DOWNLOAD_SUCCESS)
            return True, download_file_path

class Downloader:

    def __init__(self, savepath, data):
        self.savepath = savepath
        self.data = data
        pass

    def download(self):
        pass
