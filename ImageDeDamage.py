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
    image_nums = str(len(images))
    for cindex, image_path in enumerate(images):

        try:
            if cv.imread(image_path) is None:
                os.remove(image_path)
                print("\033[35m\r" + str(cindex) + "/" + image_nums + "  移除CV损坏图片:"+image_path+"\033[0m", end="", flush=True)
                DBAPI.setDownloadFlag(urls[cindex], DBAPI.DOWNLOAD_FLAG_DAMAGE)
                continue

            img = Image.open(image_path)  # 读取图片
            if img is None:
                os.remove(image_path)
                DBAPI.setDownloadFlag(urls[cindex], DBAPI.DOWNLOAD_FLAG_DAMAGE)
                print("\033[35m\r" + str(cindex) + "/" + image_nums + "  移除PIL损坏图片:"+image_path+"\033[0m", end="", flush=True)
                continue
        except:
            if os.path.isfile(image_path):
                os.remove(image_path)
            DBAPI.setDownloadFlag(urls[cindex], DBAPI.DOWNLOAD_FLAG_DAMAGE)
            print("\033[35m\r" + str(cindex) + "/" + image_nums + "  移除损坏图片:"+image_path+"\033[0m", end="", flush=True)
        else:
            DBAPI.setDownloadFlag(urls[cindex], DBAPI.DOWNLOAD_FLAG_NO_DAMAGE)
            print("\033[35m\r" + str(cindex+1) + "/" + image_nums + "\033[0m", end="", flush=True)
            pass

