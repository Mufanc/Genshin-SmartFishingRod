from queue import Queue
from threading import Thread

import cv2
import numpy as np

from genshin import Manager
from window import FishingWindow

manager = Manager('UnityWndClass', '原神')  # 使用窗口类名和标题
colors = {  # ui 颜色
    'progress': [(64, 255, 192), (67, 255, 192), (255, 204, 50)],  # 进度条的颜色
    'entity': [(255, 255, 192), ],  # 滑框和游标的颜色
}
left, right = 600, 1000
position, height = [92, 112, 132], 4  # 钓鱼进度条离窗口顶部的高度（可能有多个）、截取部分的高度


def scale2x(img):
    return cv2.resize(img, (img.shape[1] * 2, img.shape[0] * 2), interpolation=cv2.INTER_NEAREST)


def analyze(sample):
    # noinspection PyShadowingNames
    def polar(index):
        segment = sample[index-1:index+2]
        for name in colors:
            if any(np.all(segment == color) for color in colors[name]):
                return name
        return 'normal'

    smooth = [polar(i) for i in range(1, len(sample) - 1)]
    start, last, px = 0, -1, {'progress': [], 'entity': []}
    for i, val in enumerate(smooth):
        for name in colors:
            if val == name and last != name:
                start = i
            elif val != name and last == name:
                px[name].append((start, i))
        last = val

    return px['progress'], px['entity']


def action_thread():
    global state
    while True:
        if message.get() == 'exit':
            break
        state = 'pending'
        manager.click()
        state = 'idle'


def main():
    Thread(target=action_thread).start()
    window = FishingWindow()
    try:
        while True:
            images, results = [], []
            for i, y_offset in enumerate(position):
                progress = manager.screencap()[y_offset:y_offset + height, left:right]
                sample = np.average(cv2.cvtColor(progress, cv2.COLOR_BGR2RGB), axis=0)
                results.append(analyze(sample))
                images.append(progress)
            to_show = cv2.vconcat(images)
            img_height = to_show.shape[0]

            perform = False
            for progress, entity in results:
                if not len(progress):
                    continue
                for bounds in progress:
                    cv2.line(to_show, (bounds[0], img_height//2), (bounds[1], img_height//2), (46, 213, 115), 2)
                cursor = progress[-1][1] + np.average([p[1] - p[0] for p in entity])
                if len(entity) == 3:  # 发现三个分点
                    entity.sort(key=lambda r: abs(cursor-sum(r)/2))
                    x_list = []
                    for i, bounds in enumerate(entity):
                        x = sum(bounds) // 2
                        x_list.append(x)
                        color = (0, 0, 255) if i else (0, 255, 0)
                        cv2.line(to_show, (x, 0), (x, img_height), color, 2)
                    if x_list[0] < (x_list[1] + x_list[2]) / 2:
                        perform = True
                elif len(entity) == 2:  # 发现两个分点（可能滑框到达边缘）
                    width = right - left
                    entity.sort(key=lambda r: abs(cursor-sum(r)/2))
                    x_list = []
                    for i, bounds in enumerate(entity):
                        x = sum(bounds) // 2
                        x_list.append(x)
                    for i, x in enumerate(x_list):
                        color = (0, 0, 255) if i else (0, 255, 0)
                        cv2.line(to_show, (x, 0), (x, img_height), color, 2)
                        cv2.line(to_show, (x, 0), (x, img_height), color, 2)
                    if x_list[1] > width / 2 and x_list[0] < (width + x_list[1]) / 2:  # 右边缘
                        perform = True
                    elif x_list[1] < width / 2 and x_list[0] < x_list[1] / 2:  # 左边缘
                        perform = True

            if perform and state == 'idle':
                message.put('click')

            window.show(scale2x(to_show))
            window.move(*manager.get_corner())
    except KeyboardInterrupt:
        message.put('exit')
    except Exception as err:
        message.put('exit')
        raise err


if __name__ == '__main__':
    state = 'idle'
    message = Queue()
    main()
