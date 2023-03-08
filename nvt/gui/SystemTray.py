import os
import logging
from typing import Optional
from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from nvt import Config
from nvt.utils import icons_dir
from nvt.bindings import StatusProcess, QuickConnectProcess, NVStatus, DisconnectProcess, ConnectProcess
from nvt.bindings.Countries import NV_COUNTRIES
from .SettingsWindow import SettingsWindow

log = logging.getLogger(__name__)


class SystemTrayIcon(QSystemTrayIcon):
    loading: bool
    connecting: bool
    status: NVStatus
    window: Optional[SettingsWindow]
    error_action: Optional[QAction]
    status_action: QAction
    quick_connect_action: QAction
    disconnect_action: QAction
    last_connected_menu: QMenu
    timer: QTimer

    def __init__(self, parent):
        QSystemTrayIcon.__init__(self, QIcon(os.path.join(icons_dir(), 'icon.png')), parent)
        self.status_process = None
        self.qc_process = None
        self.c_process = None
        self.d_process = None

        self.loading = False
        self.connecting = False
        self.status = NVStatus()
        self.window = None

        self.setToolTip("NordVPN")

        self.menu = QMenu(parent)

        self.error_action = None
        self.status_action = self.menu.addAction("Loading...")
        self.status_action.setDisabled(True)

        self.menu.addSeparator()

        self.quick_connect_action = self.menu.addAction(QIcon.fromTheme("view-refresh"), "Quick Connect")
        self.quick_connect_action.triggered.connect(self.quick_connect_vpn)
        self.disconnect_action = self.menu.addAction(QIcon.fromTheme("network-offline"), "Disconnect")
        self.disconnect_action.triggered.connect(self.disconnect_vpn)
        self.last_connected_menu = self.menu.addMenu("Last connected")
        self.render_last_connected()

        self.menu.addSeparator()

        settings_action = self.menu.addAction(QIcon.fromTheme("preferences-other"), "Settings")
        settings_action.triggered.connect(self.open_settings)
        exit_action = self.menu.addAction(QIcon.fromTheme("application-exit"), "Exit")
        exit_action.triggered.connect(self.exit_app)

        self.activated.connect(self.open_settings)
        self.setContextMenu(self.menu)

        self.load_status()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_status())
        self.timer.setInterval(1000 * 60)
        self.timer.start()

    def render_last_connected(self):
        items = Config.get_last_connected()

        self.last_connected_menu.clear()
        for country, city, node in items:
            code = NV_COUNTRIES.get(country)
            label = country.replace('_', ' ')
            if node:
                label += f"#{node}"
            elif city:
                label += ' (' + city.replace('_', ' ') + ')'
            action = self.last_connected_menu.addAction(label)
            action.triggered.connect(lambda: self.connect_vpn(country, city, node))
            ico_file = os.path.join(icons_dir(), 'countries', f"{code.lower()}.png")
            if ico_file:
                action.setIcon(QIcon(ico_file))

    def update_disabled_items(self):
        self.quick_connect_action.setDisabled(self.connecting)
        self.disconnect_action.setDisabled(self.connecting)
        for action in self.last_connected_menu.actions():
            action.setDisabled(self.connecting)

    def set_loading(self, loading: bool):
        self.loading = loading

    def set_connecting(self, connecting: bool):
        self.connecting = connecting
        self.update_disabled_items()
        if self.window:
            self.window.set_connecting(connecting)

    def set_status(self, status: NVStatus):
        self.status = status
        if self.window:
            self.window.set_status(self.status)

    def set_error(self, msg: Optional[str] = None):
        if self.error_action:
            self.menu.removeAction(self.error_action)
        if msg:
            log.error(msg)
            self.error_action = QAction(QIcon.fromTheme('dialog-error'), msg)
            self.menu.insertAction(self.status_action, self.error_action)
            self.error_action.setDisabled(True)
        if self.window:
            self.window.set_connect_error(msg)

    def load_status(self):
        if self.loading:
            return

        def done(status: NVStatus):
            self.status_process = None
            self.set_status(status)
            self.set_loading(False)

            if status.status.lower() == 'connected':
                status_text = "Connected to:\n{} ({})\n{} ({})\n{} ({})\n{}\n{}".format(
                    status.country,
                    status.city,
                    status.host,
                    status.ip,
                    status.technology,
                    status.protocol,
                    status.uptime,
                    status.transfer,
                )
            else:
                status_text = status.status
            self.status_action.setText(status_text)

        def error(e):
            self.status_process = None
            self.set_loading(False)
            self.status_action.setText('')
            self.set_error(f"Load status failed: {e}")

        self.set_loading(True)
        self.status_action.setText('Loading...')
        self.status_process = StatusProcess(on_finish=done, on_error=error).run()

    def quick_connect_vpn(self):
        if self.connecting:
            return

        def done():
            self.qc_process = None
            self.set_connecting(False)
            self.update_disabled_items()
            self.load_status()

        def error(e):
            self.qc_process = None
            self.set_connecting(False)
            self.set_error(f"Quick connect failed: {e}")
            self.update_disabled_items()
            self.load_status()

        self.set_connecting(True)
        self.set_status(NVStatus("Connecting"))
        self.status_action.setText("Connecting...")
        self.update_disabled_items()
        self.qc_process = QuickConnectProcess(on_finish=done, on_error=error).run()

    def connect_vpn(self, country: str, city: Optional[str], server_number: Optional[str]):
        if self.connecting:
            return

        def done():
            self.c_process = None
            self.set_connecting(False)
            self.update_disabled_items()
            self.load_status()
            Config.add_last_connected(country, city, server_number)
            self.render_last_connected()

        def error(e):
            self.c_process = None
            self.set_connecting(False)
            self.set_error(f"Connect failed: {e}")
            self.update_disabled_items()
            self.load_status()

        self.set_connecting(True)
        self.set_status(NVStatus("Connecting"))
        self.status_action.setText("Connecting...")
        self.update_disabled_items()
        self.c_process = ConnectProcess(on_finish=done, on_error=error).run(country, city, server_number)

    def disconnect_vpn(self):
        if self.connecting:
            return

        def done():
            self.d_process = None
            self.set_connecting(False)
            self.update_disabled_items()
            self.load_status()

        def error(e):
            self.d_process = None
            self.set_connecting(False)
            self.set_error(f"Disconnect failed: {e}")
            self.update_disabled_items()
            self.load_status()

        self.set_connecting(True)
        self.set_status(NVStatus("Disconnecting"))
        self.status_action.setText("Disconnecting...")
        self.update_disabled_items()
        self.d_process = DisconnectProcess(on_finish=done, on_error=error).run()

    def open_settings(self):
        if not self.window:
            self.window = SettingsWindow(self.quick_connect_vpn, self.connect_vpn, self.disconnect_vpn)

        self.window.set_connecting(self.connecting)
        self.window.set_status(self.status)

        self.window.show()
        self.window.activateWindow()

    @staticmethod
    def exit_app():
        QCoreApplication.exit()
