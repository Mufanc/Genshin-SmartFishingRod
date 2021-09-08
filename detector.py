import cv2
import yaml
import numpy as np

with open('detects/detects.yml', 'r', encoding='utf-8') as fp:
    configs = yaml.safe_load(fp)
    detects = configs['detects']
    progress = configs['progress']
font = cv2.FONT_HERSHEY_COMPLEX


def init():
    for item in detects:
        if 'template' in item:
            item['template'] = cv2.imread(f'detects/images/{item["template"]}')
        if 'convert' in item:
            item['convert'] = getattr(cv2, f'COLOR_BGR2{item["convert"].upper()}')
            if 'template' in item:
                item['template'] = cv2.cvtColor(item['template'], item['convert'])
                

def parse_rect(shape, rect):
    x1 = int(rect['left'] * shape[1])
    y1 = int(rect['top'] * shape[0])
    x2 = shape[1] - int(rect['right'] * shape[1])
    y2 = shape[0] - int(rect['bottom'] * shape[0])
    return x1, y1, x2, y2
        

def clip_image(image, index):
    if index >= len(detects):
        return
    height, width = image.shape[:2]
    item = detects[index]
    x1, y1, x2, y2 = parse_rect((height, width), item['rect'])
    clip = image[y1:y2, x1:x2]
    if 'convert' in item:  # 其实貌似可以不写这个？
        clip = cv2.cvtColor(clip, item['convert'])
    filepath = f'detects/clips/{item["name"]}.png'
    cv2.imwrite(filepath, clip)
    print(f'\nScreenshot saved to {filepath}')


def mark(image, x1, y1, x2, y2, text, color):
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
    if not text:
        return
    rect, _ = cv2.getTextSize(text, font, 0.5, 2)
    if y1 < rect[1]:
        cv2.putText(image, text, ((x1 + x2 - rect[0]) // 2, y2 + rect[1]), font, 0.5, color, 2)
    else:
        cv2.putText(image, text, ((x1 + x2 - rect[0]) // 2, y1 - rect[1]), font, 0.5, color, 2)


def match(image):  # 匹配图片
    height, width = image.shape[:2]
    cover = np.zeros((height, width, 3), dtype=np.uint8)
    groups = {}
    for i, item in enumerate(detects):
        x1, y1, x2, y2 = parse_rect((height, width), item['rect'])
        text = f'[{i}] {item["name"]}'
        if 'template' in item and 'threshold' in item:
            target = image[y1:y2, x1:x2]
            if 'convert' in item:
                target = cv2.cvtColor(target, item['convert'])
            result = cv2.matchTemplate(target, item['template'], cv2.TM_SQDIFF_NORMED)
            min_val, _, min_loc, _ = cv2.minMaxLoc(result)
            similarity = 1 - min_val
            text += f' {similarity * 100:.1f}%'
            if similarity > item['threshold']:
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
            if item['mode'] == 'match':
                if similarity > item['threshold']:
                    groups[item['name']] = (x1, y1), (width, height)
            elif item['mode'] == 'find':
                min_loc = (min_loc[0] + x1, min_loc[1] + y1)
                t_height, t_width = item['template'].shape[:2]
                mark(cover, min_loc[0], min_loc[1], min_loc[0] + t_width, min_loc[1] + t_height, text, color)
                text, color = f'[{i}]', (0, 255, 255)
                if similarity > item['threshold']:
                    groups[item['name']] = min_loc, (t_width, t_height)
            else:
                color = (255, 255, 255)
        else:
            color = (255, 0, 0)
        mark(cover, x1, y1, x2, y2, text, color)
    return cover, groups


def detect(image, grp, cover):  # 检测进度条位置
    img_height, img_width = image.shape[:2]
    center_x = grp[0][0] + grp[1][0] // 2
    center_y = grp[0][1] + grp[1][1] // 2 - int(img_height * progress['offset'])

    width = int(img_width * progress['width'])
    height = int(img_height * progress['height'])
    x1, x2 = center_x - width // 2, center_x + width // 2
    y1, y2 = center_y - height // 2, center_y + height // 2
    clip = image[y1:y2, x1:x2]

    frame_color = progress['frame-color']
    mask = np.all(clip == frame_color, axis=2)  #
    count = np.sum(mask)
    rate = count / (width * height)

    if rate > progress['threshold']:
        mark(cover, x1, y1, x2, y2, f'Progress [{count}/{width * height}]', (255, 0, 0))
        sample = np.sum(mask, axis=0)
        sp = progress['sp']
        frame, cursor = [], []
        for i, val in enumerate(sample):
            if sp[0] <= val < sp[1]:
                frame.append(i)
            elif val >= sp[1]:
                cursor.append(i)
        if frame and cursor:
            frame, cursor = [min(frame), max(frame)], [min(cursor), max(cursor)]
            mark(cover, x1 + frame[0], y1, x1 + frame[1], y2, 'Frame', (255, 0, 255))
            mark(cover, x1 + frame[0], y1, x1 + frame[1], y2, 'Frame', (255, 0, 255))
            cursor_x = sum(cursor) // 2
            if frame[0] <= cursor_x <= frame[1]:
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
            mark(cover, x1 + cursor[0], y1, x1 + cursor[1], y2, 'Cursor', color)
            return cursor_x < sum(frame) // 2  # 如果未达到位置则需要点击
    return None


init()

if __name__ == '__main__':
    print(configs)
