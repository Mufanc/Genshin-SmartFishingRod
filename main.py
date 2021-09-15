import ctypes
import multiprocessing
import sys
from threading import Thread
from time import sleep

import cv2
import numpy as np
from loguru import logger

from automaton import Genshin, Overlay, Detector, Hotkey
from automaton import alpha_mask, choose_model


class Timer(Thread):
    def __init__(self, game):
        super().__init__(daemon=True)
        self.game = game
        self.start()

    def run(self):
        global dps
        while True:
            logger.info(f'{dps} detects per second.')
            dps = 0
            sleep(1)


def main():
    global dps

    game = Genshin()
    overlay = Overlay(game.hwnd)
    hotkey = Hotkey()

    model_name = choose_model(game.screencap())
    logger.info(f'Loading module "{model_name}"')
    detector = Detector(model_name)

    Timer(game)
    hide_ui = False
    while True:
        screen = game.screencap()
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

        if key := hotkey.get():
            if key[0] == 'NUMPAD':
                if key[1]:
                    detector.clip_image(screen, key[1])
                else:
                    image = cv2.resize(alpha_mask(screen), cover.shape[1::-1], interpolation=cv2.INTER_NEAREST)
                    cv2.imshow('Configuration', cv2.add(image, cover))
                    cv2.waitKey(0)
            else:
                hide_ui = not hide_ui

        if hide_ui:
            cover = np.zeros(cover.shape, dtype=np.uint8)
        overlay.update(cover)
        dps += 1


if __name__ == '__main__':
    multiprocessing.freeze_support()  # 为了 pyinstaller 正常打包
    if ctypes.windll.shell32.IsUserAnAdmin():
        dps = 0
        main()
    else:  # 自动以管理员身份重启
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, __file__, None, 1)
