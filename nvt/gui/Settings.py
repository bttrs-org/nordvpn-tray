import logging
from typing import Dict, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsOpacityEffect
from nvt.bindings import SettingsProcess, NVSettings
from .ErrorRow import ErrorRow

log = logging.getLogger(__name__)


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
    option_rows: Dict[str, OptionRow]
    error_row: ErrorRow

    def __init__(self, parent=None):
        super().__init__(parent)
        self.inputs = dict()
        self.option_rows = dict()
        self.load_process = None
        self.set_setting_process = None

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(5)

        def create_option_row(key: str, label: str):
            self.option_rows[key] = OptionRow(label)
            self.layout.addWidget(self.option_rows[key])
            self.layout.addWidget(Separator())

        create_option_row('technology', 'Technology')
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

    def set_error(self, msg: Optional[str] = None):
        if msg:
            self.error_row.set_msg(msg)
        else:
            self.error_row.clear()

    def load_settings(self):
        if self.load_process:
            return
        self.set_error()

        def done(settings: NVSettings):
            self.load_process = None
            for key, value in self.option_rows.items():
                value.set_value(getattr(settings, key))

        def error(e):
            self.load_process = None
            log.error(e)
            self.set_error(e)

        self.load_process = SettingsProcess(on_finish=done, on_error=error).run()
