import pandas as pd
import glob

# Pick up ALL csvs in data folder
files = glob.glob("data/*.csv")

dfs = []
for f in files:
    df = pd.read_csv(f)
    print(f"✅ {f} → {len(df)} rows")
    dfs.append(df)

# Merge
merged = pd.concat(dfs, ignore_index=True)

# Drop duplicates just in case
merged = merged.drop_duplicates()

# Shuffle
merged = merged.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\n📊 Total rows after merge: {len(merged)}")

# Save
merged.to_csv("data/ml_training_data_final.csv", index=False)
print("✅ Saved → data/ml_training_data_final.csv")