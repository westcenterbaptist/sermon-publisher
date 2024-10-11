import re
from datetime import datetime

def end_with_slash(path):
    if not path.endswith('/'):
        path += '/'
    return path

def strip_break(string):
    return string.split('<br/>')

def remove_ordinal_suffix(date_str):
    """
    Removes ordinal suffixes from day numbers in a date string.
    
    :param date_str: The original date string (e.g., "October 6th, 2024").
    :return: Cleaned date string without ordinal suffixes (e.g., "October 6, 2024").
    """
    # Regular expression pattern to match ordinal suffixes
    pattern = r'(\d{1,2})(st|nd|rd|th)'
    return re.sub(pattern, r'\1', date_str)

def convert_to_iso(date_str):
    """
    Converts a date string with ordinal suffixes to ISO 8601 format.
    
    :param date_str: The original date string (e.g., "October 6th, 2024").
    :return: ISO formatted date string (e.g., "2024-10-06T00:00:00").
    """
    # Step 1: Remove ordinal suffixes
    clean_date_str = remove_ordinal_suffix(date_str)
    
    # Step 2: Define the original format
    original_format = "%B %d, %Y"  # e.g., "October 6, 2024"
    
    # Step 3: Parse the cleaned date string into a datetime object
    try:
        date_obj = datetime.strptime(clean_date_str, original_format)
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return None
    
    # Step 4: Convert to ISO 8601 format with time set to midnight
    iso_format = date_obj.strftime("%Y-%m-%dT%H:%M:%S")
    return iso_format
