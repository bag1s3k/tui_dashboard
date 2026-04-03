import json
from pathlib import Path

from utils.correct_path import get_path

class AppConfig:
    def __init__(self, path: str | Path):
        self.path: str | Path = path
        self.config: dict = self.read_config()

        self.read_config()

    def read_config(self) -> dict:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.loads(f.read())

appconfig = AppConfig(get_path("./config.json"))