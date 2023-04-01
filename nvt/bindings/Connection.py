from typing import Optional
from dataclasses import dataclass
from .utils import parse_options_list
from .Process import Process
from .Countries import NV_COUNTRIES


@dataclass
class NVStatus:
    status: str = "Disconnected"
    country: Optional[str] = None
    city: Optional[str] = None
    host: Optional[str] = None
    ip: Optional[str] = None
    technology: Optional[str] = None
    protocol: Optional[str] = None
    transfer: Optional[str] = None
    uptime: Optional[str] = None


class StatusProcess(Process[NVStatus]):
    def run(self):
        return super()._start_process(['status'])

    def _parse_output(self, data: str) -> NVStatus:
        attr_map = {
            "status": "Status",
            "country": "Country",
            "city": "City",
            "host": "Hostname",
            "ip": "IP",
            "technology": "Current technology",
            "protocol": "Current protocol",
            "transfer": "Transfer",
            "uptime": "Uptime",
        }

        return parse_options_list(data, attr_map, NVStatus())


class QuickConnectProcess(Process[None]):
    def run(self, country: Optional[str]):
        params = ['connect']
        if country:
            params.append(country)
        return super()._start_process(params)


class ConnectProcess(Process[None]):
    def run(self, country: str, city: Optional[str], server_number: Optional[str]):
        params = ["connect"]
        if server_number:
            country_code = NV_COUNTRIES.get(country)
            if not country_code:
                return
            params.append(f"{country_code}{server_number}")
        else:
            params.append(country)
            if city:
                params.append(city)

        return super()._start_process(params)


class DisconnectProcess(Process[None]):
    def run(self):
        return super()._start_process(["disconnect"])
