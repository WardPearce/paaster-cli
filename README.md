# Paaster CLI: Encrypted Pastes from Your Terminal

## Support
- Linux (Tested)
- Windows (Tested)
- MacOS (Not tested, please submit an issue if it works or not)

## Installation
- `pip3 install paaster`

## Commands
- `paaster --help`: Shows available commands.
- `paaster upload`: Upload locally encrypted clipboard to the API.

    Options:
    - `-m, --mode TEXT`: Specify the mode for the paste, choose from "clipboard", "file", or "inline". (default: clipboard)
    - `-ctc, --copy_to_clipboard BOOLEAN`: Overwrite COPY_URL_TO_CLIPBOARD setting.
    - `-ob, --open_browser BOOLEAN`: Overwrite OPEN_URL_IN_BROWSER setting.
    - `-eu, --echo_url BOOLEAN`: Overwrite ECHO_URL setting.

- `paaster set --name "" --value ""`: Set config parameters.

## Parameters
- `API_URL`: Backend URL, type: string.
- `FRONTEND_URL`: Frontend URL, type: string.
- `COPY_URL_TO_CLIPBOARD`: Copy URL to clipboard, type: "true/false".
- `OPEN_URL_IN_BROWSER`: Open paste in the browser, type: "true/false".
- `ECHO_URL`: Echo the paste URL in terminal, type: "true/false"
