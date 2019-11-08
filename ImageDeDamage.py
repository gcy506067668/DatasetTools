import os
from PIL import Image
from db.DBOperator import DBDownload
import cv2 as cv



def clean():
    db_download_instance = DBDownload()
    images = db_download_instance.findAllToDeDamage()
    print(len(images))
    image_nums = str(len(images))
    for cindex, image_path in enumerate(images):

        try:
            if cv.imread(image_path) is None:
                os.remove(image_path)
                print("\033[35m\r" + str(cindex) + "/" + image_nums + "  移除CV损坏图片:"+image_path+"\033[0m")
                db_download_instance.updateFlag(DBDownload.DOWNLOAD_FLAG_DAMAGE, image_path)
                continue

            img = Image.open(image_path)  # 读取图片
            if img is None:
                os.remove(image_path)
                db_download_instance.updateFlag(DBDownload.DOWNLOAD_FLAG_DAMAGE, image_path)
                print("\033[35m\r" + str(cindex) + "/" + image_nums + "  移除PIL损坏图片:"+image_path+"\033[0m")
                continue
        except:
            if os.path.isfile(image_path):
                os.remove(image_path)
            db_download_instance.updateFlag(DBDownload.DOWNLOAD_FLAG_DAMAGE, image_path)
            print("\033[35m\r" + str(cindex) + "/" + image_nums + "  移除损坏图片:"+image_path+"\033[0m")
        else:
            db_download_instance.updateFlag(DBDownload.DOWNLOAD_FLAG_NODAMAGE, image_path)
            print("\033[35m\r" + str(cindex+1) + "/" + image_nums + "\033[0m", end="", flush=True)
            pass

