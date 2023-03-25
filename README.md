# NordVPN Tray

NordVPN Tray is a simple GUI app to manage the official NordVPN linux client
app [https://nordvpn.com/download/linux/](https://nordvpn.com/download/linux/). It does not replace the official
client and cannot be used without it.

I've created this app for my personal use. It is not supported or sponsored by the NordVPN.

App is written in python with PySide6 (Qt6) library and built with pyinstaller.

### Screenshots

![System Tray](https://raw.github.com/bttrs-org/nordvpn-tray/main/screenshots/tray.png "System Tray")
![Connection window](https://raw.github.com/bttrs-org/nordvpn-tray/main/screenshots/connection.png "Connection window")
![Settings Tray](https://raw.github.com/bttrs-org/nordvpn-tray/main/screenshots/settings.png "Settings window")

## Installation

To install this application you can either download a prebuilt binaries, run it from sources with python or build it for
yourself with pyinstaller

Before using this app, make sure that you have installed the official NordVPN linux
client [https://nordvpn.com/download/linux/](https://nordvpn.com/download/linux/).

### Download prebuilt executables

The easiest way is to download prebuilt app from GitHub releases page.

1. Download the latest release
   from [https://github.com/bttrs-org/nordvpn-tray/releases](https://github.com/bttrs-org/nordvpn-tray/releases).
2. Unpack downloaded file: `tar -xf nordvpn-tray.tar.xz`
3. Copy unpacked folder to a folder where you want to keep the application: `sudo cp -r nordvpn-tray /opt`
4. Run app from terminal: `/opt/nordvpn-tray/nordvpn-tray`

#### Create a desktop and startup entry

To add desktop entry to applications list, create a new file `nordvpn-tray.desktop` in `~/.local/share/applications`
with content:

```
[Desktop Entry]
Version=1.0
Type=Application
Name=NordVPN Tray
Comment=GUI for NordVPN client.
Icon=nordvpn
Exec=/opt/nordvpn-tray/nordvpn-tray
```

If you wan to start applicatin automativally after user log in create a new file `nordvpn-tray.desktop`
in `~/.config/autostart` with content:

```
[Desktop Entry]
Type=Application
Name=NordVPN Tray
Comment=GUI for NordVPN client.
Exec=/opt/nordvpn-tray/nordvpn-tray
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=15
```

### Custom build

TBD
