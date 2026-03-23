import os
import pandas as pd
from sklearn.model_selection import train_test_split

# === CONFIG ===
INPUT_FILE = "creditcard.csv"
OUTPUT_DIRS = ["data-and-scratch1", "data-and-scratch2"]

# === LOAD DATA ===
df = pd.read_csv(INPUT_FILE)

# Shuffle dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# === SPLIT INTO TWO EQUAL PARTS ===
mid = len(df) // 2
peer1 = df.iloc[:mid]
peer2 = df.iloc[mid:]

peers = [peer1, peer2]

# === PROCESS EACH PEER ===
for i, peer_df in enumerate(peers):
    base_dir = OUTPUT_DIRS[i]
    app_data_dir = os.path.join(base_dir, "app-data")

    # Create directories
    os.makedirs(app_data_dir, exist_ok=True)

    # Train-test split (80-20)
    train, test = train_test_split(peer_df, test_size=0.2, random_state=42)

    # Save files
    train.to_csv(os.path.join(app_data_dir, "train.csv"), index=False)
    test.to_csv(os.path.join(app_data_dir, "test.csv"), index=False)

    print(f"Created data for {base_dir}")
    print(f"Train rows: {len(train)}")
    print(f"Test rows: {len(test)}")

print("Dataset splitting completed.")
