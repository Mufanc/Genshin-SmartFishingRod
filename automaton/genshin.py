import ctypes
import ctypes.wintypes as wintypes
from multiprocessing import Process, Pipe

import numpy as np
import win32api
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

    def _get_clip_rect(self):
        # 获取游戏所在显示器信息
        vw_rect = win32gui.GetWindowRect(self.hwnd)
        vw_center = (vw_rect[0] + vw_rect[2]) // 2, (vw_rect[1] + vw_rect[3]) // 2
        h_monitor = win32api.MonitorFromPoint(vw_center, MONITOR_DEFAULTTONULL)
        if h_monitor is None:
            return None
        v_monitor = win32api.GetMonitorInfo(h_monitor)['Monitor']

        # 获取窗口真实坐标
        rw_rect = wintypes.RECT()
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        ctypes.windll.dwmapi.DwmGetWindowAttribute(
            wintypes.HWND(self.hwnd),
            ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
            ctypes.byref(rw_rect),
            ctypes.sizeof(rw_rect)
        )

        # 计算缩放比例
        rw_width = rw_rect.right - rw_rect.left
        vw_width = (lambda r: r[2] - r[0])(win32gui.GetWindowRect(self.hwnd))
        dpi_scale = rw_width / vw_width

        # 得到用户区域左上角坐标
        v_x1, v_y1 = win32gui.ClientToScreen(self.hwnd, (0, 0))
        _, _, vc_width, vc_height = win32gui.GetClientRect(self.hwnd)
        r_x1 = v_monitor[0] + (v_x1 - v_monitor[0]) * dpi_scale
        r_y1 = v_monitor[1] + (v_y1 - v_monitor[1]) * dpi_scale
        rc_width, rc_height = vc_width * dpi_scale, vc_height * dpi_scale

        # 计算坐标偏移
        rx_offset, ry_offset = r_x1 - rw_rect.left, r_y1 - rw_rect.top

        return map(round, (rx_offset, ry_offset, rc_width, rc_height))

    def screencap(self):
        return self.receiver.recv()

    def run(self):
        hwnd_dc = win32gui.GetWindowDC(self.hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        while True:
            # 屏幕截图
            bitmap = win32ui.CreateBitmap()

            rect = self._get_clip_rect()
            if rect is None:
                continue
            x1, y1, width, height = rect

            bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(bitmap)
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (x1, y1), SRCCOPY)
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
