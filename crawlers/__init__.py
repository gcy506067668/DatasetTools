# import os
# from PIL import Image
# import cv2 as cv
#
# IMG_EXTENSIONS = [
#     '.jpg', '.JPG', '.jpeg', '.JPEG',
#     '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
# ]
#
#
# def is_image_file(filename):
#     return any(filename.endswith(extension) for extension in IMG_EXTENSIONS)
#
#
# def make_dataset(dir):
#     images = []
#     assert os.path.isdir(dir), '%s is not a valid directory' % dir
#     classes = os.listdir(dir)
#     for root, _, fnames in sorted(os.walk(dir)):
#         for fname in fnames:
#             if is_image_file(fname):
#                 path = os.path.join(root, fname)
#                 images.append(path)
#     return images
#
#
# def dedamage(images):
#     for path in images:
#         if path.split("/")[-1].startswith("P000"):
#             os.remove(path)
#
#
# root_path = "/home/letmesleep/data/cartoon/cartoon_with_people_in/WebCaricature/OriginalImages"
# images = make_dataset(root_path)
# dedamage(images)