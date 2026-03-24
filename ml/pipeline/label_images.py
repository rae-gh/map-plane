"""
Interactive image labeler for peptide bond ring classification.

Controls:
    t / right arrow  → True (has rings)
    f / left arrow   → False (no rings)
    u                → Uncertain
    z                → Undo last label
    q                → Save and quit

Usage:
    # Label unlabeled images (random order)
    python ml/pipeline/label_images.py

    # Review low-confidence model predictions (uncertainty order)
    python ml/pipeline/label_images.py --mode review

    # Spot-check True predictions (random order)
    python ml/pipeline/label_images.py --mode review --filter true

    # Spot-check False predictions (random order)
    python ml/pipeline/label_images.py --mode review --filter false

    # Filter to specific model
    python ml/pipeline/label_images.py --mode review --model ring_classifier_v3 --filter true
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
TSV_PATH   = Path("ml/data/peptide_bonds_data.tsv")
IMAGE_DIR  = Path("ml/data/images/peptide_bonds")
CLASSIFIER = "human"
# ──────────────────────────────────────────────────────────────────────────────


def save(df):
    df.to_csv(TSV_PATH, sep="\t", index=False)
    print(f"  Saved → {TSV_PATH}")


def get_label_queue(df, mode, model, filter_label):
    """Return list of df indices to work through, depending on mode."""
    if mode == "label":
        # All unlabeled rows, randomised
        queue = df[df["has_rings"].isna()].sample(frac=1, random_state=42).index.tolist()

    elif mode == "review":
        # Model-classified rows not yet manually verified
        mask = df["manually_verified"] == "False"
        if model:
            mask &= df["classified_by"] == model
        if filter_label:
            mask &= df["has_rings"].str.lower() == filter_label.lower()
        subset = df[mask].copy()
        subset["confidence"] = pd.to_numeric(subset["confidence"], errors="coerce")
        # If filtering by label, randomise for spot-checking
        # Otherwise sort by uncertainty (closest to 0.5 first)
        if filter_label:
            subset = subset.sample(frac=1, random_state=42)
        else:
            subset["uncertainty"] = (subset["confidence"] - 0.5).abs()
            subset = subset.sort_values("uncertainty")
        queue = subset.index.tolist()

    return queue


def build_title(row, idx, total, mode):
    base = (f"{row['pdb_code']}  |  {row['aa']}  |  "
            f"{row['resolution']}Å  |  {idx+1}/{total}")
    if mode == "review":
        conf = row.get("confidence", "?")
        pred = row.get("has_rings", "?")
        base += f"\nModel: {pred}  (conf: {conf})"
    return base


def run(mode, model, filter_label):
    df = pd.read_csv(TSV_PATH, sep="\t", dtype=str)

    # Ensure required columns exist
    for col in ["has_rings", "classified_by", "manually_verified", "confidence"]:
        if col not in df.columns:
            df[col] = None

    queue = get_label_queue(df, mode, model, filter_label)
    total = len(queue)

    if total == 0:
        if mode == "label":
            print("Nothing left to label!")
        else:
            print("No unverified predictions found.")
            if model:
                print(f"  (filtered to model: {model})")
        return

    mode_label = "REVIEW" if mode == "review" else "LABEL"
    n_labeled  = (df["has_rings"].notna() & (df["classified_by"] == "human")).sum()
    n_verified = (df["manually_verified"] == "True").sum()

    print(f"\n{'='*50}")
    print(f"  Mode            : {mode_label}")
    if mode == "review" and model:
        print(f"  Model           : {model}")
    if filter_label:
        print(f"  Filter          : has_rings = {filter_label}")
    print(f"  Human labeled   : {n_labeled}")
    print(f"  Verified        : {n_verified}")
    print(f"  Queue           : {total}")
    print(f"{'='*50}")
    print(f"  t / → = True | f / ← = False | u = Uncertain | z = Undo | q = Quit\n")

    fig, ax = plt.subplots(figsize=(6, 6))
    plt.subplots_adjust(top=0.85)
    title_mode = "Ring Labeler" if mode == "label" else "Ring Reviewer"
    fig.canvas.manager.set_window_title(title_mode)

    state = {"pos": 0, "history": []}

    def show(idx):
        row = df.loc[queue[idx]]
        img = mpimg.imread(IMAGE_DIR / row["image_name"])
        ax.clear()
        ax.imshow(img, cmap="gray")
        ax.set_title(build_title(row, idx, total, mode), fontsize=9)
        ax.axis("off")
        fig.canvas.draw()

    def label(value):
        idx     = state["pos"]
        row_idx = queue[idx]

        # Store previous state for undo
        prev = {
            "has_rings":         df.at[row_idx, "has_rings"],
            "classified_by":     df.at[row_idx, "classified_by"],
            "manually_verified": df.at[row_idx, "manually_verified"],
        }
        state["history"].append((row_idx, prev))

        # Write new label
        df.at[row_idx, "has_rings"]         = value
        df.at[row_idx, "classified_by"]     = CLASSIFIER
        df.at[row_idx, "manually_verified"] = "True"
        df.at[row_idx, "confidence"] = None

        n_done = idx + 1
        print(f"  [{n_done}/{total}]  {df.loc[row_idx,'image_name']} → {value}")

        # Autosave every 10
        if n_done % 10 == 0:
            save(df)

        # Advance or finish
        if idx + 1 < total:
            state["pos"] += 1
            show(state["pos"])
        else:
            print("\nAll done! Saving...")
            save(df)
            plt.close()

    def on_key(event):
        k = event.key
        if k in ("t", "right"):
            label("True")
        elif k in ("f", "left"):
            label("False")
        elif k == "u":
            label("Uncertain")
        elif k == "z":
            if state["history"]:
                row_idx, prev = state["history"].pop()
                for col, val in prev.items():
                    df.at[row_idx, col] = val
                state["pos"] = max(0, state["pos"] - 1)
                print(f"  Undo → {df.loc[row_idx, 'image_name']}")
                show(state["pos"])
        elif k == "q":
            save(df)
            plt.close()

    fig.canvas.mpl_connect("key_press_event", on_key)
    show(0)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",   default="label",
                        choices=["label", "review"],
                        help="label = new images, review = check model predictions")
    parser.add_argument("--model",  default=None,
                        help="Filter review to a specific model version")
    parser.add_argument("--filter", default=None,
                        choices=["true", "false"],
                        help="Filter review to True or False predictions only (random order for spot-checking)")
    args = parser.parse_args()
    run(args.mode, args.model, args.filter)