import contextlib
import logging
from typing import Optional, Callable
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsOpacityEffect, QComboBox
from nvt.Config import get_quick_connect, save_quick_connect
from nvt.bindings import SettingsProcess, NVSettings
from .ErrorRow import ErrorRow

log = logging.getLogger(__name__)


class DefaultCountry(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.addWidget(QLabel('Quick connect to: '))
        self.countries = QComboBox()
        layout.addWidget(self.countries)
        self.setLayout(layout)

    def set_countries(self, countries: list[tuple[str, str]]):
        with contextlib.suppress(RuntimeError):
            self.countries.currentIndexChanged.disconnect(self._value_changed)
        self.countries.clear()
        self.countries.addItem('# fastest')
        for country, code, icon in countries:
            self.countries.addItem(icon, country.replace("_", " "), userData=country)

        saved = get_quick_connect()
        if saved:
            idx = self.countries.findData(saved)
            self.countries.setCurrentIndex(idx)
        else:
            self.countries.setCurrentIndex(0)

        self.countries.currentIndexChanged.connect(self._value_changed)

    def _value_changed(self):
        save_quick_connect(self.countries.currentData())


class OptionRow(QWidget):
    def __init__(self, label: str):
        super().__init__()

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.addWidget(QLabel(label))
        layout.addStretch()
        self.value_label = QLabel('')
        layout.addWidget(self.value_label)
        self.setLayout(layout)

    def set_value(self, value: Optional[str]):
        self.value_label.setStyleSheet('font-weight: 500;')
        if value:
            if value.lower() == 'enabled':
                self.value_label.setStyleSheet('font-weight: 500; color: palette(highlight);')
            if value.lower() == 'disabled':
                self.value_label.setStyleSheet('font-weight: 200;')
            self.value_label.setText(value)
        else:
            self.value_label.setText('')


class Separator(QFrame):
    def __init__(self):
        super().__init__()

        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0.3)

        self.setFrameShape(QFrame.Shape.HLine)
        self.setLineWidth(1)
        self.setGraphicsEffect(self.opacity_effect)


class Settings(QWidget):
    load_countries: Callable[[], None]
    default_country: DefaultCountry
    option_rows: dict[str, OptionRow]
    error_row: ErrorRow

    def __init__(self, load_countries: Callable[[], None], parent=None):
        super().__init__(parent)
        self.load_countries = load_countries

        self.inputs = dict()
        self.option_rows = dict()
        self.load_process = None
        self.set_setting_process = None

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(5)

        # default quick connect
        self.default_country = DefaultCountry()
        self.layout.addWidget(self.default_country)
        self.layout.addSpacing(16)

        # cli option
        def create_option_row(key: str, label: str):
            self.option_rows[key] = OptionRow(label)
            self.layout.addWidget(self.option_rows[key])
            self.layout.addWidget(Separator())

        create_option_row('technology', 'Technology')
        create_option_row('protocol', 'Protocol')
        create_option_row('autoconnect', 'Auto-connect')
        create_option_row('killswitch', 'Kill Switch')
        create_option_row('routing', 'Routing')
        create_option_row('analytics', 'Analytics')
        create_option_row('tplite', 'Threat Protection Lite')
        create_option_row('notify', 'Notify')
        create_option_row('ipv6', 'IPv6')
        create_option_row('meshnet', 'Meshnet')
        create_option_row('dns', 'DNS')
        create_option_row('firewall', 'Firewall')
        create_option_row('fwmark', 'Firewall Mark')

        self.layout.addSpacing(10)
        self.layout.addWidget(QLabel('Run `nordvpn set --help` in a terminal to learn how to change settings.'))

        self.layout.addStretch()

        self.error_row = ErrorRow()
        self.layout.addWidget(self.error_row)

        self.setLayout(self.layout)
        self.load_settings()

    def set_countries(self, countries: list[tuple[str, str]]):
        self.default_country.set_countries(countries)

    def load_settings(self):
        if self.load_process:
            return
        self._set_error()

        def done(settings: NVSettings):
            self.load_process = None
            for key, value in self.option_rows.items():
                value.set_value(getattr(settings, key))

        def error(e):
            self.load_process = None
            log.error(e)
            self._set_error(e)

        self.load_process = SettingsProcess(on_finish=done, on_error=error).run()

    def _set_error(self, msg: Optional[str] = None):
        if msg:
            self.error_row.set_msg(msg)
        else:
            self.error_row.clear()
