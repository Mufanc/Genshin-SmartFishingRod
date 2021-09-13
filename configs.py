import json
import os

import yaml

filepath = os.path.join(os.path.split(__file__)[0], 'configs.yml')
with open(filepath, 'r', encoding='utf-8') as _fp:
    configs = yaml.safe_load(_fp)


if __name__ == '__main__':
    print(json.dumps(configs, indent=4, ensure_ascii=False))
