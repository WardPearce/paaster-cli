# Paaster CLI
Upload locally encrypted pastes to paaster.io from your desktop.

## Support
Currently only tested on Linux. Let me know if you have any issues on Windows or MacOS.

## Installing
- `pip3 install paaster`

## Commands
- paaster --help
    - Shows commands
- paaster upload
    - Upload locally encrypted clipboard to API.
- paaster set --name "" --value ""
    - Sets config parameters

## Parameters
- API_URL
    - Backend URL, type string
- FRONTEND_URL
    - Frontend URL, type string
- COPY_URL_TO_CLIPBOARD
    - If to copy URL to clipboard, type "true/false"
- OPEN_URL_IN_BROWSER
    - If to open paste in browser, type "true/false"
