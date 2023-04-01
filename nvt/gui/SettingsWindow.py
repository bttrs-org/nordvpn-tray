import os
import logging
from typing import Callable, Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QCloseEvent, QShowEvent
from PySide6.QtWidgets import QMainWindow, QLabel, QTabWidget, QVBoxLayout, QWidget
from nvt import Config
from nvt.utils import icons_dir, svg_icon
from nvt.bindings import AccountProcess, NVStatus, CountriesProcess, CitiesProcess
from .Connection import Connection
from .ErrorRow import ErrorRow
from .Settings import Settings

log = logging.getLogger(__name__)


class SettingsWindow(QMainWindow):
    error_row: ErrorRow
    account_label: QLabel
    connect_tab: Connection
    settings_tab: Settings

    def __init__(self, quick_connect_vpn: Callable[[], None],
                 connect_vpn: Callable[[str, Optional[str], Optional[str]], None], disconnect_vpn: Callable[[], None]):
        super().__init__(None)
        # self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.account_process = None
        self.countries_process = None
        self.cities_process = None

        self.setWindowTitle("NordVPN tray")
        self.setWindowIcon(QIcon(os.path.join(icons_dir(), 'icon.png')))
        self.setMinimumSize(480, 480)
        width, height = Config.get_dimension()
        if width and height:
            self.resize(width, height)

        self.error_row = ErrorRow()

        self.account_label = QLabel('', self.statusBar())
        self.account_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.statusBar().addPermanentWidget(self.account_label, 1)

        self.connect_tab = Connection(self, self._load_countries, self._load_cities, quick_connect_vpn, connect_vpn,
                                      disconnect_vpn)
        self.settings_tab = Settings(self._load_countries, self)

        tabs = QTabWidget()
        tabs.addTab(self.connect_tab, svg_icon('connect'), "Connect")
        tabs.addTab(self.settings_tab, svg_icon('settings'), "Settings")

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_widget.setLayout(main_layout)

        main_layout.addWidget(tabs)
        main_layout.addWidget(self.error_row)

        self.setCentralWidget(main_widget)
        self._load_account()

    def showEvent(self, event: QShowEvent) -> None:
        self.settings_tab.load_settings()

    def closeEvent(self, event: QCloseEvent):
        Config.save_dimension(self.width(), self.height())
        super().closeEvent(event)

    def set_connecting(self, connecting: bool):
        self.connect_tab.set_connecting(connecting)

    def set_connect_error(self, msg: Optional[str] = None):
        self._set_error(msg)

    def set_status(self, status: NVStatus):
        self.connect_tab.set_status(status)

    def _load_account(self):
        if self.account_process:
            return

        def done(account):
            self.account_process = None
            self.account_label.setText(f"{account.email} - {account.status}")

        def error(e):
            self.account_process = None
            self._set_error(f"Load account failed: {e}")

        self.account_process = AccountProcess(on_finish=done, on_error=error).run()

    def _load_countries(self):
        if self.countries_process:
            return
        self._set_error()

        def done(countries):
            self.countries_process = None
            if countries:
                self.connect_tab.set_countries(countries)
                self.settings_tab.set_countries(countries)

        def error(e):
            self.countries_process = None
            self._set_error(f"Load countries failed: {e}")

        self.countries_process = CountriesProcess(on_finish=done, on_error=error).run()

    def _load_cities(self, country: str):
        if self.cities_process:
            self.cities_process.close()
        self._set_error()

        def done(cities):
            self.cities_process = None
            if cities:
                self.connect_tab.set_cities(cities)

        def error(e):
            self.cities_process = None
            self._set_error(f"Load cities failed: {e}")

        self.cities_process = CitiesProcess(on_finish=done, on_error=error).run(country)

    def _set_error(self, msg: Optional[str] = None):
        if msg:
            self.error_row.set_msg(msg)
        else:
            self.error_row.clear()
