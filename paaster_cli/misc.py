# -*- coding: utf-8 -*-

"""
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
"""


from base64 import urlsafe_b64encode


def end_slash(value: str) -> str:
    if not value.endswith("/"):
        value += "/"
    return value


def url_unpadded_base64(data: bytes) -> str:
    return urlsafe_b64encode(data).decode().rstrip("=")
