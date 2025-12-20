import os
import re
from datetime import datetime

# Month dictionary for parsing dates in format "DD Mon YYYY"
MONTH_DICT = {
    'Jan': '01', 'January': '01',
    'Feb': '02', 'February': '02',
    'Mar': '03', 'March': '03',
    'Apr': '04', 'April': '04',
    'May': '05',
    'Jun': '06', 'June': '06',
    'Jul': '07', 'July': '07',
    'Aug': '08', 'August': '08',
    'Sep': '09', 'Sept': '09', 'September': '09',
    'Oct': '10', 'October': '10',
    'Nov': '11', 'November': '11',
    'Dec': '12', 'December': '12'
}

def format_size(size_bytes):
    """Converts bytes to human readable string (B, KB, MB, GB, TB)."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def parse_date_dmy(date_str):
    """
    Parses date strings in format "DD Mon YYYY" (e.g., "03 Oct 2023").
    Returns a datetime object if successful, None otherwise.
    
    Args:
        date_str: String containing date in "DD Mon YYYY" format
        
    Returns:
        datetime object or None if parsing fails
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    # Remove extra whitespace
    date_str = date_str.strip()
    
    # Pattern for "DD Mon YYYY" format (e.g., "03 Oct 2023")
    pattern = r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})'
    match = re.search(pattern, date_str)
    
    if not match:
        return None
    
    day = match.group(1).zfill(2)  # Pad with zero if needed
    month_name = match.group(2)
    year = match.group(3)
    
    # Look up month number
    month_num = MONTH_DICT.get(month_name) or MONTH_DICT.get(month_name.capitalize())
    
    if not month_num:
        return None
    
    try:
        # Create datetime object to validate the date
        date_obj = datetime.strptime(f"{year}-{month_num}-{day}", "%Y-%m-%d")
        return date_obj
    except ValueError:
        return None

def validate_date(date_str):
    """
    Validates if a date string is in correct format and represents a valid date.
    Supports multiple formats including "DD Mon YYYY", "DD/MM/YYYY", "YYYY-MM-DD".
    
    Args:
        date_str: String to validate as date
        
    Returns:
        Tuple of (is_valid: bool, parsed_date: datetime or None, format_used: str)
    """
    if not date_str or not isinstance(date_str, str):
        return (False, None, "")
    
    date_str = date_str.strip()
    
    # Try parsing "DD Mon YYYY" format first
    parsed = parse_date_dmy(date_str)
    if parsed:
        return (True, parsed, "DD Mon YYYY")
    
    # Try other common formats
    formats_to_try = [
        ("%d/%m/%Y", "DD/MM/YYYY"),
        ("%Y-%m-%d", "YYYY-MM-DD"),
        ("%d-%m-%Y", "DD-MM-YYYY"),
        ("%m/%d/%Y", "MM/DD/YYYY"),
    ]
    
    for fmt, fmt_name in formats_to_try:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return (True, parsed, fmt_name)
        except ValueError:
            continue
    
    return (False, None, "")

def get_files_map(directory):
    """
    Scans a directory and returns a dictionary mapping basenames (no extension)
    to a list of full filenames.
    Example: {'report': ['report.pdf', 'report.docx']}
    """
    files_map = {} 
    if not os.path.exists(directory):
        print(f"Error: Directory not found: {directory}")
        return files_map
    
    try:
        for f in os.listdir(directory):
            full_path = os.path.join(directory, f)
            if os.path.isfile(full_path):
                base_name = os.path.splitext(f)[0]
                if base_name not in files_map:
                    files_map[base_name] = []
                files_map[base_name].append(f)
    except Exception as e:
        print(f"Error reading {directory}: {e}")
    return files_map

def read_file(path):
    """Reads a text file and returns its content as a stripped string."""
    if not os.path.exists(path):
        return f"[Error: File not found - {path}]"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        return f"[Error reading {path}: {e}]"

def ensure_dir_exists(directory):
    """Creates the directory if it does not exist."""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            return True
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            return False
    return True
