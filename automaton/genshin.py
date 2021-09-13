from multiprocessing import Process, Pipe
from time import sleep

import numpy as np
import win32gui
import win32ui
from win32con import *

from configs import configs
from .utils import get_window_rect


class Genshin(Process):
    def __init__(self):
        super().__init__(daemon=True)

        self.hwnd = win32gui.FindWindow(*configs['game-window'])
        if not self.hwnd:
            raise RuntimeError('未检测到游戏窗口，请先启动游戏或检查配置文件是否正确！')

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
            bgra = np.frombuffer(ints_array, dtype=np.uint8)
            bgra.shape = (height, width, 4)

            if configs['use-alpha']:  # Todo: 只对待检测区域进行透明通道混合，以提高效率
                image, alpha = bgra[..., :3] >> 4, bgra[..., 3] >> 4
                np.multiply(image[..., 0], alpha, out=image[..., 0])
                np.multiply(image[..., 1], alpha, out=image[..., 1])
                np.multiply(image[..., 2], alpha, out=image[..., 2])
            else:
                image = bgra[..., :3]

            if clip := configs['window-clip'] is not None:
                # clip: [ left, top, right, bottom ]
                image = image[clip[1]:clip[3], clip[0]:clip[2]]

            self.sender.send(image)

    def mouse(self, state):
        left, top, right, bottom = get_window_rect(self.hwnd)
        width, height = right - left, bottom - top
        message = WM_LBUTTONDOWN if state else WM_LBUTTONUP
        win32gui.PostMessage(self.hwnd, message, MK_LBUTTON, ((height // 2) << 16) | (width // 2))
