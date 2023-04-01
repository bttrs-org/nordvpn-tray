import sys
import os
from typing import Optional
from PySide6.QtGui import QIcon


def is_dev() -> bool:
    return os.getenv('APP_ENV') == 'dev'


def user_data_dir() -> str:
    path = os.path.join(os.path.expanduser('~'), '.local', 'share', 'nordvpn-tray')
    if not os.path.isdir(path):
        os.makedirs(path, mode=0o755)
    return path


def icons_dir() -> str:
    return os.path.join(os.path.dirname(sys.argv[0]), 'icons')


icons: dict[str, Optional[QIcon]] = dict()


def country_icon(code: Optional[str]) -> Optional[QIcon]:
    if not code:
        return None
    if code not in icons:
        path = os.path.join(icons_dir(), 'flags', f"{code.lower()}.png")
        if os.path.isfile(path):
            ico = QIcon(path)
            icons[code] = ico
        else:
            icons[code] = None

    return icons[code]


def png_icon(icon: str):
    name = f"{icon}.png"
    if name not in icons:
        ico = QIcon(os.path.join(icons_dir(), name))
        icons[name] = ico

    return icons[name]


def svg_icon(icon: str):
    name = f"{icon}.svg"
    if name not in icons:
        ico = QIcon(os.path.join(icons_dir(), name))
        icons[name] = ico

    return icons[name]
