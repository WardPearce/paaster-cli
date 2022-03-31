import toga
import pyclip
import requests
import secrets

from pynput import keyboard

from toga.style.pack import Pack, LEFT, COLUMN


class PaasterClient(toga.App):
    _paaster_api = "https://api.paaster.io/"
    _paaster_frontend = "https://paaster.io/"
    _global_shortcut = None

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
            self._global_shortcut.start()

    def on_paste(self) -> None:
        plain_clipboard = pyclip.paste()

        client_sided_key = secrets.token_urlsafe(32)

        resp = requests.put(
            self._paaster_api + "api/paste/create",
            data="",
            headers={
                "Content-Type": "text/plain"
            }
        )
        if resp.status_code == 200:
            json = resp.json()
            pyclip.copy(
                f"{self._paaster_frontend}{json['pasteId']}#{client_sided_key}"
            )

    def startup(self) -> None:
        self.main_window = toga.Window(
            title=self.name,
            size=(300, 400)
        )

        box = toga.Box(
            style=Pack(
                flex=1,
                direction=COLUMN,
                padding=10
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
        self._shortcut.value = "<ctrl>+<alt>+p"
        self.update_shortcut()

        box.add(shortcut_label)
        box.add(self._shortcut)
        box.add(
            toga.Button(
                "Update shortcut",
                on_press=self.update_shortcut,
                style=Pack(width=300)
            )
        )

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


if __name__ == '__main__':
    main().main_loop()
