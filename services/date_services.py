from datetime import UTC, datetime
from zoneinfo import ZoneInfo


def format_french_datetime(dt: datetime) -> str:
    """Convert a UTC datetime to a French-localized string (Europe/Paris)."""
    if dt is None:
        return "N/A"

    # DATETIME not supported in MySQL (future TIMESTAMP migration needed)
    # So we make dt aware :
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return dt.astimezone(ZoneInfo("Europe/Paris")).strftime(
        "%d/%m/%Y (%H:%M:%S)"
    )


def format_utc_datetime(dt_str: str | None) -> datetime | None:
    """Convert a French-localized datetime string back to a UTC datetime.

    Args:
        dt_str: String in format "DD/MM/YYYY (HH:MM:SS)" or "N/A"

    Returns:
        datetime in UTC, or None if input is None or "N/A"
    """
    if dt_str is None or dt_str == "N/A":
        return None

    # Parse the string to a naive datetime
    naive_dt = datetime.strptime(dt_str, "%d/%m/%Y (%H:%M:%S)").replace(
        tzinfo=ZoneInfo("Europe/Paris")
    )

    # Interpret as Europe/Paris and convert to UTC
    return naive_dt.astimezone(UTC)
