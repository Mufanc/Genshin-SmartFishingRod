import tkinter as tk
from ctypes import wintypes

import cv2
import win32gui
from PIL import Image, ImageTk
from win32con import *


class Overlay(object):
    def __init__(self):
        root = tk.Tk()
        root.attributes('-transparentcolor', '#000000')
        root.title('Genshin Overlay')
        root.overrideredirect(True)
        self.root = root

        self.image = ImageTk.PhotoImage(Image.new('RGB', (512, 512), '#000000'))
        self.panel = tk.Label(root, image=self.image)
        self.panel.pack()

        root.lift()
        root.attributes('-topmost', True)
        # root.after_idle(root.attributes, '-topmost', True)

        self.hwnd = wintypes.HANDLE(int(root.frame(), 16)).value
        win32gui.SetWindowLong(self.hwnd, GWL_EXSTYLE, WS_EX_TRANSPARENT | WS_EX_LAYERED)
        # win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 0, LWA_ALPHA)

    def loop(self):
        self.root.mainloop()

    def follow(self, manager):
        left, top, right, bottom = manager.get_window_rect()
        width, height = right - left, bottom - top
        win32gui.MoveWindow(self.hwnd, left, top, width, height, False)

    def update(self, image):
        self.image = ImageTk.PhotoImage(
            Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        )
        self.panel.configure(image=self.image)
        self.panel.image = self.image
