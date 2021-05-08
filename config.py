import json
import os

CONFIG_PY_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG = CONFIG_PY_PATH + "/config.json"


class Config:
    def __init__(self):
        with open(CONFIG, "r", encoding="utf-8") as file:
            self.res = json.loads(file.read())

    def __getitem__(self, item):
        return self.res[item]
