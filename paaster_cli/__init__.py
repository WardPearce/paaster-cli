# -*- coding: utf-8 -*-

"""
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
"""

import platform
import struct
import webbrowser
from base64 import b64encode
from io import BytesIO
from os import getenv
from typing import Any, Dict, Optional

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
    pathway = f"{getenv('HOME')}/Library/Application Support/paaster"
else:
    raise Exception("Platform not supported.")

VALID = [
    "API_URL",
    "FRONTEND_URL",
    "COPY_URL_TO_CLIPBOARD",
    "OPEN_URL_IN_BROWSER",
    "ECHO_URL",
]
STORAGE = JsonStorage(pathway)

API_URL: str = STORAGE.get("API_URL")
FRONTEND_URL: str = STORAGE.get("FRONTEND_URL")
COPY_URL_TO_CLIPBOARD: bool = STORAGE.get("COPY_URL_TO_CLIPBOARD")
OPEN_URL_IN_BROWSER: bool = STORAGE.get("OPEN_URL_IN_BROWSER")
ECHO_URL: bool = STORAGE.get("ECHO_URL", False)


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

    # Generate master key and salt for encryption
    raw_master_key = pysodium.randombytes(32)
    paste_key_salt = pysodium.randombytes(pysodium.crypto_pwhash_SALTBYTES)

    paste_key_raw = pysodium.crypto_pwhash(
        pysodium.crypto_secretstream_xchacha20poly1305_KEYBYTES,
        raw_master_key,
        paste_key_salt,
        pysodium.crypto_pwhash_OPSLIMIT_INTERACTIVE,
        pysodium.crypto_pwhash_MEMLIMIT_INTERACTIVE,
        pysodium.crypto_pwhash_ALG_DEFAULT,
    )

    # Initialize the secretstream encryption state
    stream, header = pysodium.crypto_secretstream_xchacha20poly1305_init_push(
        paste_key_raw
    )

    encrypted_buffer = []
    raw_processed_length = 0
    raw_bytes = plain_paste.encode("utf-8")

    # Encrypt the data in chunks
    for i in range(0, len(raw_bytes), 1024):
        raw_chunk = raw_bytes[i : i + 1024]
        raw_processed_length += len(raw_chunk)

        # Decide on tag (message or final chunk)
        tag = (
            pysodium.crypto_secretstream_xchacha20poly1305_TAG_FINAL
            if raw_processed_length >= len(raw_bytes)
            else pysodium.crypto_secretstream_xchacha20poly1305_TAG_MESSAGE
        )

        encrypted_chunk = pysodium.crypto_secretstream_xchacha20poly1305_push(
            stream, raw_chunk, None, tag
        )

        # Store the length of the chunk in little-endian format
        chunk_len_bytes = struct.pack("<I", len(encrypted_chunk))
        encrypted_buffer.append(chunk_len_bytes + encrypted_chunk)

    # Prepare form data for sending
    form_data = {
        "codeHeader": url_unpadded_base64(header),
        "codeKeySalt": url_unpadded_base64(paste_key_salt),
    }

    # Upload encrypted content to Paaster.io
    resp = requests.post(
        API_URL + f"api/paste",
        data=form_data,
        headers={
            "Referer": API_URL,
            "Origin": API_URL.removesuffix("/"),
        },
    )
    if resp.ok:
        paste: Dict[str, Any] = resp.json()

        s3_payload = {}
        for key, value in paste["signedUrl"]["fields"].items():
            s3_payload[key] = value

        blob = BytesIO(b"".join(encrypted_buffer))
        s3_payload["file"] = blob

        s3_response = requests.post(
            paste["signedUrl"]["url"],
            files=s3_payload,
        )

        if s3_response.ok:
            url = f"{FRONTEND_URL}{paste['pasteId']}#{url_unpadded_base64(raw_master_key)}"

            if echo_url:
                click.echo(url)

            if copy_to_clipboard:
                pyperclip.copy(url)

            if open_browser:
                webbrowser.open(url, 0)
