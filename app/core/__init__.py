from datetime import date, datetime
from typing import Optional


def parse_date(value: Optional[str]) -> Optional[date]:
    if value is None:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return date.fromisoformat(value)
