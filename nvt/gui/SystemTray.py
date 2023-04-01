import logging
from typing import Optional
from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from nvt import Config
from nvt.utils import country_icon, svg_icon, png_icon
from nvt.Config import get_quick_connect
from nvt.bindings import StatusProcess, QuickConnectProcess, NVStatus, DisconnectProcess, ConnectProcess
from nvt.bindings.Countries import NV_COUNTRIES
from .SettingsWindow import SettingsWindow

log = logging.getLogger(__name__)


class SystemTray(QSystemTrayIcon):
    loading: bool
    connecting: bool
    status: NVStatus
    main_window: Optional[SettingsWindow]
    error_action: Optional[QAction]
    status_action: QAction
    quick_connect_action: QAction
    disconnect_action: QAction
    last_connected_menu: QMenu
    timer: QTimer

    def __init__(self, parent):
        QSystemTrayIcon.__init__(self, png_icon('icon'), parent)
        self.status_process = None
        self.qc_process = None
        self.c_process = None
        self.d_process = None

        self.loading = False
        self.connecting = False
        self.status = NVStatus()
        self.main_window = None

        self.setToolTip("NordVPN")

        self.menu = QMenu(parent)

        self.error_action = None
        self.status_action = self.menu.addAction("Loading...")
        self.status_action.setDisabled(True)

        self.menu.addSeparator()

        self.quick_connect_action = self.menu.addAction(svg_icon('reconnect'), "Quick Connect")
        self.quick_connect_action.triggered.connect(self._quick_connect_vpn)
        self.disconnect_action = self.menu.addAction(svg_icon('disconnect'), "Disconnect")
        self.disconnect_action.triggered.connect(self._disconnect_vpn)
        self.last_connected_menu = self.menu.addMenu("Last connected")
        self._render_last_connected()

        self.menu.addSeparator()

        settings_action = self.menu.addAction(svg_icon('settings'), "Settings")
        settings_action.triggered.connect(self._open_settings)
        exit_action = self.menu.addAction(svg_icon('exit'), "Exit")
        exit_action.triggered.connect(self._exit_app)

        self.activated.connect(self._open_settings)
        self.setContextMenu(self.menu)

        self._load_status()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._load_status)
        self.timer.start(1000 * 60)

    def _render_last_connected(self):
        items = Config.get_last_connected()

        self.last_connected_menu.clear()

        def create_cb(country: str, city: Optional[str], node: Optional[str]):
            return lambda: self._connect_vpn(country, city, node)

        for country, city, node in items:
            code = NV_COUNTRIES.get(country)
            label = country.replace('_', ' ')
            if node:
                label += f"#{node}"
            elif city:
                label += ' (' + city.replace('_', ' ') + ')'
            action = self.last_connected_menu.addAction(label)
            icon = country_icon(code)
            if icon:
                action.setIcon(icon)
            action.triggered.connect(create_cb(country, city, node))

    def _update_disabled_items(self):
        self.quick_connect_action.setDisabled(self.connecting)
        self.disconnect_action.setDisabled(self.connecting)
        for action in self.last_connected_menu.actions():
            action.setDisabled(self.connecting)

    def _set_loading(self, loading: bool):
        self.loading = loading

    def _set_connecting(self, connecting: bool):
        self.connecting = connecting
        self._update_disabled_items()
        if self.main_window:
            self.main_window.set_connecting(connecting)

    def _set_status(self, status: NVStatus):
        self.status = status
        if self.main_window:
            self.main_window.set_status(self.status)

    def _set_error(self, msg: Optional[str] = None):
        if self.error_action:
            self.menu.removeAction(self.error_action)
        if msg:
            log.error(msg)
            self.error_action = QAction(svg_icon('error'), msg)
            self.menu.insertAction(self.status_action, self.error_action)
            self.error_action.setDisabled(True)
        if self.main_window:
            self.main_window.set_connect_error(msg)

    def _load_status(self):
        if self.loading:
            return

        def done(status: NVStatus):
            self.status_process = None
            self._set_status(status)
            self._set_loading(False)

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
                self.setIcon(png_icon('icon_connected'))
            elif status.status.lower() == 'disconnected':
                status_text = status.status
                self.setIcon(png_icon('icon_disconnected'))
            else:
                status_text = status.status
                self.setIcon(png_icon('icon'))
            self.status_action.setText(status_text)

        def error(e):
            self.status_process = None
            self._set_loading(False)
            self.status_action.setText('')
            self._set_error(f"Load status failed: {e}")

        self._set_loading(True)
        self.status_action.setText('Loading...')
        self.status_process = StatusProcess(on_finish=done, on_error=error).run()

    def _quick_connect_vpn(self):
        if self.connecting:
            return

        def done():
            self.qc_process = None
            self._set_connecting(False)
            self._update_disabled_items()
            self._load_status()

        def error(e):
            self.qc_process = None
            self._set_connecting(False)
            self._set_error(f"Quick connect failed: {e}")
            self._update_disabled_items()
            self._load_status()

        self._set_connecting(True)
        self._set_status(NVStatus("Connecting"))
        self.status_action.setText("Connecting...")
        self._update_disabled_items()
        country = get_quick_connect()
        self.qc_process = QuickConnectProcess(on_finish=done, on_error=error).run(country)

    def _connect_vpn(self, country: str, city: Optional[str], server_number: Optional[str]):
        if self.connecting:
            return

        def done():
            self.c_process = None
            self._set_connecting(False)
            self._update_disabled_items()
            self._load_status()
            Config.add_last_connected(country, city, server_number)
            self._render_last_connected()

        def error(e):
            self.c_process = None
            self._set_connecting(False)
            self._set_error(f"Connect failed: {e}")
            self._update_disabled_items()
            self._load_status()

        self._set_connecting(True)
        self._set_status(NVStatus("Connecting"))
        self.status_action.setText("Connecting...")
        self._update_disabled_items()
        self.c_process = ConnectProcess(on_finish=done, on_error=error).run(country, city, server_number)

    def _disconnect_vpn(self):
        if self.connecting:
            return

        def done():
            self.d_process = None
            self._set_connecting(False)
            self._update_disabled_items()
            self._load_status()

        def error(e):
            self.d_process = None
            self._set_connecting(False)
            self._set_error(f"Disconnect failed: {e}")
            self._update_disabled_items()
            self._load_status()

        self._set_connecting(True)
        self._set_status(NVStatus("Disconnecting"))
        self.status_action.setText("Disconnecting...")
        self._update_disabled_items()
        self.d_process = DisconnectProcess(on_finish=done, on_error=error).run()

    def _open_settings(self):
        if not self.main_window:
            self.main_window = SettingsWindow(self._quick_connect_vpn, self._connect_vpn, self._disconnect_vpn)

        self.main_window.set_connecting(self.connecting)
        self.main_window.set_status(self.status)
        self.main_window.show()
        self.main_window.activateWindow()

    @staticmethod
    def _exit_app():
        QCoreApplication.exit()
