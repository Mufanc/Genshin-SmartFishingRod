import ctypes
from ctypes import wintypes
from threading import Thread

import win32con
from win32con import *

BASE_ID = 728
user32 = ctypes.windll.user32


class Hotkey(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.message = None
        self.start()

    def run(self):
        for i in range(10):
            key_id = BASE_ID + i
            user32.RegisterHotKey(None, key_id, MOD_ALT, VK_NUMPAD0 + i)
        user32.RegisterHotKey(None, BASE_ID + 10, MOD_ALT, VK_DECIMAL)  # register for "."
        try:
            msg = wintypes.MSG()
            while True:
                if user32.GetMessageA(ctypes.byref(msg), None, 0, 0):
                    if msg.message != win32con.WM_HOTKEY:
                        continue
                    for i in range(10):
                        if msg.wParam == BASE_ID + i:
                            self.message = ('NUMPAD', i)
                    if msg.wParam == BASE_ID + 10:
                        self.message = ('DECIMAL', )
        finally:
            for i in range(10):
                user32.UnregisterHotKey(None, BASE_ID + i)
            user32.UnregisterHotKey(None, BASE_ID + 10)

    def get(self):
        result, self.message = self.message, None
        return result
