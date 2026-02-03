import os

DATA_DIR = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_broker\datasets\test-set-broker\labels"


def main():
    print("Checking broker test set distribution...")
    if not os.path.exists(DATA_DIR):
        print(f"Dir not found: {DATA_DIR}")
        return

    types = [
        d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))
    ]
    total_files = 0

    for t in types:
        path = os.path.join(DATA_DIR, t)
        count = len([f for f in os.listdir(path) if f.lower().endswith(".json")])
        print(f"  - {t}: {count}")
        total_files += count

    print(f"Total: {total_files}")


if __name__ == "__main__":
    main()
