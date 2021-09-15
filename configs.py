import yaml


with open('configs.yml', 'r', encoding='utf-8') as _fp:
    configs = yaml.safe_load(_fp)


with open('detects/models.yml', 'r', encoding='utf-8') as _fp:
    models = yaml.safe_load(_fp)


if __name__ == '__main__':
    print(models)
