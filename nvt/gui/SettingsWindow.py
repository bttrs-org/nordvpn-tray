import os
import logging
from typing import Callable, Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QCloseEvent
from PySide6.QtWidgets import QMainWindow, QLabel, QTabWidget
from nvt import Config
from nvt.utils import icons_dir
from nvt.bindings import AccountProcess, NVStatus
from .Connection import Connection
from .Settings import Settings

log = logging.getLogger(__name__)


class SettingsWindow(QMainWindow):
    status_bar_label: QLabel
    connect_tab: Connection
    settings_tab: Settings

    def __init__(self, quick_connect_vpn: Callable[[], None],
                 connect_vpn: Callable[[str, Optional[str], Optional[str]], None], disconnect_vpn: Callable[[], None]):
        super().__init__(None)
        self.account_process = None

        self.setWindowTitle("NordVPN tray")
        self.setWindowIcon(QIcon(os.path.join(icons_dir(), 'icon.png')))
        self.setMinimumSize(480, 480)
        width, height = Config.get_dimension()
        if width and height:
            self.resize(width, height)

        self.status_bar_label = QLabel('', self.statusBar())
        self.status_bar_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.statusBar().addPermanentWidget(self.status_bar_label, 1)

        self.connect_tab = Connection(self, quick_connect_vpn, connect_vpn, disconnect_vpn)
        self.settings_tab = Settings(self)

        tabs = QTabWidget(self)
        tabs.addTab(self.connect_tab, QIcon.fromTheme("network-transmit"), "Connect")
        tabs.addTab(self.settings_tab, QIcon.fromTheme("preferences-system"), "Settings")

        self.setCentralWidget(tabs)

        self.load_account()

    def load_account(self):
        if self.account_process:
            return

        def done(account):
            self.account_process = None
            self.status_bar_label.setText(f"{account.email} - {account.status}")

        def error(e):
            self.account_process = None
            self.status_bar_label.setText(f"Load account failed: {e}")

        self.account_process = AccountProcess(on_finish=done, on_error=error).run()

    def closeEvent(self, event: QCloseEvent):
        Config.save_dimension(self.width(), self.height())
        super().closeEvent(event)

    def set_connecting(self, connecting: bool):
        self.connect_tab.set_connecting(connecting)

    def set_connect_error(self, msg: Optional[str] = None):
        self.connect_tab.set_error(msg)

    def set_status(self, status: NVStatus):
        self.connect_tab.set_status(status)
