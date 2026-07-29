from langchain_core.tools import tool
from pydantic import BaseModel, Field


class ParseDateInput(BaseModel):
    date_string: str = Field(description="Date string to parse (e.g. '2024-01-15', 'Jan 15, 2024')")


@tool(args_schema=ParseDateInput)
def parse_date(date_string: str) -> str:
    """Parse a natural language date string into ISO format.

    Args:
        date_string: Date string in common formats.

    Returns:
        ISO-formatted date with detected format.
    """
    try:
        from dateutil import parser
    except ImportError:
        return "Error: python-dateutil is required. Install with: pip install crew-tools[templates]"

    try:
        dt = parser.parse(date_string)
        return dt.isoformat()
    except (ValueError, OverflowError, TypeError):
        pass

    try:
        import parsedatetime
        cal = parsedatetime.Calendar()
        dt, status = cal.parse(date_string)
        if status > 0:
            from datetime import datetime, timezone
            return datetime(*dt[:6], tzinfo=timezone.utc).isoformat()
    except ImportError:
        pass

    return f"Error: could not parse date: {date_string}"


class FormatDateInput(BaseModel):
    date_string: str = Field(description="Date string to format")
    output_format: str = Field(default="%Y-%m-%d", description="strftime output format")


@tool(args_schema=FormatDateInput)
def format_date(date_string: str, output_format: str = "%Y-%m-%d") -> str:
    """Parse and reformat a date string.

    Args:
        date_string: Date string in common formats.
        output_format: strftime format string.

    Returns:
        Reformatted date string.
    """
    try:
        from dateutil import parser
    except ImportError:
        return "Error: python-dateutil is required. Install with: pip install crew-tools[templates]"

    try:
        dt = parser.parse(date_string)
        return dt.strftime(output_format)
    except (ValueError, OverflowError) as e:
        return f"Error: could not parse date: {e}"
    except Exception as e:
        return f"Error formatting date: {e}"


class TimezoneConvertInput(BaseModel):
    date_string: str = Field(description="Date string to convert")
    from_tz: str = Field(default="UTC", description="Source timezone (e.g. 'US/Eastern', 'Europe/London')")
    to_tz: str = Field(default="UTC", description="Target timezone")


@tool(args_schema=TimezoneConvertInput)
def timezone_convert(date_string: str, from_tz: str = "UTC", to_tz: str = "UTC") -> str:
    """Convert a date/time between timezones.

    Args:
        date_string: Date string to convert.
        from_tz: Source timezone name.
        to_tz: Target timezone name.

    Returns:
        Converted date/time in ISO format.
    """
    try:
        from dateutil import parser
    except ImportError:
        return "Error: python-dateutil is required."

    try:
        import pytz
    except ImportError:
        return "Error: pytz is required. Install with: pip install crew-tools[templates]"

    try:
        dt = parser.parse(date_string)
        if dt.tzinfo is None:
            src_tz = pytz.timezone(from_tz)
            dt = src_tz.localize(dt)
        dst_tz = pytz.timezone(to_tz)
        converted = dt.astimezone(dst_tz)
        return converted.isoformat()
    except Exception as e:
        return f"Error converting timezone: {e}"


class CurrentTimeInput(BaseModel):
    timezone: str = Field(default="UTC", description="Timezone name (e.g. 'US/Eastern', 'Asia/Tokyo')")
    output_format: str = Field(default="%Y-%m-%d %H:%M:%S %Z", description="strftime output format")


@tool(args_schema=CurrentTimeInput)
def current_time(timezone: str = "UTC", output_format: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    """Get the current date and time in a specified timezone.

    Args:
        timezone: Timezone name.
        output_format: strftime format string.

    Returns:
        Current date/time string.
    """
    from datetime import datetime
    from datetime import timezone as tz_mod

    try:
        import pytz
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime(output_format)
    except Exception:
        pass

    try:
        dt = datetime.now(tz_mod.utc)
        return dt.strftime(output_format)
    except Exception as e:
        return f"Error getting current time: {e}"
