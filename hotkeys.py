import ctypes
from ctypes import wintypes
from threading import Thread

import win32con
from win32con import *

base = 728  # 随意选一个数（起始热键 ID）
user32 = ctypes.windll.user32


class HotKey(Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.daemon = True

    def run(self):
        for i in range(10):
            key_id = base + i
            user32.RegisterHotKey(None, key_id, MOD_ALT, VK_NUMPAD0 + i)
        try:
            msg = wintypes.MSG()
            while True:
                if user32.GetMessageA(ctypes.byref(msg), None, 0, 0):
                    if msg.message != win32con.WM_HOTKEY:
                        continue
                    for i in range(10):
                        if msg.wParam == base + i:
                            self.callback(i)
        finally:
            for i in range(10):
                user32.UnregisterHotKey(None, base + i)
