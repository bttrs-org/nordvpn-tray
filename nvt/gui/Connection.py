import os
import logging
from typing import Optional, Callable
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QIntValidator
from PySide6.QtWidgets import QWidget, QPushButton, QListWidget, QListWidgetItem, QGridLayout, QLabel, QHBoxLayout, \
    QVBoxLayout, QLineEdit
from nvt.utils import icons_dir
from nvt.bindings import CountriesProcess, CitiesProcess, NVStatus
from nvt.gui.ErrorRow import ErrorRow

log = logging.getLogger(__name__)


class CountryListItem(QListWidgetItem):
    country: str

    def __init__(self, country: str, code: str):
        super().__init__(country.replace("_", " "))
        self.country = country
        if code:
            ico_file = os.path.join(icons_dir(), 'countries', f"{code.lower()}.png")
            self.setIcon(QIcon(ico_file))


class CityListItem(QListWidgetItem):
    city: str

    def __init__(self, city: str):
        super().__init__(city.replace("_", " "))
        self.city = city


class Connection(QWidget):
    connecting: bool
    selected_country: Optional[str]

    quick_connect_vpn: Callable[[], None]
    connect_vpn: Callable[[str, Optional[str], Optional[str]], None]
    disconnect_vpn: Callable[[], None]

    status_text: QLabel
    countries_list: QListWidget
    cities_list: QListWidget
    quick_connect_btn: QPushButton
    connect_btn: QPushButton
    error_row: ErrorRow

    def __init__(self, parent, quick_connect_vpn: Callable[[], None],
                 connect_vpn: Callable[[str, Optional[str], Optional[str]], None], disconnect_vpn: Callable[[], None]):
        super().__init__(parent)
        self.connecting = False
        self.selected_country = None

        self.quick_connect_vpn = quick_connect_vpn
        self.connect_vpn = connect_vpn
        self.disconnect_vpn = disconnect_vpn

        self.countries_process = None
        self.cities_process = None

        self.status_text = QLabel("Status")

        self.quick_connect_btn = QPushButton(QIcon.fromTheme("view-refresh"), "Quick Connect")
        self.quick_connect_btn.clicked.connect(self.quick_connect_vpn)

        self.connect_btn = QPushButton(QIcon.fromTheme("network-transmit"), "Connect")
        self.connect_btn.setDisabled(True)
        self.connect_btn.clicked.connect(self._on_connect_click)

        self.disconnect_btn = QPushButton(QIcon.fromTheme("network-offline"), "Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_vpn)

        self.countries_list = QListWidget(self)
        self.countries_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.countries_list.itemSelectionChanged.connect(self._on_country_selected)

        self.cities_list = QListWidget(self)
        self.cities_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        self.server_input = QLineEdit(self)
        self.server_input.setPlaceholderText("123")
        self.server_input.setValidator(QIntValidator(bottom=0))

        # LAYOUTS
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)

        top_panel = QVBoxLayout()
        top_panel.addWidget(self.status_text)
        top_panel.addWidget(self.quick_connect_btn, 0, Qt.AlignmentFlag.AlignRight)
        top_panel.setSpacing(10)
        top_panel.setContentsMargins(5, 5, 5, 5)
        main_layout.addLayout(top_panel, 0, 0, 1, 2)

        main_layout.addWidget(self.countries_list, 2, 0)
        main_layout.addWidget(self.cities_list, 2, 1)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Server #"))
        input_layout.addSpacing(10)
        input_layout.addWidget(self.server_input)
        main_layout.addLayout(input_layout, 3, 0, 1, 2)

        bottom_panel = QHBoxLayout()
        bottom_panel.addStretch()
        bottom_panel.addWidget(self.disconnect_btn)
        bottom_panel.addWidget(self.connect_btn)
        bottom_panel.setSpacing(10)
        bottom_panel.setContentsMargins(5, 5, 5, 5)
        main_layout.addLayout(bottom_panel, 4, 0, 1, 2)

        self.error_row = ErrorRow()
        main_layout.addWidget(self.error_row, 5, 0, 1, 2)

        self.setLayout(main_layout)

        self.load_countries()

    def update_disabled_buttons(self):
        if self.selected_country and not self.connecting:
            self.connect_btn.setDisabled(False)
        else:
            self.connect_btn.setDisabled(True)

        if not self.connecting:
            self.disconnect_btn.setDisabled(False)
            self.quick_connect_btn.setDisabled(False)
        else:
            self.disconnect_btn.setDisabled(True)
            self.quick_connect_btn.setDisabled(True)

    def set_connecting(self, connecting: bool):
        self.connecting = connecting
        self.update_disabled_buttons()

    def set_error(self, msg: Optional[str] = None):
        if msg:
            self.error_row.set_msg(msg)
        else:
            self.error_row.clear()

    def set_status(self, status: NVStatus):
        if status is None:
            status_text = "Loading..."
        elif status.status.lower() == "connected":
            status_text = f"""Connected to: {status.country}, {status.city}
{status.host} ({status.ip}) {status.technology} ({status.protocol})
Connected {status.uptime}, {status.transfer}"""
        else:
            status_text = f"{status.status}\n\n"

        self.status_text.setText(status_text)

    def load_countries(self):
        if self.cities_process:
            return
        self.set_error()

        def done(countries):
            self.countries_process = None
            if not countries:
                return
            self.countries_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
            self.countries_list.clear()
            for country, code in countries:
                row = CountryListItem(country, code)
                self.countries_list.addItem(row)
            self.countries_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        def error(e):
            self.countries_process = None
            self.set_error(f"Load countries failed: {e}")

        self.countries_process = CountriesProcess(on_finish=done, on_error=error).run()

    def load_cities(self):
        if self.cities_process:
            self.cities_process.close()
        self.set_error()

        def done(cities):
            self.cities_process = None
            self.cities_list.clear()
            if not cities:
                return
            self.cities_list.addItem(QListWidgetItem('# fastest'))
            for city in cities:
                row = CityListItem(city)
                self.cities_list.addItem(row)

        def error(e):
            self.cities_process = None
            self.set_error(f"Load cities failed: {e}")

        self.cities_process = CitiesProcess(on_finish=done, on_error=error).run(self.selected_country)

    def _on_country_selected(self):
        self.cities_list.clear()
        if self.countries_list.selectedItems():
            self.selected_country = self.countries_list.selectedItems()[0].country
            self.load_cities()
        else:
            self.selected_country = None

        self.update_disabled_buttons()

    def _on_connect_click(self):
        selected_countries = self.countries_list.selectedItems()
        selected_cities = self.cities_list.selectedItems()

        if not selected_countries:
            return

        country = selected_countries[0].country
        city = None
        if selected_cities and isinstance(selected_cities[0], CityListItem):
            city = selected_cities[0].city
        server_number = self.server_input.text()
        self.connect_vpn(country, city, server_number)
