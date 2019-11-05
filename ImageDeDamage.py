import os
from PIL import Image
from db.URLDatabase import DBAPI
import cv2 as cv



def clean():
    image_dict = DBAPI.getImageToDeDamage()
    images = []
    urls = []
    for item in image_dict:
        images.append(str(item["d_filepath"], encoding='utf8'))
        urls.append(str(item["d_url"],encoding='utf8'))
    for cindex, image_path in enumerate(images):
        try:
            if cv.imread(image_path) is None:
                os.remove(image_path)
                print("移除CV损坏图片:", image_path)  # 若失败则跳过
                DBAPI.setDownloadFlag(urls[cindex], DBAPI.DOWNLOAD_FLAG_DAMAGE)
                continue

            img = Image.open(image_path)  # 读取图片
            if img is None:
                os.remove(image_path)
                DBAPI.setDownloadFlag(urls[cindex], DBAPI.DOWNLOAD_FLAG_DAMAGE)
                print("移除PIL损坏图片::", image_path)
                continue
        except:
            if os.path.isfile(image_path):
                os.remove(image_path)
            DBAPI.setDownloadFlag(urls[cindex], DBAPI.DOWNLOAD_FLAG_DAMAGE)
            print("移除损坏图片:", image_path)
        else:
            DBAPI.setDownloadFlag(urls[cindex], DBAPI.DOWNLOAD_FLAG_NO_DAMAGE)
            pass

