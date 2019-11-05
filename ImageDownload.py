import os
import requests
from db.URLDatabase import DBAPI


class Download:

    def __init__(self):
        self.imageToDownload = DBAPI.getDownload()
        self.IMG_EXTENSIONS = [
            '.jpg', '.JPG', '.jpeg', '.JPEG',
            '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
        ]
        pass

    def downloadByKeys(self, keys, savepath):
        image_urls = DBAPI.selectByLabels(keys)
        for index, url in enumerate(image_urls):
            self._dowmload(url, savepath, index)
        pass

    def download(self, savepath):
        for index, url in enumerate(self.imageToDownload):
            self._dowmload(url, savepath, index)
        pass

    def _dowmload(self, url, savepath, id):
        print('正在下载图片，图片地址:' + str(url))
        try:
            if url is not None:
                pic = requests.get(url, timeout=7)

        except BaseException:
            DBAPI.downloadFaild(url)
            print('错误，当前图片无法下载')
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
