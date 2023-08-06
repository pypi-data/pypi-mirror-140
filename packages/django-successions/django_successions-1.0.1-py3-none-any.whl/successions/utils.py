import re
from datetime import datetime


FIXTURES = {
    "%year%": lambda: datetime.now().year,
    "%month%": lambda: datetime.now().month,
    "%day%": lambda: datetime.now().day,
}

REGEXS = {
    "%year%": "\d{4}",
    "%month%": "\d{2}",
    "%day%": "\d{2}",
}


def generate_next_value(
    current: int, increment: int, padding: int, prefix: str = "", suffix: str = ""
):
    next_number = current + increment if current else increment
    fixtures = {
        **FIXTURES,
        "%number%": lambda: str(next_number).zfill(padding),
    }
    next_value = "{}%number%{}".format(prefix, suffix)
    for replace, func in fixtures.items():
        next_value = next_value.replace(replace, str(func()))

    return next_value, next_number


def get_number_from_value(value: str, prefix: str = "", suffix: str = ""):
    regexs = {**REGEXS, "%number%": "(?P<number>\d+)"}
    pattern = "{}%number%{}".format(prefix, suffix)
    for replace, regex in regexs.items():
        pattern = pattern.replace(replace, regex)

    matcher = re.search(pattern, value, re.I)

    if matcher:
        number = matcher.group("number")
        return int(number)

    return matcher
