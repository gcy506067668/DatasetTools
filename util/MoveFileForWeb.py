import os
import shutil



if __name__ == '__main__':
    rootpath = "/disk3/CenterDataset/WITH_PEOPLE/webimg/webimg1"
    dstpath = "/disk3/CenterDataset/NO_PEOPLE/webimg/webimg1"
    ori_file_list = os.listdir(rootpath)
    for item in ori_file_list:
        item_path = os.path.join(rootpath, item, "nopeople")
        dst_item_path = os.path.join(dstpath, item, "nopeople")
        shutil.copytree(item_path, dst_item_path)
        item_path = os.path.join(rootpath, item, "people")
        dst_item_path = os.path.join(dstpath, item, "people")
        shutil.copytree(item_path, dst_item_path)
