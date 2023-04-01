from typing import Optional
from dataclasses import dataclass
from .utils import parse_options_list
from .Process import Process


@dataclass
class NVSettings:
    autoconnect: Optional[bool] = None
    technology: Optional[str] = None
    protocol: Optional[str] = None
    firewall: Optional[bool] = None
    fwmark: Optional[str] = None
    routing: Optional[bool] = None
    analytics: Optional[bool] = None
    killswitch: Optional[bool] = None
    tplite: Optional[bool] = None
    notify: Optional[bool] = None
    ipv6: Optional[bool] = None
    meshnet: Optional[bool] = None
    dns: Optional[bool] = None


class SettingsProcess(Process[NVSettings]):
    def run(self):
        return super()._start_process(['settings'])

    def _parse_output(self, data: str) -> NVSettings:
        attr_map = {
            'autoconnect': 'Auto-connect',
            'technology': 'Technology',
            'protocol': 'Protocol',
            'firewall': 'Firewall',
            'fwmark': 'Firewall Mark',
            'routing': 'Routing',
            'analytics': 'Analytics',
            'killswitch': 'Kill Switch',
            'tplite': 'Threat Protection Lite',
            'notify': 'Notify',
            'ipv6': 'IPv6',
            'meshnet': 'Meshnet',
            'dns': 'DNS',
        }

        return parse_options_list(data, attr_map, NVSettings())
