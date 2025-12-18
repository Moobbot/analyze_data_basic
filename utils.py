import os

def format_size(size_bytes):
    """Converts bytes to human readable string (B, KB, MB, GB, TB)."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

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
