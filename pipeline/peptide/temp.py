"""
Rename randomly named images to deterministic names based on TSV lookup.

Old: 471561.png
New: 1ejg_A_1_THR.png

Updates the TSV image_name column to match.

Usage:
    python pipeline/rename_images.py
"""

import pandas as pd
from pathlib import Path
import shutil

# ── Config ─────────────────────────────────────────────────────────────────────
TSV_PATH  = Path("data/peptide_bonds_data.tsv")
IMAGE_DIR = Path("data/images/peptide_bonds")
DRY_RUN   = False   # set to False to actually rename
# ──────────────────────────────────────────────────────────────────────────────


def new_name(row):
    return f"{row['pdb_code']}_{row['chain']}_{row['rid']}_{row['aa']}.png"


def main():
    df = pd.read_csv(TSV_PATH, sep="\t", dtype=str)

    if "image_name" not in df.columns:
        print("No image_name column found — nothing to rename.")
        return

    n_renamed   = 0
    n_missing   = 0
    n_collision = 0
    collisions  = []

    print(f"\n{'DRY RUN — ' if DRY_RUN else ''}Renaming {len(df)} images...\n")

    for idx, row in df.iterrows():
        old_name = row["image_name"]
        old_path = IMAGE_DIR / old_name
        new      = new_name(row)
        new_path = IMAGE_DIR / new

        if not old_path.exists():
            n_missing += 1
            continue

        if new_path.exists() and new_path != old_path:
            n_collision += 1
            collisions.append((old_name, new))
            continue

        if old_name == new:
            continue  # already correct name

        if not DRY_RUN:
            old_path.rename(new_path)
            df.at[idx, "image_name"] = new

        print(f"  {old_name}  →  {new}")
        n_renamed += 1

    print(f"\nSummary:")
    print(f"  Renamed   : {n_renamed}")
    print(f"  Missing   : {n_missing}")
    print(f"  Collision : {n_collision}")

    if collisions:
        print(f"\nCollisions (target already exists):")
        for old, new in collisions:
            print(f"  {old} → {new}")

    if not DRY_RUN and n_renamed > 0:
        df.to_csv(TSV_PATH, sep="\t", index=False)
        print(f"\nTSV updated → {TSV_PATH}")
    elif DRY_RUN:
        print(f"\nDry run complete — set DRY_RUN = False to apply changes.")


if __name__ == "__main__":
    main()