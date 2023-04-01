from dataclasses import dataclass
from typing import Optional
from .Process import Process
from .utils import parse_options_list


@dataclass
class Account:
    email: Optional[str] = None
    status: Optional[str] = None


class AccountProcess(Process[Account]):
    def run(self):
        return super()._start_process(['account'])

    def _parse_output(self, data: str) -> Account:
        attr_map = {
            "email": "Email Address",
            "status": "VPN Service",
        }

        return parse_options_list(data, attr_map, Account())
