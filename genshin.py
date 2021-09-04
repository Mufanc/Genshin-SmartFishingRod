from time import sleep

import cv2
import numpy as np
import win32gui
import win32ui
from win32con import *


class Manager(object):
    def __init__(self, class_name, window_name):
        self.hwnd = win32gui.FindWindow(class_name, window_name)
        assert self.hwnd
        self.hwnd_dc = win32gui.GetWindowDC(self.hwnd)
        self.mfc_dc = win32ui.CreateDCFromHandle(self.hwnd_dc)
        self.save_dc = self.mfc_dc.CreateCompatibleDC()

    def get_corner(self):
        left, top, _, _ = win32gui.GetWindowRect(self.hwnd)
        return left, top

    def screencap(self):
        bitmap = win32ui.CreateBitmap()
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        width, height = right - left, bottom - top
        bitmap.CreateCompatibleBitmap(self.mfc_dc, width, height)
        self.save_dc.SelectObject(bitmap)
        self.save_dc.BitBlt((0, 0), (width, height), self.mfc_dc, (0, 0), SRCCOPY)
        # bitmap.SaveBitmapFile(save_dc, 'Test.bmp')
        ints_array = bitmap.GetBitmapBits(True)
        win32gui.DeleteObject(bitmap.GetHandle())
        img = np.frombuffer(ints_array, dtype='uint8')
        img.shape = (height, width, 4)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # BGR

    def click(self):
        win32gui.PostMessage(self.hwnd, WM_LBUTTONDOWN, MK_LBUTTON, (450 << 16) | 799)
        sleep(0.05)
        win32gui.PostMessage(self.hwnd, WM_LBUTTONUP, 0, (450 << 16) | 799)
        sleep(0.1)

    def __del__(self):
        self.save_dc.DeleteDC()
        self.mfc_dc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwnd_dc)
