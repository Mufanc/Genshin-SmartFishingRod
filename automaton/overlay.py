import tkinter as tk
from ctypes import wintypes
from multiprocessing import Process, Value, Pipe
from threading import Thread

import cv2
import win32gui
from PIL import Image, ImageTk
from win32con import *

from .utils import get_window_rect


class Overlay(Process):
    def __init__(self, hwnd_game):
        super().__init__(daemon=True)
        self.receiver, self.sender = Pipe(False)
        self.hwnd_game = hwnd_game
        self._hwnd = Value('i', 0)
        self.panel = self.image = None

        self.start()

    @property
    def hwnd(self):
        return self._hwnd.value

    def run(self):
        root = tk.Tk()
        root.attributes('-transparentcolor', '#000000')
        root.title('Genshin Overlay')
        root.overrideredirect(True)

        self.image = ImageTk.PhotoImage(Image.new('RGB', (512, 512), '#000000'))
        self.panel = tk.Label(root, image=self.image)
        self.panel.pack()

        root.lift()
        root.attributes('-topmost', True)
        # root.after_idle(root.attributes, '-topmost', True)

        hwnd = wintypes.HANDLE(int(root.frame(), 16)).value
        self._hwnd.value = hwnd
        win32gui.SetWindowLong(hwnd, GWL_EXSTYLE, WS_EX_TRANSPARENT | WS_EX_LAYERED)

        Thread(target=self._update, daemon=True).start()
        root.mainloop()

    def _update(self):
        while True:
            image = self.receiver.recv()
            self.image = ImageTk.PhotoImage(
                Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            )
            self.panel.configure(image=self.image)
            self.panel.image = self.image

            left, top, right, bottom = get_window_rect(self.hwnd_game)
            width, height = right - left, bottom - top
            win32gui.MoveWindow(self.hwnd, left, top, width, height, False)

    def update(self, image):
        self.sender.send(image)
