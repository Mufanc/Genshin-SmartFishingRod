import ctypes
import ctypes.wintypes as wintypes

import cv2
import numpy as np
import win32gui
import win32ui
from win32con import *


# noinspection PyUnresolvedReferences
class Manager(object):
    def __init__(self, class_name, window_name):
        self.hwnd = win32gui.FindWindow(class_name, window_name)
        if not self.hwnd:
            raise RuntimeError('请先开启游戏！')
        self.hwnd_dc = win32gui.GetWindowDC(self.hwnd)
        self.mfc_dc = win32ui.CreateDCFromHandle(self.hwnd_dc)
        self.save_dc = self.mfc_dc.CreateCompatibleDC()
        self.mouse_state = False  # True 按下 | False 抬起

    def get_window_rect(self):  # dpi 缩放级别会影响 win32gui.GetWindowRect，故换用此实现
        rect = wintypes.RECT()
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        ctypes.windll.dwmapi.DwmGetWindowAttribute(
            wintypes.HWND(self.hwnd),
            ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
            ctypes.byref(rect),
            ctypes.sizeof(rect)
        )
        return rect.left, rect.top, rect.right, rect.bottom

    def screencap(self):
        bitmap = win32ui.CreateBitmap()
        left, top, right, bottom = self.get_window_rect()
        width, height = right - left, bottom - top
        bitmap.CreateCompatibleBitmap(self.mfc_dc, width, height)
        self.save_dc.SelectObject(bitmap)
        self.save_dc.BitBlt((0, 0), (width, height), self.mfc_dc, (0, 0), SRCCOPY)
        ints_array = bitmap.GetBitmapBits(True)
        win32gui.DeleteObject(bitmap.GetHandle())
        img = np.frombuffer(ints_array, dtype='uint8')
        img.shape = (height, width, 4)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # BGR

    def mouse_down(self):
        if self.mouse_state:
            return
        self.mouse_state = True
        self.mouse_event(WM_LBUTTONDOWN)

    def mouse_up(self):
        if not self.mouse_state:
            return
        self.mouse_state = False
        self.mouse_event(WM_LBUTTONUP)

    def mouse_event(self, message):
        left, top, right, bottom = self.get_window_rect()
        width, height = right - left, bottom - top
        win32gui.PostMessage(self.hwnd, message, MK_LBUTTON, ((height // 2) << 16) | (width // 2))

    def __del__(self):
        self.save_dc.DeleteDC()
        self.mfc_dc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwnd_dc)
