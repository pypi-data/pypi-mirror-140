import os

from ruamel.yaml import YAML

default = '''
base:
  # 程序名称
  name: 机器人
  # 版本号
  version: 1.0.0
'''


class Config:
    def __init__(self, file: str, data: str = default):
        self.factory = YAML()
        self.file = file
        self.data = self.factory.load(data)
        self.load() if os.path.exists(self.file) else self.dump()

    def load(self):
        with open(self.file, 'r', encoding='utf-8') as f:
            self.data = self.factory.load(f)

    def dump(self):
        path = os.path.dirname(self.file)
        if path:
            os.makedirs(path, exist_ok=True)
        with open(self.file, 'w', encoding='utf-8') as f:
            self.factory.dump(self.data, f)
