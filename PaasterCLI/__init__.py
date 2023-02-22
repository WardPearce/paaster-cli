# -*- coding: utf-8 -*-

"""
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
"""

import platform
import webbrowser
from os import getenv
from typing import Any

import click
import pyperclip
import pysodium
import requests

from .misc import end_slash, url_unpadded_base64
from .storage import JsonStorage

SYSTEM = platform.system()
if SYSTEM == "Linux":
    pathway = f"{getenv('HOME')}/.config/paaster"
elif SYSTEM == "Windows":
    pathway = f"{getenv('APPDATA')}\\paaster"
elif SYSTEM == "Darwin":
    pathway = f"/Users/{getenv('HOME')}/Library/Application Support/paaster"
else:
    raise Exception("Platform not supported.")

VALID = ["API_URL", "FRONTEND_URL", "COPY_URL_TO_CLIPBOARD", "OPEN_URL_IN_BROWSER"]
STORAGE = JsonStorage(pathway)

_paaster_api = STORAGE.get("API_URL")
_paaster_frontend = STORAGE.get("FRONTEND_URL")
_copy_to_clipboard = STORAGE.get("COPY_URL_TO_CLIPBOARD")
_open_browser = STORAGE.get("OPEN_URL_IN_BROWSER")


@click.group()
def main() -> None:
    """Upload locally encrypted pastes to paaster.io from your desktop."""

    pass


@main.command("set")
@click.option("--name")
@click.option("--value")
def set_(name: str, value: Any) -> None:
    """Set a config parameter."""

    name = name.upper()

    if name not in VALID:
        click.echo(f"{name} isn't a valid parameter.")
    else:
        value = value.lower()
        if name in ("API_URL", "FRONTEND_URL"):
            value = end_slash(value)
        elif value == "true":
            value = True
        elif value == "false":
            value = False

        STORAGE.set(name, value)


@main.command()
def upload() -> None:
    """Upload locally encrypted clipboard to API."""

    plain_clipboard = pyperclip.paste()
    if not plain_clipboard.strip():
        return

    raw_key = pysodium.randombytes(32)
    raw_iv = pysodium.randombytes(pysodium.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES)
    cipher_text = pysodium.crypto_aead_xchacha20poly1305_ietf_encrypt(
        plain_clipboard.encode("utf8"), None, raw_iv, raw_key
    )

    resp = requests.post(
        _paaster_api + f"controller/paste/{url_unpadded_base64(raw_iv)}",
        data=cipher_text,
    )
    if resp.status_code == 201:
        paste = resp.json()
        url = _paaster_frontend + paste["_id"] + f"#{url_unpadded_base64(raw_key)}"

        if _copy_to_clipboard:
            pyperclip.copy(url)

        if _open_browser:
            # Adds server secret at end of URL.
            # this will be removed from URL ASAP by paaster,
            # this functionality isn't done for copy on clipboard
            # because someone may share the link directly
            # with someone else.

            # This secret isn't shared with the server at any point.
            webbrowser.open(url + "&ownerSecret=" + paste["owner_secret"], 0)
