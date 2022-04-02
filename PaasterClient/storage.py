import json

from typing import Any


class JsonStorage:
    def __init__(self, pathway: str = "./paaster.json") -> None:
        self._pathway = pathway

    @property
    def pathway(self) -> str:
        return self._pathway

    def all(self) -> dict:
        try:
            with open(self.pathway, "r") as f_:
                try:
                    return json.loads(f_.read())
                except json.JSONDecodeError:
                    return {}
        except FileNotFoundError:
            return {}

    def get(self, key: str, fallback: Any = None) -> Any:
        data = self.all()
        return data[key] if key in data else fallback

    def set(self, key: str, value: Any) -> None:
        data = self.all()
        data[key] = value

        with open(self.pathway, "w+") as f_:
            f_.write(json.dumps(data))
