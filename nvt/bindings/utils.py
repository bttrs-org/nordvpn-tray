import re
from typing import TypeVar, Dict, List

T = TypeVar('T')


def parse_string_list(data: str) -> List[str]:
    lines = data.splitlines(False)

    content_line = lines.pop().strip()
    while not content_line:
        content_line = lines.pop().strip()

    items = []
    tokens = content_line.split(",")
    for t in tokens:
        items.append(t.strip())

    return items


def parse_options_list(lines_str: str, attr_map: Dict[str, str], obj: T) -> T:
    lines = lines_str.splitlines(False)
    for line in lines:
        for attr, label in attr_map.items():
            result = re.search(label + r":\s*(?P<value>.*)", line, re.IGNORECASE)
            if result is not None:
                value = result.groupdict()["value"].strip()
                if value:
                    setattr(obj, attr, value)
                break
    return obj
