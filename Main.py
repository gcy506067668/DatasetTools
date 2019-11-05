from ImageDeDamage import clean
from ImageDeRepeat import DeRepeat
from ImageDownload import Download
from WebCrawler import WebCrawler
import os

from db.URLDatabase import DBAPI


def mkdir(path):
    if not os.path.isdir(path):
        mkdir(os.path.split(path)[0])
    else:
        return
    os.mkdir(path)


if __name__ == '__main__':
    savepath = "/home/letmesleep/data/cartoon/cartoon_with_people_in/baidu_web_cw"
    mkdir(savepath)

    # key_words = ['夜市', '集贸市场','观众','婚礼现场']
    # key_words = ['庙会']
    # key_words = ['习大大与彭妈妈', '习近平主席']
    # key_words = ['习大大']
    # key_words = ['特朗普与伊万卡']
    # key_words = ['特朗普参会']
    #20191103
    # key_words = ['卡通脸', '漫画脸', '动漫古风']
    # key_words = ['漫画男人形象', '漫画女人形象', '漫画小孩形象']
    key_words = ['漫画', '']


    limit = 8000

    WebCrawler.goToFind(key_words, limit)

    Download().download(savepath)

    clean()

    DeRepeat().deRepeat()

    # Download().downloadByKeys(key_words, savepath)
    Download().download(savepath)

