import toga
import pyclip
import requests
import secrets
import os
import webbrowser

from pynput import keyboard
from toga.style.pack import Pack, LEFT, COLUMN

from .encrypt import encrypt_for_cryptojs


class PaasterClient(toga.App):
    _paaster_api = "https://api.paaster.io/"
    _paaster_frontend = "https://paaster.io/"
    _global_shortcut = None
    _default_shortcut = "<ctrl>+<alt>+p"

    def __save_shortcut(self, value: str) -> None:
        with open("shortcut.txt", "w+") as f_:
            f_.write(value)

    def __end_slash(self, value: str) -> str:
        if not value.endswith("/"):
            value += "/"
        return value

    def on_api_url_change(self, widget: toga.Widget) -> None:
        self._paaster_api = self.__end_slash(widget.value)

    def on_frontend_url_change(self, widget: toga.Widget) -> None:
        self._paaster_frontend = self.__end_slash(widget.value)

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
            self.__save_shortcut(self._shortcut.value)
            self._global_shortcut.start()

    def on_paste(self) -> None:
        plain_clipboard = pyclip.paste()
        if not plain_clipboard:
            return

        client_sided_key = secrets.token_urlsafe(32)

        resp = requests.put(
            self._paaster_api + "api/paste/create",
            data=encrypt_for_cryptojs(plain_clipboard, client_sided_key),
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
                pyclip.copy(url)

            if self._open_browser.is_on:
                webbrowser.open(url, 0)

    def startup(self) -> None:
        self.main_window = toga.Window(
            title=self.name,
            size=(300, 300)
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
        api_url.value = self._paaster_api

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
        frontend_url.value = self._paaster_frontend

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
        if os.path.exists("./shortcut.txt"):
            with open("shortcut.txt") as f_:
                self._shortcut.value = f_.read()
        else:
            self.__save_shortcut(self._default_shortcut)
            self._shortcut.value = self._default_shortcut

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
            style=Pack(padding_top=20, width=300)
        )
        box.add(self._copy_to_clipboard)

        self._open_browser = toga.Switch(
            "Open in browser on save",
            style=Pack(padding_top=10, width=300)
        )
        box.add(self._open_browser)

        self.main_window.content = box
        self.main_window.show()


def main():
    return PaasterClient(
        "paaster",
        "io.paaster.app",
        author="WardPearce",
        description="Simple program to upload to paaster",
        version="0.0.0",
        home_page="https://paaster.io"
    )
