import os
import shutil
import cv2 as cv
from skimage.measure import compare_ssim
from tqdm import tqdm


def compareKeyFrame(frame1, frame2):
    return compare_ssim(frame1, frame2, multichannel=True)

    pass


def compareVideoFrame(video_path1, video_path2):
    cap1 = cv.VideoCapture(video_path1)

    VIDEO1_FPS = cap1.get(cv.CAP_PROP_FPS)
    VIDEO1_WIDTH = cap1.get(cv.CAP_PROP_FRAME_WIDTH)
    VIDEO1_HEIGHT = cap1.get(cv.CAP_PROP_FRAME_HEIGHT)
    VIDEO1_FRAME_COUNT = cap1.get(cv.CAP_PROP_FRAME_COUNT)

    VIDEO1_TOTAL_TIME = VIDEO1_FRAME_COUNT / VIDEO1_FPS

    cap2 = cv.VideoCapture(video_path2)
    VIDEO2_FPS = cap2.get(cv.CAP_PROP_FPS)
    VIDEO2_WIDTH = cap2.get(cv.CAP_PROP_FRAME_WIDTH)
    VIDEO2_HEIGHT = cap2.get(cv.CAP_PROP_FRAME_HEIGHT)
    VIDEO2_FRAME_COUNT = cap2.get(cv.CAP_PROP_FRAME_COUNT)

    VIDEO2_TOTAL_TIME = VIDEO2_FRAME_COUNT / VIDEO2_FPS

    if VIDEO1_WIDTH != VIDEO2_WIDTH or VIDEO1_HEIGHT != VIDEO2_HEIGHT:
        return False

    if abs(VIDEO1_TOTAL_TIME - VIDEO2_TOTAL_TIME) > 10:
        return False

    frame_count = 0
    key_frames = []
    for index in range(10):
        if index * (int(VIDEO1_FPS / 2)) < VIDEO1_FRAME_COUNT or index * (int(VIDEO2_FPS / 2)) < VIDEO2_FRAME_COUNT:
            key_frames.append(index * (int(VIDEO1_FPS / 2)))
        else:
            break
    score = 0
    while cap1.isOpened() or cap2.isOpened():
        suc1, frame1 = cap1.read()
        suc2, frame2 = cap2.read()
        if frame_count in key_frames:
            single_score = compareKeyFrame(frame1, frame2)
            score += single_score
        if frame_count > key_frames[len(key_frames) - 1]:
            break

        frame_count += 1

    score_avg = score / len(key_frames)
    cap1.release()
    cap2.release()
    print('\nscore_avg: ', score_avg)
    if score_avg > 0.5:
        return True
    else:
        return False


VIDEO_EXTENSIONS = [
    'mpg', 'mp4'
]


def is_video_file(filename):
    return any(filename.endswith(extension) for extension in VIDEO_EXTENSIONS)


def make_dataset(dir):
    videos = []
    assert os.path.isdir(dir), '%s is not a valid directory' % dir
    for root, _, fnames in sorted(os.walk(dir)):
        for fname in fnames:
            if is_video_file(fname):
                path = os.path.join(root, fname)
                videos.append(path)
    return videos


def findSourceVideo(Q_path, K_paths):
    Q_video_list = []
    K_video_list = []

    if isinstance(Q_path, list):
        for item in Q_path:
            Q_video_list.extend(make_dataset(item))
    else:
        Q_video_list.extend(make_dataset(Q_path))

    if isinstance(K_paths, list):
        for item in K_paths:
            K_video_list.extend(make_dataset(item))

    with open("q_to_k.txt", "w+") as f:
        for q_item in tqdm(Q_video_list):
            for k_item in K_video_list:
                if compareVideoFrame(q_item, k_item):
                    f.write(q_item)
                    f.write(":")
                    f.write(k_item)
                    f.write("\n")
                    print(" find source video:\n" + "q:" + q_item + "\n" + "k:" + k_item)
                    break
    pass


def copyTargetVideoFile():
    q_and_k_dict = {}
    with open("q_to_k.txt", "r") as f:
        while True:
            line = f.readline()
            if line:
                line = line.replace("\n", "")
                q_and_k = line.split(":")
                if len(q_and_k) == 2:
                    q_video = q_and_k[0]
                    k_video = q_and_k[1]
                    q_and_k_dict[q_video] = k_video
            else:
                break

    print(q_and_k_dict)
    pass


if __name__ == '__main__':
    Q_path = ['/home/letmesleep/data/test/q_folder']

    K_paths = ['/home/letmesleep/data/test/k_folder/k1',
               '/home/letmesleep/data/test/k_folder/k2',
               '/home/letmesleep/data/test/k_folder/k3'
               ]

    findSourceVideo(Q_path, K_paths)

    copyTargetVideoFile()
