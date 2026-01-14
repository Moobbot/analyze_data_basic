"""
File operations and directory management utilities.

Provides common file system operations used throughout the project.
"""

import os
import json
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def ensure_dir_exists(directory: Path) -> bool:
    """
    Create the directory if it does not exist.

    Args:
        directory: Path to directory (can be Path object or string)

    Returns:
        True if directory exists or was created, False on error

    Examples:
        >>> ensure_dir_exists(Path("output/data"))
        True
    """
    try:
        if isinstance(directory, str):
            directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")
        return False


def read_file(path: Path) -> str:
    """
    Read a text file and return its content as a stripped string.

    Args:
        path: Path to file (can be Path object or string)

    Returns:
        File content or error message

    Examples:
        >>> content = read_file("data.txt")
    """
    if isinstance(path, str):
        path = Path(path)

    if not path.exists():
        return f"[Error: File not found - {path}]"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        return f"[Error reading {path}: {e}]"


def get_files_map(directory: Path) -> Dict[str, List[str]]:
    """
    Scan a directory and return a dictionary mapping basenames (no extension)
    to a list of full filenames.

    Example: {'report': ['report.pdf', 'report.docx']}

    Args:
        directory: Directory to scan (can be Path object or string)

    Returns:
        Dictionary mapping basenames to list of filenames

    Examples:
        >>> files = get_files_map("data/")
        >>> print(files.get("invoice_001"))
        ['invoice_001.pdf', 'invoice_001.json']
    """
    if isinstance(directory, str):
        directory = Path(directory)

    files_map: Dict[str, List[str]] = {}

    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        return files_map

    try:
        for item in directory.iterdir():
            if item.is_file():
                base_name = item.stem
                if base_name not in files_map:
                    files_map[base_name] = []
                files_map[base_name].append(item.name)
    except Exception as e:
        print(f"Error reading {directory}: {e}")

    return files_map


def get_files_map_recursive(directory: Path) -> Dict[str, List[str]]:
    """
    Scan a directory recursively and return a dictionary mapping basenames
    (relative path without extension) to a list of full relative filenames.

    Normalizes case to handle directory casing differences.
    Example: {'subdir/report': ['subdir/report.pdf', 'subdir/report.json']}

    Args:
        directory: Root directory to scan (can be Path object or string)

    Returns:
        Dictionary mapping normalized base paths to list of relative file paths
    """
    if isinstance(directory, str):
        directory = Path(directory)

    files_map: Dict[str, List[str]] = {}

    if not directory.exists():
        print(f"Directory not found: {directory}")
        return files_map

    for root, _, files in os.walk(directory):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(directory)
            # Use relative path without extension as key to match structure
            # Normalize case to handle directory casing differences
            base_name = os.path.normcase(str(rel_path.with_suffix("")))

            if base_name not in files_map:
                files_map[base_name] = []
            files_map[base_name].append(str(rel_path))

    return files_map


def list_files_recursive(directory: Path, extension: str) -> List[str]:
    """
    List files with specific extension recursively (all levels).

    Args:
        directory: Directory to search (can be Path object or string)
        extension: File extension (e.g., '.pdf')

    Returns:
        List of relative paths from the directory

    Examples:
        >>> pdf_files = list_files_recursive("data/", ".pdf")
        >>> print(len(pdf_files))
        42
    """
    if isinstance(directory, str):
        directory = Path(directory)

    files: List[str] = []

    if not directory.exists():
        return files

    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(extension.lower()):
                full_path = Path(root) / filename
                rel_path = full_path.relative_to(directory)
                files.append(str(rel_path))

    return files


def get_json_content_hash(json_path: Path) -> Optional[str]:
    """
    Read JSON file, parse it, and return MD5 hash of canonical representation.

    Uses sorted keys to ensure consistent hashing regardless of key order.

    Args:
        json_path: Path to JSON file (can be Path object or string)

    Returns:
        MD5 hash of JSON content, or None if error occurs

    Examples:
        >>> hash_val = get_json_content_hash("data.json")
    """
    if isinstance(json_path, str):
        json_path = Path(json_path)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Dump with sort_keys=True to ensure key order doesn't affect hash
        canonical_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(canonical_str.encode("utf-8")).hexdigest()
    except Exception as e:
        print(f"Error processing {json_path}: {e}")
        return None


def copy_file_and_label(
    filename: str,
    dest_folder_files: Path,
    dest_folder_labels: Path,
    source_files_dir: Path,
    source_labels_dir: Path,
) -> Tuple[bool, bool]:
    """
    Copy both a file and its corresponding JSON label to destination folders.

    Note: This is a generic version. Module-specific versions should handle
    their own config imports.

    Args:
        filename: Name of the file (typically PDF)
        dest_folder_files: Destination folder for files
        dest_folder_labels: Destination folder for JSON label files
        source_files_dir: Source directory for files
        source_labels_dir: Source directory for labels

    Returns:
        Tuple of (file_copied: bool, label_copied: bool)
    """
    if isinstance(dest_folder_files, str):
        dest_folder_files = Path(dest_folder_files)
    if isinstance(dest_folder_labels, str):
        dest_folder_labels = Path(dest_folder_labels)
    if isinstance(source_files_dir, str):
        source_files_dir = Path(source_files_dir)
    if isinstance(source_labels_dir, str):
        source_labels_dir = Path(source_labels_dir)

    file_copied = False
    label_copied = False

    # Copy main file
    source_file = source_files_dir / filename
    dest_file = dest_folder_files / filename

    # Ensure dest dir exists
    dest_file.parent.mkdir(parents=True, exist_ok=True)

    if source_file.exists():
        try:
            shutil.copy2(source_file, dest_file)
            file_copied = True
        except Exception as e:
            print(f"  Error copying file {filename}: {e}")

    # Copy corresponding JSON label
    label_filename = Path(filename).stem + ".json"
    source_label = source_labels_dir / label_filename
    dest_label = dest_folder_labels / label_filename

    # Ensure dest label dir exists
    dest_label.parent.mkdir(parents=True, exist_ok=True)

    if source_label.exists():
        try:
            shutil.copy2(source_label, dest_label)
            label_copied = True
        except Exception as e:
            print(f"  Error copying label {label_filename}: {e}")

    return file_copied, label_copied


def move_file_and_label(
    filename: str,
    dest_folder_files: Path,
    dest_folder_labels: Path,
    source_files_dir: Path,
    source_labels_dir: Path,
) -> Tuple[bool, bool]:
    """
    Move both a file and its corresponding JSON label to destination folders.

    Note: This is a generic version. Module-specific versions should handle
    their own config imports.

    Args:
        filename: Name of the file (typically PDF)
        dest_folder_files: Destination folder for files
        dest_folder_labels: Destination folder for JSON label files
        source_files_dir: Source directory for files
        source_labels_dir: Source directory for labels

    Returns:
        Tuple of (file_moved: bool, label_moved: bool)
    """
    if isinstance(dest_folder_files, str):
        dest_folder_files = Path(dest_folder_files)
    if isinstance(dest_folder_labels, str):
        dest_folder_labels = Path(dest_folder_labels)
    if isinstance(source_files_dir, str):
        source_files_dir = Path(source_files_dir)
    if isinstance(source_labels_dir, str):
        source_labels_dir = Path(source_labels_dir)

    file_moved = False
    label_moved = False

    # Move main file
    source_file = source_files_dir / filename
    dest_file = dest_folder_files / filename

    # Ensure dest dir exists
    dest_file.parent.mkdir(parents=True, exist_ok=True)

    if source_file.exists():
        try:
            shutil.move(str(source_file), str(dest_file))
            # shutil.copy2(str(source_file), str(dest_file))
            file_moved = True
        except Exception as e:
            print(f"  Error moving file {filename}: {e}")

    # Move corresponding JSON label
    label_filename = Path(filename).stem + ".json"
    source_label = source_labels_dir / label_filename
    dest_label = dest_folder_labels / label_filename

    # Ensure dest label dir exists
    dest_label.parent.mkdir(parents=True, exist_ok=True)

    if source_label.exists():
        try:
            shutil.move(str(source_label), str(dest_label))
            # shutil.copy2(str(source_label), str(dest_label))
            label_moved = True
        except Exception as e:
            print(f"  Error moving label {label_filename}: {e}")

    return file_moved, label_moved


def move_file_safe(src: Path, dest_folder: Path) -> bool:
    """
    Safely move a file from src to dest_folder using copy + remove.

    Args:
        src: Source file path (can be Path object or string)
        dest_folder: Destination folder path (can be Path object or string)

    Returns:
        True if file was successfully moved, False otherwise
    """
    if isinstance(src, str):
        src = Path(src)
    if isinstance(dest_folder, str):
        dest_folder = Path(dest_folder)

    if not src.exists():
        print(f"File not found: {src}")
        return False

    dest_path = dest_folder / src.name

    if dest_path.exists():
        print(f"File already exists in destination: {dest_path}. Overwriting...")

    try:
        shutil.copy2(src, dest_path)
        if dest_path.exists():
            src.unlink()
            # Verify removal
            if src.exists():
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
