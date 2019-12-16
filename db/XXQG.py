import time

import autopy


def watch_news(num_news):
    time.sleep(2)

    # autopy.mouse.move(100, 100)  # 移动鼠标
    autopy.mouse.move(1450, 560)  #
    autopy.mouse.click()
    time.sleep(5)
    for index in range(num_news):
        autopy.mouse.smooth_move(550, 580 + (25 * index))
        autopy.mouse.click()
        time.sleep(5)

        # 打开新闻
        autopy.mouse.smooth_move(1910, 580)  # 浏览器滚轴
        autopy.mouse.click()
        time.sleep(180)

        autopy.mouse.smooth_move(1910, 900)  # 浏览器滚轴
        autopy.mouse.click()
        time.sleep(60)

        autopy.mouse.smooth_move(778, 40)  # 第三个tab 关闭点
        autopy.mouse.click()

    autopy.mouse.smooth_move(540, 40)  # 第二个tab 关闭点
    autopy.mouse.click()
    pass


def watch_video(num_video):
    time.sleep(2)

    autopy.mouse.smooth_move(710, 410)  # 电视台
    autopy.mouse.click()
    time.sleep(5)

    autopy.mouse.smooth_move(1910, 200)  # 浏览器滚轴
    autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)  # 浏览器滚轴
    autopy.mouse.smooth_move(1910, 300)  # 浏览器滚轴
    autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)  # 浏览器滚轴
    autopy.mouse.smooth_move(580, 850)  # 浏览器滚轴
    autopy.mouse.click()
    time.sleep(5)
    for index in range(num_video):
        autopy.mouse.smooth_move(600 + (index % 4 * 250), 650 + (int(index/4)*250))  # 浏览器滚轴
        autopy.mouse.click()
        time.sleep(600)

        autopy.mouse.smooth_move(1015, 40)  # 第四个tab 关闭点
        autopy.mouse.click()
        pass

    autopy.mouse.smooth_move(780, 40)  # 第三个tab 关闭点
    autopy.mouse.click()

    autopy.mouse.smooth_move(540, 40)  # 第二个tab 关闭点
    autopy.mouse.click()
    pass

watch_news(2)
watch_video(2)
watch_news(2)

