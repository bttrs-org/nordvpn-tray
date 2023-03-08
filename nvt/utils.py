import sys
import os


def is_dev() -> bool:
    return os.getenv('APP_ENV') == 'dev'


def user_data_dir() -> str:
    path = os.path.join(os.path.expanduser('~'), '.local', 'share', 'nordvpn-tray')
    if not os.path.isdir(path):
        os.makedirs(path, mode=0o755)
    return path


def icons_dir() -> str:
    return os.path.join(os.path.dirname(sys.argv[0]), 'icons')
