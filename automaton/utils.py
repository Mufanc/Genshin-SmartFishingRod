import ctypes
import ctypes.wintypes as wintypes

import cv2
import numpy as np

from configs import configs, models


# dpi 缩放级别会影响 win32gui.GetWindowRect，故换用此实现
def get_window_rect(hwnd):
    rect = wintypes.RECT()
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        wintypes.HWND(hwnd),
        ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
        ctypes.byref(rect),
        ctypes.sizeof(rect)
    )
    return rect.left, rect.top, rect.right, rect.bottom


def choose_model(screen):
    height, width = screen.shape[:2]
    ratio = height / width
    best = min(models.keys(), key=lambda key: abs(ratio - key))
    if len(np.unique(screen[..., 3])) == 1:
        model = 'rgb'
    else:
        model = 'alpha'
    return models[best][model]


def _alpha_mask(bgra):  # Fast
    if configs['use-alpha']:
        image, alpha = bgra[..., :3] >> 4, bgra[..., 3] >> 4
        np.multiply(image[..., 0], alpha, out=image[..., 0])
        np.multiply(image[..., 1], alpha, out=image[..., 1])
        np.multiply(image[..., 2], alpha, out=image[..., 2])
    else:
        image = bgra[..., :3]
    return image


def alpha_mask(bgra):  # 尝试使用 Alpha 层作为蒙版
    # image = _alpha_mask(bgra)
    if configs['use-alpha']:
        alpha = bgra[..., 3]
        image = bgra[..., :3].astype(np.uint16)
        for ch in range(3):
            image[..., ch] *= alpha
        image = (image // 255).astype(np.uint8)
    else:
        image = bgra[..., :3]

    if configs['gray-only']:
        image = cv2.cvtColor(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)

    return image
