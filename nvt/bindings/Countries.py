from typing import Optional
from PySide6.QtGui import QIcon
from nvt.utils import country_icon
from .Process import Process
from .utils import parse_string_list

NV_COUNTRIES = {
    'Albania': 'AL', 'Argentina': 'AR', 'Australia': 'AU', 'Austria': 'AT', 'Belgium': 'BE',
    'Bosnia_And_Herzegovina': 'BA', 'Brazil': 'BR', 'Bulgaria': 'BG', 'Canada': 'CA', 'Chile': 'CL', 'Colombia': 'CO',
    'Costa_Rica': 'CR', 'Croatia': 'HR', 'Cyprus': 'CY', 'Czech_Republic': 'CZ', 'Denmark': 'DK', 'Estonia': 'EE',
    'Finland': 'FI', 'France': 'FR', 'Georgia': 'GE', 'Germany': 'DE', 'Greece': 'GR', 'Hong_Kong': 'HK',
    'Hungary': 'HU', 'Iceland': 'IS', 'Indonesia': 'ID', 'Ireland': 'IE', 'Israel': 'IL', 'Italy': 'IT', 'Japan': 'JP',
    'Latvia': 'LV', 'Lithuania': 'LT', 'Luxembourg': 'LU', 'Malaysia': 'MY', 'Mexico': 'MX', 'Moldova': 'MD',
    'Netherlands': 'NL', 'New_Zealand': 'NZ', 'North_Macedonia': 'MK', 'Norway': 'NO', 'Poland': 'PL', 'Portugal': 'PT',
    'Romania': 'RO', 'Serbia': 'RS', 'Singapore': 'SG', 'Slovakia': 'SK', 'Slovenia': 'SI', 'South_Africa': 'ZA',
    'South_Korea': 'KR', 'Spain': 'ES', 'Sweden': 'SE', 'Switzerland': 'CH', 'Taiwan': 'TW', 'Thailand': 'TH',
    'Turkey': 'TR', 'Ukraine': 'UA', 'United_Kingdom': 'GB', 'United_States': 'US', 'Vietnam': 'VN',
}


class CountriesProcess(Process[list[tuple[str, Optional[str], Optional[QIcon]]]]):
    def run(self):
        return super()._start_process(['countries'])

    def _parse_output(self, data: str) -> list[tuple[str, Optional[str], Optional[QIcon]]]:
        """
        Returns: List of (country, country_code, icon_path)
        """
        country_names = parse_string_list(data)
        countries = []
        for name in country_names:
            code = NV_COUNTRIES.get(name)
            ico_file = country_icon(code)
            countries.append((name, code, ico_file))

        return countries
