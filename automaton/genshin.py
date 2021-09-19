import subprocess as sp
from multiprocessing import Process, Pipe
from time import sleep

import numpy as np
import win32gui
import win32ui
from loguru import logger
from win32con import *

from configs import configs
from .utils import get_window_rect


class Genshin(Process):
    def __init__(self):
        super().__init__(daemon=True)

        if hwnd := win32gui.FindWindow(*configs['game-window']):
            rect = get_window_rect(hwnd)
            if [rect[2] - rect[0], rect[3] - rect[1]] != configs['window-size']:
                logger.error(f'游戏窗口与预设大小不匹配，请检查窗口大小是否为 {configs["window-size"]} 以及游戏进程是否带有 -popupwindow 参数')
                raise AttributeError(f'游戏窗口大小与预设大小不匹配！')
            else:
                self.hwnd = hwnd
        else:
            logger.info('启动游戏中...')
            sp.Popen(
                [configs['game-executable'], '-screen-width', '1600', '-screen-height', '900', '-popupwindow'],
                shell=True
            )

            for i in range(60):
                self.hwnd = win32gui.FindWindow(*configs['game-window'])
                if not self.hwnd:
                    sleep(1)
                else:
                    sleep(10)
                    break
            else:
                raise RuntimeError('长时间未检测到游戏窗口，请先启动游戏或检查配置文件是否正确！')

        self.receiver, self.sender = Pipe(False)
        self.start()

    def screencap(self):
        return self.receiver.recv()

    def run(self):
        hwnd_dc = win32gui.GetWindowDC(self.hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        while True:
            # 屏幕截图
            bitmap = win32ui.CreateBitmap()
            left, top, right, bottom = get_window_rect(self.hwnd)
            width, height = right - left, bottom - top
            bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(bitmap)
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), SRCCOPY)
            ints_array = bitmap.GetBitmapBits(True)
            win32gui.DeleteObject(bitmap.GetHandle())
            image = np.frombuffer(ints_array, dtype=np.uint8)
            image.shape = (height, width, 4)

            self.sender.send(image)

    def mouse(self, state):
        left, top, right, bottom = get_window_rect(self.hwnd)
        width, height = right - left, bottom - top
        message = WM_LBUTTONDOWN if state else WM_LBUTTONUP
        win32gui.PostMessage(self.hwnd, message, MK_LBUTTON, ((height // 2) << 16) | (width // 2))
