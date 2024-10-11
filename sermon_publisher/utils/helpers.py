import os
import re
from datetime import datetime
from typing import Optional

def end_with_slash(path: str) -> str:
    """
    Ensures the path ends with a slash.

    :param path: The original path.
    :return: Path ending with a slash.
    """
    return path if path.endswith('/') else f"{path}/"

def strip_break(string: str) -> list:
    """
    Splits a string by <br/> tags.

    :param str string: The original string.
    :return: List of substrings.
    """
    return string.split('<br/>')

def remove_ordinal_suffix(date_str: str) -> str:
    """
    Removes ordinal suffixes from day numbers in a date string.

    :param str date_str: The original date string (e.g., "October 6th, 2024").
    :return: Cleaned date string without ordinal suffixes (e.g., "October 6, 2024").
    """
    pattern = r'(\d{1,2})(st|nd|rd|th)'
    return re.sub(pattern, r'\1', date_str)

def convert_to_iso(date_str: str) -> Optional[str]:
    """
    Converts a date string with ordinal suffixes to ISO 8601 format.

    :param date_str: The original date string (e.g., "October 6th, 2024").
    :return: ISO formatted date string (e.g., "2024-10-06T00:00:00").
    """
    clean_date_str = remove_ordinal_suffix(date_str)
    original_format = "%B %d, %Y"  # e.g., "October 6, 2024"

    try:
        date_obj = datetime.strptime(clean_date_str, original_format)
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return None

    return date_obj.strftime("%Y-%m-%dT%H:%M:%S")
