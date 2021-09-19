import cv2
import numpy as np
import yaml
from loguru import logger

from configs import configs
from .utils import alpha_mask

COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_MAGENTA = (255, 0, 255)


class Detector(object):
    def __init__(self, model_name):
        self.font = cv2.FONT_HERSHEY_COMPLEX
        self.model_name = model_name
        filepath = f'detects/{self.model_name}/detects.yml'

        with open(filepath, 'r', encoding='utf-8') as fp:
            self.configs = yaml.safe_load(fp)

        for item in self.configs['templates']:
            if 'template' not in item:
                continue
            item['template'] = cv2.imread(f'detects/{self.model_name}/images/{item["template"]}')

    @staticmethod
    def parse_rect(shape, rect):
        x1 = int(rect['left'] * shape[1])
        y1 = int(rect['top'] * shape[0])
        x2 = shape[1] - int(rect['right'] * shape[1])
        y2 = shape[0] - int(rect['bottom'] * shape[0])
        return x1, y1, x2, y2

    def clip_image(self, image, _index):
        index = _index - 1
        if index >= len(self.configs['templates']):
            logger.warning(f'No such template with index "{_index}"')
            return
        height, width = image.shape[:2]
        template = self.configs['templates'][index]
        x1, y1, x2, y2 = self.parse_rect((height, width), template['rect'])
        filepath = f'detects/{self.model_name}/clips/{template["name"]}.png'
        cv2.imwrite(filepath, alpha_mask(image[y1:y2, x1:x2]))
        logger.info(f'Screenshot for "{template["name"]}" saved to {filepath}')

    def mark(self, image, x1, y1, x2, y2, text, color):
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        if not text:
            return
        rect, _ = cv2.getTextSize(text, self.font, 0.5, 2)
        if y1 < rect[1]:
            cv2.putText(image, text, ((x1 + x2 - rect[0]) // 2, y2 + rect[1]), self. font, 0.5, color, 2)
        else:
            cv2.putText(image, text, ((x1 + x2 - rect[0]) // 2, y1 - rect[1]), self.font, 0.5, color, 2)

    def match_template(self, image):  # 模板匹配
        height, width = image.shape[:2]
        cover = np.zeros((height, width, 3), dtype=np.uint8)
        groups = {}

        for i, item in enumerate(self.configs['templates']):
            x1, y1, x2, y2 = self.parse_rect((height, width), item['rect'])
            hint = f'[{i+1}] {item["name"]}'
            if 'template' in item:
                target = alpha_mask(image[y1:y2, x1:x2])
                template = item['template']
                self.mark(cover, x1, y1, x2, y2, '', COLOR_YELLOW)

                result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
                min_val, _, min_loc, _ = cv2.minMaxLoc(result)
                similarity = 1 - min_val  # 计算相似度
                min_loc = min_loc[0] + x1, min_loc[1] + y1  # 还原到绝对坐标
                min_rect = (*min_loc, min_loc[0] + template.shape[1], min_loc[1] + template.shape[0])

                hint += f' {similarity * 100:.2f}%'
                if similarity >= item['threshold']:
                    color = COLOR_GREEN
                    groups[item['name']] = min_rect
                else:
                    color = COLOR_RED

                self.mark(cover, *min_rect, hint, color)
            else:
                self.mark(cover, x1, y1, x2, y2, hint, COLOR_BLUE)

        return groups, cover

    def match_progress(self, image, hook_pos, cover):  # 进度条匹配
        progress_config = self.configs['progress']

        img_height, img_width = image.shape[:2]
        center_x = (hook_pos[0] + hook_pos[2]) // 2
        center_y = (hook_pos[1] + hook_pos[3]) // 2 - int(img_height * progress_config['offset'])

        width = int(img_width * progress_config['width'])
        height = int(img_height * progress_config['height'])
        x1, x2 = center_x - width // 2, center_x + width // 2
        y1, y2 = center_y - height // 2, center_y + height // 2
        progress = alpha_mask(image[y1:y2, x1:x2])

        frame_color = progress_config['frame-color']
        mask = np.all(progress == frame_color, axis=2)
        count = np.sum(mask)

        self.mark(cover, x1, y1, x2, y2, f'Progress [{count}/{width * height}]', (255, 0, 0))
        if (count / (width * height)) > progress_config['threshold']:
            sample = np.sum(mask, axis=0)
            sp = progress_config['sp']
            frame_pos, cursor_pos = [], []
            for i, val in enumerate(sample):
                if sp[0] <= val < sp[1]:
                    frame_pos.append(i)
                elif val >= sp[1]:
                    cursor_pos.append(i)
            if frame_pos and cursor_pos:
                frame_pos, cursor_pos = [min(frame_pos), max(frame_pos)], [min(cursor_pos), max(cursor_pos)]
                self.mark(cover, x1 + frame_pos[0], y1, x1 + frame_pos[1], y2, 'Frame', (255, 0, 255))
                cursor_x = sum(cursor_pos) // 2
                if frame_pos[0] <= cursor_x <= frame_pos[1]:
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 255)
                self.mark(cover, x1 + cursor_pos[0], y1, x1 + cursor_pos[1], y2, 'Cursor', color)

                # 如果未达到位置则需要点击
                return cursor_x < frame_pos[0] + (frame_pos[1] - frame_pos[0]) * configs['progress-threshold']
        return None
