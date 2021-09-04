import cv2
import win32gui


class FishingWindow(object):
    def __init__(self):
        self.name = 'Fishing'
        self.classname = 'Main HighGUI class'
        self.hwnd = 0

    def show(self, img):
        cv2.imshow(self.name, img)
        cv2.waitKey(1)
        if not self.hwnd:
            self.hwnd = win32gui.FindWindow(self.classname, self.name)

    def move(self, x, y):
        if not self.hwnd:
            return
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        width, height = right - left, bottom - top
        win32gui.MoveWindow(self.hwnd, x - 8, y - height + 5, width, height, False)
