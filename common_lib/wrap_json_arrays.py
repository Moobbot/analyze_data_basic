#!/usr/bin/env python3
"""
wrap_json_arrays.py
Utility to wrap JSON objects into arrays for multipage document support
"""

import json
from pathlib import Path
from typing import List, Tuple


def wrap_json_in_folder(
    folder_path: Path, recursive: bool = True
) -> Tuple[int, int, List[str]]:
    """
    Wrap all JSON objects in a folder to arrays

    Args:
        folder_path: Path to folder containing JSON files
        recursive: If True, process subdirectories recursively

    Returns:
        Tuple of (fixed_count, already_array_count, errors)
    """
    if not folder_path.exists():
        return 0, 0, [f"Folder not found: {folder_path}"]

    fixed_count = 0
    already_array = 0
    errors = []

    # Find all JSON files
    if recursive:
        json_files = list(folder_path.rglob("*.json"))
    else:
        json_files = list(folder_path.glob("*.json"))

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                content = f.read().strip()

            # Skip if already array
            if content.startswith("["):
                already_array += 1
                continue

            # Wrap object in array
            if content.startswith("{"):
                try:
                    obj = json.loads(content)
                    with open(json_file, "w", encoding="utf-8") as f:
                        json.dump([obj], f, indent=2, ensure_ascii=False)
                    fixed_count += 1
                except json.JSONDecodeError as e:
                    errors.append(f"{json_file.name}: {e}")
            else:
                errors.append(f"{json_file.name}: Invalid format (not {{ or [)")

        except Exception as e:
            errors.append(f"{json_file.name}: {e}")

    return fixed_count, already_array, errors


def wrap_json_in_folders(
    folder_paths: List[Path], recursive: bool = True, verbose: bool = True
) -> dict:
    """
    Wrap JSON objects to arrays in multiple folders

    Args:
        folder_paths: List of folder paths to process
        recursive: If True, process subdirectories recursively
        verbose: If True, print progress messages

    Returns:
        Dictionary with summary statistics
    """
    results = {
        "total_fixed": 0,
        "total_already": 0,
        "total_errors": 0,
        "folders_processed": 0,
        "details": [],
    }

    for folder_path in folder_paths:
        if not folder_path.exists():
            if verbose:
                print(f"⚠️  Folder not found: {folder_path}")
            continue

        if verbose:
            print(f"📁 Processing: {folder_path}")

        # Process subdirectories if they exist
        subdirs = [d for d in folder_path.iterdir() if d.is_dir()]

        if subdirs and recursive:
            for subdir in sorted(subdirs):
                fixed, already, errors = wrap_json_in_folder(subdir, recursive=False)

                results["total_fixed"] += fixed
                results["total_already"] += already
                results["total_errors"] += len(errors)
                results["folders_processed"] += 1

                if verbose:
                    err_str = f", Errors: {len(errors)}" if errors else ""
                    print(
                        f"  ✓ {subdir.name}: Fixed={fixed}, Already[]={already}{err_str}"
                    )

                    if errors and len(errors) <= 3:
                        for err in errors:
                            print(f"      - {err}")

                results["details"].append(
                    {
                        "folder": str(subdir),
                        "fixed": fixed,
                        "already_array": already,
                        "errors": errors,
                    }
                )
        else:
            # Process the folder itself
            fixed, already, errors = wrap_json_in_folder(
                folder_path, recursive=recursive
            )

            results["total_fixed"] += fixed
            results["total_already"] += already
            results["total_errors"] += len(errors)
            results["folders_processed"] += 1

            if verbose:
                err_str = f", Errors: {len(errors)}" if errors else ""
                print(
                    f"  ✓ {folder_path.name}: Fixed={fixed}, Already[]={already}{err_str}"
                )

            results["details"].append(
                {
                    "folder": str(folder_path),
                    "fixed": fixed,
                    "already_array": already,
                    "errors": errors,
                }
            )

    return results


if __name__ == "__main__":
    # Example usage
    print("This is a library module. Import it in your scripts:")
    print(
        "  from common_lib.wrap_json_arrays import wrap_json_in_folder, wrap_json_in_folders"
    )
