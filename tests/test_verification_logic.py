import sys
import os

sys.path.append(os.getcwd())
from core import verification


def test_match():
    # Case 1: User Example (Partial/Prefix)
    json_val = "RSPHL/2510/00"
    text_content = "Some text RSPHL/2510/002 here."

    print(f"Testing JSON: '{json_val}' vs Text: '{text_content}'")
    status, score, _, _, _ = verification.get_best_match(json_val, text_content)
    print(f"Result: {status}")
    assert status == "FOUND_SUBSTRING"

    # Case 2: Exact Match
    json_val_2 = "RSPHL/2510/002"
    print(f"Testing JSON: '{json_val_2}' vs Text: '{text_content}'")
    status, score, _, _, _ = verification.get_best_match(json_val_2, text_content)
    print(f"Result: {status}")
    assert status == "FOUND"

    # Case 3: Exact Match surrounded by symbols
    json_val_3 = "12345"
    text_content_3 = "Invoice #12345."
    print(f"Testing JSON: '{json_val_3}' vs Text: '{text_content_3}'")
    status, score, _, _, _ = verification.get_best_match(json_val_3, text_content_3)
    print(f"Result: {status}")
    assert status == "FOUND"


if __name__ == "__main__":
    try:
        test_match()
        print("\nAll tests passed!")
    except AssertionError as e:
        print(f"\nTest Failed: {e}")
