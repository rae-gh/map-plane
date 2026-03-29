"""
Interactive image labeler for peptide bond ring classification.

"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

def get_stats(df):
    total = len(df)
    true_count = df["has_rings"].str.lower().value_counts().get("true", 0)
    false_count = df["has_rings"].str.lower().value_counts().get("false", 0)
    unclassified_count = df["has_rings"].isna().sum()
    return {
        "total": total,
        "true": true_count,
        "false": false_count,
        "unclassified": unclassified_count
    }


def get_all_images(df, IMAGE_DIR):
    # get the first matching random image that has not been classified by a model (has_rings is NaN)
    subset = df.copy()
    subset = subset.sample(frac=1, random_state=42)  # randomize
    queue = subset.index.tolist()
    rows = []
    paths = []
    for idx in queue:
        row = df.loc[idx]
        img_path = IMAGE_DIR / row["image_name"]
        rows.append(row)
        paths.append(img_path)
    return paths, rows

def get_next_image(df, IMAGE_DIR, last_idx=None):
    # get the first matching random image that has not been classified by a model (has_rings is NaN)
    subset = df.copy()
    subset = subset.sample(frac=1, random_state=42)  # randomize
    queue = subset.index.tolist()

    if last_idx is not None:
        while len(queue) > 0:
            this_idx = queue.pop(0)
            print(f"Checking index {this_idx} against last index {last_idx}...")
            if this_idx == last_idx:
                break
    first_idx = queue[0] if len(queue) > 0 else None
    if first_idx is not None:
        row = df.loc[first_idx]
        img_path = IMAGE_DIR / row["image_name"]
        return img_path, row, first_idx

    return None, None, None

def save_response(df, idx, tsv_path, response):
    df.to_csv(tsv_path, sep="\t", index=False)
    print(f"  Saved → {tsv_path}")
    if response == "True":
        df.at[idx.name, "has_rings"] = "True"
    else:
        df.at[idx.name, "has_rings"] = "False"
    df.at[idx.name, "classified_by"] = "human"
    df.at[idx.name, "classified_datetime"] = pd.Timestamp.now().isoformat()
    df.at[idx.name, "manually_verified"] = "True"
    df.at[idx.name, "verified_datetime"] = pd.Timestamp.now().isoformat()
    df.to_csv(tsv_path, sep="\t", index=False)