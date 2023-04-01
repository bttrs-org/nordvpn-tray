import os
import configparser
from typing import Optional
from .utils import user_data_dir

config_path = os.path.join(user_data_dir(), 'config.ini')
config = configparser.ConfigParser(default_section="app")
config.read(config_path)

LAST_CONNECTED_SECTION = 'last_connected'


def save_quick_connect(country: Optional[str]):
    if country:
        config.set(config.default_section, 'quick_connect', country)
    else:
        config.remove_option(config.default_section, 'quick_connect')
    _save()


def get_quick_connect() -> Optional[str]:
    return config.get(config.default_section, 'quick_connect', fallback=None)


def save_dimension(w: int, h: int):
    config.set(config.default_section, 'width', str(w))
    config.set(config.default_section, 'height', str(h))
    _save()


def get_dimension() -> tuple[Optional[int], Optional[int]]:
    w = config.getint(config.default_section, 'width', fallback=None)
    h = config.getint(config.default_section, 'height', fallback=None)
    return w, h


def get_last_connected() -> list[list[str]]:
    items: list[list[str]] = []

    for i in _get_last_connected():
        items.append(i.split(':'))
    return items


def add_last_connected(country: str, city: Optional[str], server_number: Optional[str]):
    items = _get_last_connected()
    v = ':'.join([country, city or '', server_number or ''])
    if v in items:
        items.remove(v)

    items.insert(0, v)

    if config.has_section(LAST_CONNECTED_SECTION):
        config.remove_section(LAST_CONNECTED_SECTION)
    config.add_section(LAST_CONNECTED_SECTION)
    for idx, item in enumerate(items):
        config.set(LAST_CONNECTED_SECTION, str(idx), item)
    _save()


def _get_last_connected() -> list[str]:
    if not config.has_section(LAST_CONNECTED_SECTION):
        return []

    items = []
    i = 0
    while config.has_option(LAST_CONNECTED_SECTION, str(i)):
        items.append(config.get(LAST_CONNECTED_SECTION, str(i)))
        i += 1

    return items


def _save():
    with open(config_path, 'w') as configfile:
        config.write(configfile)
