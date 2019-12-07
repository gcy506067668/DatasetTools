import os

from pypinyin import lazy_pinyin, Style

def getPinyin(text):
    p = lazy_pinyin(text)
    res = ""
    for pinyin in p:
        res += pinyin
    return res



IMG_EXTENSIONS = [
    '.jpg', '.JPG', '.jpeg', '.JPEG',
    '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
]


def is_image_file(filename):
    return any(filename.endswith(extension) for extension in IMG_EXTENSIONS)







def make_dataset(dir):
    images = []
    assert os.path.isdir(dir), '%s is not a valid directory' % dir
    for root, _, fnames in sorted(os.walk(dir)):
        for fname in fnames:
            if is_image_file(fname):
                path = os.path.join(root, fname)
                images.append(path)


    return images




if __name__ == '__main__':
    rootpath = "./"
    ori_file_list = []
    ori_file_list = os.listdir(rootpath)
    for item in ori_file_list:
        os.rename(item, getPinyin(item))
