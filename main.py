import ctypes
import sys
import cv2
from threading import Thread
from time import sleep
from time import strftime

from detector import match, clip_image, detect
from genshin import Manager
from hotkeys import HotKey
from overlay import Overlay


def mark_dps(cover):
    text, font = f'dps:{last_dps}', cv2.FONT_HERSHEY_COMPLEX
    rect, _ = cv2.getTextSize(text, font, 0.7, 2)
    color = (0, 255, 0) if last_dps > 10 else (0, 0, 255)
    cv2.putText(cover, text, (0, rect[1]), font, 0.7, color, 2)


def timer():
    global dps, last_dps
    while True:
        print(f'\r[{strftime("%H:%M:%S")}] {dps} detects per second.', end='')
        last_dps, dps = dps, 0
        sleep(1)


def ui_thread():
    global overlay
    overlay = Overlay()
    overlay.loop()


# noinspection PyUnresolvedReferences
def main():
    global dps
    Thread(target=timer, daemon=True).start()
    Thread(target=ui_thread, daemon=True).start()
    while overlay is None:
        sleep(1)
    last_cap = None
    HotKey(overlay, lambda idx: clip_image(last_cap, idx)).start()
    while True:
        image, alpha = manager.screencap()
        last_cap = image
        cover, groups = match(image)
        progress = False  # 标记进度条
        if 'hook' in groups:
            result = detect(image, groups['hook'], cover)
            if result is not None:
                progress = True
                if result:
                    manager.mouse_down()
                else:
                    manager.mouse_up()
        if 'button' in groups and not progress:
            manager.mouse_press(0.3)
        mark_dps(cover)
        overlay.update(cover)
        overlay.follow(manager)
        dps += 1


if __name__ == '__main__':
    if ctypes.windll.shell32.IsUserAnAdmin():
        dps, last_dps = 0, 0
        manager = Manager('UnityWndClass', '原神')
        overlay = None
        main()
    else:  # 自动以管理员身份重启
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, __file__, None, 1)
