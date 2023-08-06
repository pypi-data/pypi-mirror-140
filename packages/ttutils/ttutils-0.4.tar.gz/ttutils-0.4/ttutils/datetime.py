from datetime import date, datetime, timezone
from typing import Any, Union, Optional
from dateutil import parser


def utcnow() -> datetime:
    return datetime.now().astimezone(timezone.utc)


def utcnow_ms() -> datetime:
    dt = datetime.now().astimezone(timezone.utc)
    return dt.replace(microsecond=int(dt.microsecond / 1000) * 1000)


def utcnow_sec() -> datetime:
    return datetime.now().astimezone(timezone.utc).replace(microsecond=0)


def parsedt(dt: str) -> datetime:
    return parser.parse(dt).astimezone(timezone.utc)


def parsedt_ms(dt: str) -> datetime:
    _dt = parser.parse(dt).astimezone(timezone.utc)
    return _dt.replace(microsecond=int(_dt.microsecond / 1000) * 1000)


def parsedt_sec(dt: str) -> datetime:
    return parser.parse(dt).astimezone(timezone.utc).replace(microsecond=0)


def try_parsedt(dt: Any) -> Optional[datetime]:
    try:
        return parsedt(dt)
    except (ValueError, TypeError, parser.ParserError):
        return None


def isoformat(dt: Union[date, datetime]) -> str:
    if isinstance(dt, datetime):
        dt = dt.astimezone(timezone.utc)
    else:
        dt = datetime(year=dt.year, month=dt.month, day=dt.day,
            hour=0, minute=0, second=0).astimezone(timezone.utc)

    strdt = dt.isoformat().replace('+00:00', 'Z')
    strdt += 'Z' if 'Z' not in strdt else ''
    return strdt


def try_isoformat(dt: Any) -> Optional[str]:
    if not dt:
        return None
    elif isinstance(dt, (date, datetime)):
        return isoformat(dt)
    elif isinstance(dt, str):
        return dt
    elif isinstance(dt, bytes):
        return str(dt, 'utf8')
    else:
        return None
