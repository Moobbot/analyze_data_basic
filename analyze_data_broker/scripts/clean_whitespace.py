"""
Script to clean whitespace from JSON files.
Removes leading/trailing whitespace and normalizes multiple spaces to single space
in all string values.

Usage:
    python clean_whitespace.py <input_file_or_folder> [--output <output_folder>]

Examples:
    # Process single file (overwrites)
    python clean_whitespace.py datasets/labels/Trade_Confirmation/0308.json

    # Process entire folder (overwrites all JSON files)
    python clean_whitespace.py datasets/labels/Trade_Confirmation

    # Process with output to different folder
    python clean_whitespace.py datasets/labels/Trade_Confirmation --output cleaned_data
"""

import os
import json
import argparse


def clean_json_whitespace(data, parent_key=None):
    """
    Recursively clean whitespace from all string values in a JSON structure.

    Special handling for specific fields:
    - "Securities ID": removes ALL whitespace
    - "Account no.": removes ALL whitespace
    - Other fields: removes only leading/trailing whitespace (trim)

    Args:
        data: JSON data (dict, list, or primitive type)
        parent_key: Key name from parent dict (used for special field handling)

    Returns:
        Cleaned JSON data with same structure
    """
    if isinstance(data, dict):
        return {key: clean_json_whitespace(value, key) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_json_whitespace(item, parent_key) for item in data]
    elif isinstance(data, str):
        # Special fields that need ALL whitespace removed
        REMOVE_ALL_SPACES_FIELDS = ["Securities ID", "Account no."]

        if parent_key in REMOVE_ALL_SPACES_FIELDS:
            # Remove ALL whitespace (including spaces in the middle)
            return (
                data.replace(" ", "")
                .replace("\t", "")
                .replace("\n", "")
                .replace("\r", "")
            )
        else:
            # Other fields: only trim leading/trailing whitespace
            return data.strip()
    else:
        # Keep numbers, booleans, None as is
        return data


def process_json_file(input_path, output_path=None):
    """
    Process a single JSON file to clean whitespace.

    Args:
        input_path: Path to input JSON file
        output_path: Path to output JSON file (if None, overwrites input)

    Returns:
        bool: True if successful, False otherwise
    """
    if output_path is None:
        output_path = input_path

    try:
        # Read JSON file
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Clean whitespace
        cleaned_data = clean_json_whitespace(data)

        # Write back to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

        print(f"✓ Processed: {input_path}")
        return True

    except json.JSONDecodeError as e:
        print(f"✗ JSON Error in {input_path}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error processing {input_path}: {e}")
        return False


def process_folder(input_folder, output_folder=None):
    """
    Process all JSON files in a folder recursively.

    Args:
        input_folder: Path to input folder
        output_folder: Path to output folder (if None, overwrites input files)

    Returns:
        Tuple of (success_count, error_count)
    """
    success_count = 0
    error_count = 0

    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.lower().endswith(".json"):
                input_path = os.path.join(root, filename)

                if output_folder:
                    # Preserve folder structure in output
                    rel_path = os.path.relpath(input_path, input_folder)
                    output_path = os.path.join(output_folder, rel_path)

                    # Ensure output directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                else:
                    output_path = None

                if process_json_file(input_path, output_path):
                    success_count += 1
                else:
                    error_count += 1

    return success_count, error_count


def main():
    parser = argparse.ArgumentParser(
        description="Clean whitespace from JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file (overwrites)
  python clean_whitespace.py datasets/labels/Trade_Confirmation/0308.json
  
  # Process entire folder (overwrites all JSON files)
  python clean_whitespace.py datasets/labels/Trade_Confirmation
  
  # Process with output to different folder
  python clean_whitespace.py datasets/labels/Trade_Confirmation --output cleaned_data
        """,
    )

    parser.add_argument("input", help="Input JSON file or folder to process")

    parser.add_argument(
        "--output",
        "-o",
        help="Output folder (if not specified, overwrites input files)",
        default=None,
    )

    args = parser.parse_args()

    # Check if input exists
    if not os.path.exists(args.input):
        print(f"Error: Input path not found: {args.input}")
        return

    # Process based on whether input is file or directory
    if os.path.isfile(args.input):
        if args.output:
            # If output specified for single file, treat as file path
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            process_json_file(args.input, args.output)
        else:
            process_json_file(args.input)
    elif os.path.isdir(args.input):
        print(f"Processing folder: {args.input}")
        if args.output:
            print(f"Output folder: {args.output}")
            os.makedirs(args.output, exist_ok=True)
        else:
            print("Note: Overwriting input files")

        success, errors = process_folder(args.input, args.output)

        print(f"\n{'='*50}")
        print(f"Summary:")
        print(f"  ✓ Successfully processed: {success} files")
        print(f"  ✗ Errors: {errors} files")
        print(f"{'='*50}")
    else:
        print(f"Error: Input path is neither file nor directory: {args.input}")


if __name__ == "__main__":
    main()
