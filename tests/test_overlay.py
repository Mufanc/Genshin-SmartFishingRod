from threading import Thread

import cv2

from genshin import Manager
from overlay import Overlay

manager = Manager('UnityWndClass', '原神')
overlay = Overlay()


if __name__ == '__main__':
    def Test():
        while True:
            overlay.update(manager.screencap())
            cv2.waitKey(1)

    Thread(target=Test).start()
    overlay.loop()
