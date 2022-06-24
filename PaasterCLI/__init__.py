# -*- coding: utf-8 -*-

"""
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
"""

import pyperclip
import requests
import secrets
import click
import webbrowser

from typing import Any

from .misc import end_slash
from .encrypt import password_encrypt
from .storage import JsonStorage


VALID = ["API_URL", "FRONTEND_URL",
         "COPY_URL_TO_CLIPBOARD", "OPEN_URL_IN_BROWSER"]
STORAGE = JsonStorage()

_paaster_api = STORAGE.get("API_URL")
_paaster_frontend = STORAGE.get("FRONTEND_URL")
_copy_to_clipboard = STORAGE.get("COPY_URL_TO_CLIPBOARD")
_open_browser = STORAGE.get("OPEN_URL_IN_BROWSER")


@click.group()
def main() -> None:
    """Upload locally encrypted pastes to paaster.io from your desktop.
    """

    pass


@main.command("set")
@click.option("--name")
@click.option("--value")
def set_(name: str, value: Any) -> None:
    """Set a config parameter.
    """

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
    """Upload locally encrypted clipboard to API.
    """

    plain_clipboard = pyperclip.paste()
    if not plain_clipboard.strip():
        return

    client_sided_key = secrets.token_urlsafe(32)

    resp = requests.put(
        _paaster_api + "api/paste/create",
        data=password_encrypt(
            client_sided_key,
            plain_clipboard.encode()
        ),
        headers={
            "Content-Type": "text/plain"
        }
    )
    if resp.status_code == 200:
        paste = resp.json()
        url = (
            _paaster_frontend +
            paste["pasteId"] +
            f"#{client_sided_key}"
        )

        if _copy_to_clipboard:
            pyperclip.copy(url)

        if _open_browser:
            # Adds server secret at end of URL.
            # this will be removed from URL ASAP by paaster,
            # this functionality isn't done for copy on clipboard
            # because someone may share the link directly
            # with someone else.

            # This secret isn't shared with the server at any point.
            webbrowser.open(
                url + "&serverSecret=" + paste["serverSecret"], 0
            )
