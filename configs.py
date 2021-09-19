import yaml


with open('configs.yml', 'r', encoding='utf-8') as _fp:
    configs = yaml.safe_load(_fp)

configs['window-size'] = [1600, 900]


if __name__ == '__main__':
    pass
