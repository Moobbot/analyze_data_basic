import os
import re
from datetime import datetime

# Month dictionary for parsing dates in format "DD Mon YYYY"
MONTH_DICT = {
    "Jan": "01",
    "January": "01",
    "Feb": "02",
    "February": "02",
    "Mar": "03",
    "March": "03",
    "Apr": "04",
    "April": "04",
    "May": "05",
    "Jun": "06",
    "June": "06",
    "Jul": "07",
    "July": "07",
    "Aug": "08",
    "August": "08",
    "Sep": "09",
    "Sept": "09",
    "September": "09",
    "Oct": "10",
    "October": "10",
    "Nov": "11",
    "November": "11",
    "Dec": "12",
    "December": "12",
}


def format_size(size_bytes):
    """Converts bytes to human readable string (B, KB, MB, GB, TB)."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def parse_date_dmy(date_str):
    """
    Parses date strings in formats:
    - "DD Mon YYYY" (e.g., "03 Oct 2023")
    - "DD-Mon-YY" (e.g., "31-Jul-21")
    Returns a datetime object if successful, None otherwise.

    Args:
        date_str: String containing date in supported formats

    Returns:
        datetime object or None if parsing fails
    """
    if not date_str or not isinstance(date_str, str):
        return None

    # Remove extra whitespace
    date_str = date_str.strip()

    # Pattern 1: "DD Mon YYYY" format (e.g., "03 Oct 2023")
    pattern1 = r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})"
    match = re.search(pattern1, date_str)

    if match:
        day = match.group(1).zfill(2)  # Pad with zero if needed
        month_name = match.group(2)
        year = match.group(3)

        # Look up month number
        month_num = MONTH_DICT.get(month_name) or MONTH_DICT.get(
            month_name.capitalize()
        )

        if month_num:
            try:
                # Create datetime object to validate the date
                date_obj = datetime.strptime(f"{year}-{month_num}-{day}", "%Y-%m-%d")
                return date_obj
            except ValueError:
                pass

    # Pattern 2: "DD-Mon-YY" format (e.g., "31-Jul-21")
    pattern2 = r"(\d{1,2})-([A-Za-z]+)-(\d{2})"
    match = re.search(pattern2, date_str)

    if match:
        day = match.group(1).zfill(2)
        month_name = match.group(2)
        year_2digit = match.group(3)

        # Convert 2-digit year to 4-digit (assuming 2000s for years 00-99)
        year_int = int(year_2digit)
        if year_int >= 0 and year_int <= 99:
            # Assume years 00-50 are 2000-2050, 51-99 are 1951-1999
            year = f"{2000 + year_int if year_int <= 50 else 1900 + year_int}"
        else:
            return None

        # Look up month number
        month_num = MONTH_DICT.get(month_name) or MONTH_DICT.get(
            month_name.capitalize()
        )

        if month_num:
            try:
                # Create datetime object to validate the date
                date_obj = datetime.strptime(f"{year}-{month_num}-{day}", "%Y-%m-%d")
                return date_obj
            except ValueError:
                pass

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
        ("%Y.%m.%d", "YYYY.MM.DD"),
        ("%d/%m/%y", "DD/MM/YY"),
        ("%Y%m%d", "YYYYMMDD"),
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
        with open(path, "r", encoding="utf-8") as f:
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


def list_files_recursive(directory, extension):
    """
    List files with specific extension recursively (all levels).
    Returns matched files with relative paths from the directory.
    """
    files = []
    if not os.path.exists(directory):
        return files

    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(extension.lower()):
                # Get full path
                full_path = os.path.join(root, filename)
                # Get relative path from valid directory
                rel_path = os.path.relpath(full_path, directory)
                files.append(rel_path)
    return files


def get_files_map_recursive(directory):
    """
    Scans a directory recursively and returns a dictionary mapping basenames
    (relative path without extension) to a list of full relative filenames.

    Normalizes case to handle directory casing differences.
    Example: {'subdir/report': ['subdir/report.pdf', 'subdir/report.json']}

    Args:
        directory: Root directory to scan

    Returns:
        Dictionary mapping normalized base paths to list of relative file paths
    """
    files_map = {}
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return files_map

    for root, _, files in os.walk(directory):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, directory)
            # Use relative path without extension as key to match structure
            # Normalize case to handle directory casing differences (Leuco vs leuco)
            base_name = os.path.normcase(os.path.splitext(rel_path)[0])

            if base_name not in files_map:
                files_map[base_name] = []
            files_map[base_name].append(rel_path)
    return files_map


def copy_file_and_label(
    filename,
    dest_folder_files,
    dest_folder_labels,
    source_files_dir=None,
    source_labels_dir=None,
):
    """
    Copy both a file and its corresponding JSON label to destination folders.

    Args:
        filename: Name of the file (typically PDF)
        dest_folder_files: Destination folder for files
        dest_folder_labels: Destination folder for JSON label files
        source_files_dir: Source directory for files (defaults to config.DATASET_DIR)
        source_labels_dir: Source directory for labels (defaults to config.LABEL_DIR)

    Returns:
        Tuple of (file_copied: bool, label_copied: bool)
    """
    import config
    import shutil

    if source_files_dir is None:
        source_files_dir = config.DATASET_DIR
    if source_labels_dir is None:
        source_labels_dir = config.LABEL_DIR

    file_copied = False
    label_copied = False

    # Copy main file
    source_file = os.path.join(source_files_dir, filename)
    dest_file = os.path.join(dest_folder_files, filename)

    # Ensure dest dir exists
    ensure_dir_exists(os.path.dirname(dest_file))

    if os.path.exists(source_file):
        try:
            shutil.copy2(source_file, dest_file)
            file_copied = True
        except Exception as e:
            print(f"  Error copying file {filename}: {e}")

    # Copy corresponding JSON label
    label_filename = os.path.splitext(filename)[0] + ".json"
    source_label = os.path.join(source_labels_dir, label_filename)
    dest_label = os.path.join(dest_folder_labels, label_filename)

    # Ensure dest label dir exists
    ensure_dir_exists(os.path.dirname(dest_label))

    if os.path.exists(source_label):
        try:
            shutil.copy2(source_label, dest_label)
            label_copied = True
        except Exception as e:
            print(f"  Error copying label {label_filename}: {e}")

    return file_copied, label_copied


def move_file_and_label(
    filename,
    dest_folder_files,
    dest_folder_labels,
    source_files_dir=None,
    source_labels_dir=None,
):
    """
    Move both a file and its corresponding JSON label to destination folders.

    Args:
        filename: Name of the file (typically PDF)
        dest_folder_files: Destination folder for files
        dest_folder_labels: Destination folder for JSON label files
        source_files_dir: Source directory for files (defaults to config.DATASET_DIR)
        source_labels_dir: Source directory for labels (defaults to config.LABEL_DIR)

    Returns:
        Tuple of (file_moved: bool, label_moved: bool)
    """
    import config
    import shutil

    if source_files_dir is None:
        source_files_dir = config.DATASET_DIR
    if source_labels_dir is None:
        source_labels_dir = config.LABEL_DIR

    file_moved = False
    label_moved = False

    # Move main file
    source_file = os.path.join(source_files_dir, filename)
    dest_file = os.path.join(dest_folder_files, filename)

    # Ensure dest dir exists
    ensure_dir_exists(os.path.dirname(dest_file))

    if os.path.exists(source_file):
        try:
            shutil.move(source_file, dest_file)
            file_moved = True
        except Exception as e:
            print(f"  Error moving file {filename}: {e}")

    # Move corresponding JSON label
    label_filename = os.path.splitext(filename)[0] + ".json"
    source_label = os.path.join(source_labels_dir, label_filename)
    dest_label = os.path.join(dest_folder_labels, label_filename)

    # Ensure dest label dir exists
    ensure_dir_exists(os.path.dirname(dest_label))

    if os.path.exists(source_label):
        try:
            shutil.move(source_label, dest_label)
            label_moved = True
        except Exception as e:
            print(f"  Error moving label {label_filename}: {e}")

    return file_moved, label_moved


def move_file_safe(src, dest_folder):
    """
    Safely moves a file from src to dest_folder using copy + remove.
    Handles missing source or existing destination gracefully.

    Args:
        src: Source file path
        dest_folder: Destination folder path

    Returns:
        bool: True if file was successfully moved, False otherwise
    """
    import shutil

    if not os.path.exists(src):
        print(f"File not found: {src}")
        return False

    filename = os.path.basename(src)
    dest_path = os.path.join(dest_folder, filename)

    if os.path.exists(dest_path):
        print(f"File already exists in destination: {dest_path}. Overwriting...")

    try:
        shutil.copy2(src, dest_path)
        if os.path.exists(dest_path):
            os.remove(src)
            # Verify removal
            if os.path.exists(src):
                print(f"Warning: Failed to delete source file after copy: {src}")
                return False
            else:
                print(f"Moved: {src} -> {dest_path}")
                return True
        else:
            print(f"Error: Copy failed for {src}")
            return False
    except Exception as e:
        print(f"Error moving {src}: {e}")
        return False


def get_json_content_hash(json_path):
    """
    Read JSON file, parse it, and return MD5 hash of canonical representation.
    Uses sorted keys to ensure consistent hashing regardless of key order.

    Args:
        json_path: Path to JSON file

    Returns:
        str: MD5 hash of JSON content, or None if error occurs
    """
    import json
    import hashlib

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Dump with sort_keys=True to ensure key order doesn't affect hash
        canonical_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(canonical_str.encode("utf-8")).hexdigest()
    except Exception as e:
        print(f"Error processing {json_path}: {e}")
        return None


def normalize_text(text):
    """Normalizes text for easier comparison (lowercase, remove newlines)."""
    if not text:
        return ""
    # Convert to lowercase, replace newlines with spaces, and strip whitespace
    return text.lower().replace("\n", " ").strip()


def clean_whitespace(text):
    """
    Cleans whitespace from text by:
    1. Removing leading and trailing whitespace
    2. Replacing multiple consecutive spaces with a single space

    Args:
        text: String to clean

    Returns:
        Cleaned string with normalized whitespace
    """
    if not text or not isinstance(text, str):
        return text

    # Strip leading and trailing whitespace
    text = text.strip()

    # Replace multiple consecutive spaces with single space
    text = re.sub(r"\s+", " ", text)

    return text
