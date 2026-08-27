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
