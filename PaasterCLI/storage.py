# -*- coding: utf-8 -*-

"""
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
"""

import json

from typing import Any
from os import mkdir, path


class JsonStorage:
    def __init__(self, pathway: str) -> None:
        self._pathway = pathway
        if not path.exists(self._pathway):
            self.__make_config_init()

    def __make_config_init(self) -> None:
        mkdir(self._pathway)
        self.set("API_URL", "https://api.paaster.io/")
        self.set("FRONTEND_URL", "https://paaster.io/")
        self.set("COPY_URL_TO_CLIPBOARD", True)
        self.set("OPEN_URL_IN_BROWSER", False)
        self.set("NAME", "paaster")

    @property
    def pathway(self) -> str:
        return path.join(
            self._pathway,
            "config.json"
        )

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
