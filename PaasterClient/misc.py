# -*- coding: utf-8 -*-

"""
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
"""


def end_slash(value: str) -> str:
    if not value.endswith("/"):
        value += "/"
    return value
