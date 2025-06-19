import json
import os

import orjson


class JSONManager:
    """Класс для управления JSON-файлами"""

    @staticmethod
    def get_json(path) -> dict:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                data = orjson.loads(file.read())
            return data
        return {}

    @staticmethod
    def insert_json(path, obj) -> None:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(obj, file, indent=4, ensure_ascii=False)
