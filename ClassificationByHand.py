import os
import cv2
import shutil
import URLDatabase


IMG_EXTENSIONS = [
    '.jpg', '.JPG', '.jpeg', '.JPEG',
    '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
]


def findAllImages(dataroot):
    images = []
    if (os.path.isdir(dataroot)):

        for fileOrDir in os.listdir(dataroot):
            if os.path.isdir(os.path.join(dataroot, fileOrDir)):
                findAllImages(os.path.join(dataroot, fileOrDir))

            elif any(fileOrDir.endswith(extension) for extension in IMG_EXTENSIONS):
                images.append(os.path.join(dataroot, fileOrDir))
        pass

    return images


def Imgclassification(dataroot, classcount=2, tips="image"):

    wait_classification_root = os.path.join(dataroot, "wait_classification_img")
    if not os.path.exists(wait_classification_root):
        os.mkdir(wait_classification_root)

    final_data = os.path.join(dataroot, "final_data")
    if not os.path.exists(final_data):
        os.mkdir(final_data)

    images = findAllImages(wait_classification_root)
    index = 0
    imagelength = len(images)
    print("total images: " + str(imagelength))
    for image in images:
        try:
            index += 1
            cv2.imshow(tips, cv2.imread(image))
            print("current image : " + image)
            print("num :" + str(index) + "/" + str(imagelength))

            saveFileFlag = False

            while True:
                key = cv2.waitKey(0)
                for cla in range(classcount):
                    if key == ord(str(cla)):
                        if not os.path.isdir(os.path.join(final_data, str(cla))):
                            os.makedirs(os.path.join(final_data, str(cla)))

                        shutil.copyfile(image, os.path.join(final_data, str(cla), image.split(os.path.sep)[-1]))
                        os.remove(image)  #delete after copy
                        saveFileFlag = True
                        break

                if saveFileFlag:
                    break

        except:
            os.remove(image)
            URLDatabase.updateDamageImage(image)

    nums_every_class = []
    for clscount in range(classcount):
        nums_every_class.append(
            "class" + str(clscount) + ":" + str(len(findAllImages(os.path.join(final_data, str(clscount))))))
    with open(os.path.join(final_data, "README.txt"), "w+") as f:
        f.write(str(nums_every_class))
        f.close()

    return


