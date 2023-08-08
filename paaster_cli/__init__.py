# -*- coding: utf-8 -*-

"""
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
"""

import platform
import webbrowser
from os import getenv
from typing import Dict, Optional

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

VALID = ["API_URL", "FRONTEND_URL", "COPY_URL_TO_CLIPBOARD", "OPEN_URL_IN_BROWSER", "ECHO_URL"]
STORAGE = JsonStorage(pathway)

API_URL = STORAGE.get("API_URL")
FRONTEND_URL = STORAGE.get("FRONTEND_URL")
COPY_URL_TO_CLIPBOARD = STORAGE.get("COPY_URL_TO_CLIPBOARD")
OPEN_URL_IN_BROWSER = STORAGE.get("OPEN_URL_IN_BROWSER")
ECHO_URL = STORAGE.get("ECHO_URL", False)


@click.group()
def main() -> None:
    """Interact with Paaster.io from your terminal!"""

    pass


@main.command("set")
@click.option("--name", "-n")
@click.option("--value", "-v")
def set_(name: str, value: str) -> None:
    """Set a config parameter."""

    name = name.upper()

    if name not in VALID:
        click.echo(f"{name} isn't a valid parameter.")
    else:
        to_set = value.lower()
        if name in ("API_URL", "FRONTEND_URL"):
            to_set = end_slash(value)
        elif to_set == "true":
            to_set = True
        elif to_set == "false":
            to_set = False

        STORAGE.set(name, to_set)


@main.command()
@click.option(
    "--mode",
    "-m",
    default="clipboard",
    help="clipboard, file, inline",
    show_default=True,
)
@click.option(
    "--copy_to_clipboard",
    "-ctc",
    type=click.BOOL,
    show_default=True,
    default=COPY_URL_TO_CLIPBOARD,
    help="Overwrite COPY_URL_TO_CLIPBOARD setting.",
)
@click.option(
    "--open_browser",
    "-ob",
    type=click.BOOL,
    show_default=True,
    default=OPEN_URL_IN_BROWSER,
    help="Overwrite OPEN_URL_IN_BROWSER setting.",
)
@click.option(
    "--echo_url",
    "-eu",
    type=click.BOOL,
    show_default=True,
    default=ECHO_URL,
    help="Overwrite ECHO_URL setting.",
)
@click.argument("input_", default=None, required=False)
def upload(
    mode: str,
    copy_to_clipboard: bool,
    open_browser: bool,
    echo_url: bool,
    input_: Optional[str],
) -> None:
    """Use to upload to Paaster.io"""

    plain_paste = ""
    if mode == "clipboard":
        plain_paste = pyperclip.paste()
    elif mode == "file":
        if not input_:
            click.echo("--mode file requires input")
            return

        with open(input_, "r") as f_:
            plain_paste = f_.read()

    elif mode == "inline":
        if not input_:
            click.echo("--mode inline requires input")
            return

        plain_paste = input_

    if not plain_paste.strip():
        return

    raw_key = pysodium.randombytes(pysodium.crypto_aead_xchacha20poly1305_ietf_KEYBYTES)
    raw_iv = pysodium.randombytes(pysodium.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES)
    cipher_text = pysodium.crypto_aead_xchacha20poly1305_ietf_encrypt(
        plain_paste.encode("utf8"), None, raw_iv, raw_key
    )

    resp = requests.post(
        API_URL + f"controller/paste/{url_unpadded_base64(raw_iv)}",
        data=cipher_text,
    )
    if resp.status_code == 201:
        paste: Dict[str, str] = resp.json()
        url = f"{FRONTEND_URL}{paste['_id']}#{url_unpadded_base64(raw_key)}"

        if echo_url:
            click.echo(url)

        if copy_to_clipboard:
            pyperclip.copy(url)

        if open_browser:
            # Adds server secret at end of URL.
            # this will be removed from URL ASAP by paaster,
            # this functionality isn't done for copy on clipboard
            # because someone may share the link directly
            # with someone else.

            # This secret isn't shared with the server at any point.
            webbrowser.open(url + "&ownerSecret=" + paste["owner_secret"], 0)
