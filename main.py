import ctypes
import sys
from threading import Thread
from time import sleep

import cv2
import numpy as np
from loguru import logger

from automaton import Genshin, Overlay, Detector, Hotkey
from automaton import alpha_mask


class Timer(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.start()

    def run(self):
        global dps
        while True:
            logger.info(f'{dps} detects per second.')
            dps = 0
            sleep(1)


def main():
    global dps
    Timer()

    game = Genshin()
    overlay = Overlay(game.hwnd)
    hotkey = Hotkey()
    detector = Detector()

    hide_ui = False
    while True:
        screen = game.screencap()
        # cv2.imshow('Debug', alpha_mask(screen[70:200, 750:850]))
        # cv2.waitKey(1)

        if key := hotkey.get():
            if key[0] == 'NUMPAD':
                if key[1]:
                    detector.clip_image(screen, key[1])
                else:  # Todo: 配置文件生成工具
                    cv2.imshow('Configuration', alpha_mask(screen))
                    cv2.waitKey(0)
            else:
                hide_ui = not hide_ui
        groups, cover = detector.match_template(screen)

        progress_found = False
        if 'hook' in groups:
            result = detector.match_progress(screen, groups['hook'], cover)
            if result is not None:
                progress_found = True
                game.mouse(result)
        if 'button' in groups and not progress_found:
            game.mouse(True)
            sleep(0.1)
            game.mouse(False)

        if hide_ui:
            cover = np.zeros(cover.shape, dtype=np.uint8)
        overlay.update(cover)
        dps += 1


if __name__ == '__main__':
    if ctypes.windll.shell32.IsUserAnAdmin():
        dps = 0
        main()
    else:  # 自动以管理员身份重启
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, __file__, None, 1)
