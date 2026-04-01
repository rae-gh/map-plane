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

def get_next_image(df, IMAGE_DIR):
    # get the first matching random image that has not been classified by a model (has_rings is NaN)
    subset = df.copy()
    subset = subset.sample(frac=1, random_state=42)  # randomize
    queue = subset.index.tolist()
    print(f"Checking queue {queue}...")
    imgs = []
    rows = []
    paths = []
    for idx in queue:
        print(f"Checking index {idx}...")
        row = df.loc[idx]
        img_path = IMAGE_DIR / row["image_name"]
        imgs.append(img_path)
        rows.append(row)
        paths.append(img_path)
    return imgs, rows, paths

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