from threading import Thread

import cv2
import numpy as np

from genshin import Manager
from overlay import Overlay

manager = Manager('UnityWndClass', '原神')
overlay = Overlay()


if __name__ == '__main__':
    def Test():
        while True:
            left, top, right, bottom = manager.get_window_rect()
            width, height = right - left, bottom - top

            image = np.zeros((height, width, 3), dtype=np.uint8)
            cv2.rectangle(image, (0, 0), (width, height), (0, 0, 255), 3)
            cv2.rectangle(image, (width*3//4, height*7//8), (width, height), (0, 255, 0), 2)
            cv2.rectangle(image, (width//2 - 20, 0), (width//2 + 20, height), (255, 0, 0), 2)
            overlay.update(image)
            overlay.follow(manager)

    Thread(target=Test).start()
    overlay.loop()
