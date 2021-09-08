import cv2
from genshin import Manager

manager = Manager('UnityWndClass', '原神')
while True:
    screen = manager.screencap()
    cv2.imshow('Test Screencap', screen)
    cv2.waitKey(1)