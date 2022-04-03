# -*- coding: utf-8 -*-

"""
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
"""

import toga
import pyclip
import requests
import secrets
import webbrowser

from pynput import keyboard
from toga.style.pack import Pack, LEFT, COLUMN
from plyer import notification

from .misc import end_slash
from .encrypt import password_encrypt
from .storage import JsonStorage


class PaasterClient(toga.App):
    _paaster_api = "https://api.paaster.io/"
    _paaster_frontend = "https://paaster.io/"
    _global_shortcut = None
    _default_shortcut = "<ctrl>+<alt>+p"
    _storage: JsonStorage

    def on_api_url_change(self, widget: toga.Widget) -> None:
        self._paaster_api = end_slash(widget.value)
        self._storage.set("api", self._paaster_api)

    def on_frontend_url_change(self, widget: toga.Widget) -> None:
        self._paaster_frontend = end_slash(widget.value)
        self._storage.set("frontend", self._paaster_frontend)

    def on_copy_on_save_change(self, widget: toga.Widget) -> None:
        self._storage.set("copy_on_save", widget.is_on)

    def on_browser_on_save_change(self, widget: toga.Widget) -> None:
        self._storage.set("browser_on_save", widget.is_on)

    def update_shortcut(self, button=None) -> None:
        if self._global_shortcut:
            self._global_shortcut.stop()

        try:
            self._global_shortcut = keyboard.GlobalHotKeys({
                self._shortcut.value: self.on_paste}
            )
        except ValueError:
            pass
        else:
            self._global_shortcut.start()
            self._storage.set("shortcut", self._shortcut.value)

    def on_paste(self) -> None:
        plain_clipboard = pyclip.paste()
        if not plain_clipboard.strip():
            notification.notify(
                self.name, "Clipboard currently blank, upload cancelled."
            )
            return

        client_sided_key = secrets.token_urlsafe(32)

        resp = requests.put(
            self._paaster_api + "api/paste/create",
            data=password_encrypt(client_sided_key, plain_clipboard),
            headers={
                "Content-Type": "text/plain"
            }
        )
        if resp.status_code == 200:
            paste = resp.json()
            url = (
                self._paaster_frontend +
                paste["pasteId"] +
                f"#{client_sided_key}"
            )

            if self._copy_to_clipboard.is_on:
                notification.notify(
                    self.name, "Share URL copied to clipboard."
                )
                pyclip.copy(url)

            if self._open_browser.is_on:
                # Adds server secret at end of URL.
                # this will be removed from URL ASAP by paaster,
                # this functionality isn't done for copy on clipboard
                # because someone may share the link directly
                # with someone else.
                webbrowser.open(
                    url + "&serverSecret=" + paste['serverSecret'], 0
                )

    def startup(self) -> None:
        self._storage = JsonStorage()

        self.main_window = toga.Window(
            title=self.name,
            size=(320, 300)
        )

        box = toga.Box(
            style=Pack(
                flex=1,
                direction=COLUMN,
                padding_left=10
            )
        )

        api_url_label = toga.Label(
            "API URL",
            style=Pack(
                text_align=LEFT,
            )
        )
        api_url = toga.TextInput(
            style=Pack(width=300),
            on_change=self.on_api_url_change
        )
        api_url.value = self._storage.get(
            "api", self._paaster_api
        )

        frontend_url_label = toga.Label(
            "Frontend URL",
            style=Pack(
                text_align=LEFT,
                padding_top=10
            )
        )
        frontend_url = toga.TextInput(
            style=Pack(width=300),
            on_change=self.on_frontend_url_change
        )
        frontend_url.value = self._storage.get(
            "frontend", self._paaster_frontend
        )

        box.add(api_url_label)
        box.add(api_url)

        box.add(frontend_url_label)
        box.add(frontend_url)

        shortcut_label = toga.Label(
            "Shortcut",
            style=Pack(
                text_align=LEFT,
                padding_top=10
            )
        )
        self._shortcut = toga.TextInput(
            style=Pack(width=300)
        )

        self._shortcut.value = self._storage.get(
            "shortcut", self._default_shortcut
        )

        self.update_shortcut()

        box.add(shortcut_label)
        box.add(self._shortcut)
        box.add(
            toga.Button(
                "Update shortcut",
                on_press=self.update_shortcut,
                style=Pack(width=300, padding_top=5)
            )
        )

        self._copy_to_clipboard = toga.Switch(
            "Copy URL on save",
            style=Pack(padding_top=20, width=300),
            on_toggle=self.on_copy_on_save_change,
            is_on=self._storage.get("copy_on_save", True)
        )
        box.add(self._copy_to_clipboard)

        self._open_browser = toga.Switch(
            "Open in browser on save",
            style=Pack(padding_top=10, width=300),
            on_toggle=self.on_browser_on_save_change,
            is_on=self._storage.get("browser_on_save", False)
        )
        box.add(self._open_browser)

        self.main_window.content = box
        self.main_window.show()


def main():
    return PaasterClient(
        "paaster",
        "io.paaster.app",
        author="WardPearce",
        description="Upload encrypted pastes to paaster.io from your desktop",
        version="0.0.0",
        home_page="https://paaster.io"
    )
