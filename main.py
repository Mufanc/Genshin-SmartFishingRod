from threading import Thread
from time import sleep
from time import strftime

from detector import match, clip_image, detect
from genshin import Manager
from hotkeys import HotKey
from overlay import Overlay


def timer():
    global dps
    while True:
        print(f'\r[{strftime("%H:%M:%S")}] {dps} detects per second.', end='')
        dps = 0
        sleep(1)


def ui_thread():
    global overlay
    overlay = Overlay()
    overlay.loop()


# noinspection PyUnresolvedReferences
def main():
    global dps
    Thread(target=timer, daemon=True).start()
    Thread(target=ui_thread, daemon=True).start()
    while overlay is None:
        sleep(0.1)
    last_cap = None
    HotKey(lambda idx: clip_image(last_cap, idx)).start()
    while True:
        image = manager.screencap()
        last_cap = image
        cover, groups = match(image)
        if 'button' in groups and 'hook' not in groups:
            manager.mouse_down()
            sleep(0.3)
            manager.mouse_up()
        elif 'hook' in groups:
            result = detect(image, groups['hook'], cover)
            if result is not None:
                if result:
                    manager.mouse_down()
                else:
                    manager.mouse_up()
        overlay.update(cover)
        overlay.follow(manager)
        dps += 1


if __name__ == '__main__':
    dps = 0
    manager = Manager('UnityWndClass', '原神')
    overlay = None
    main()
