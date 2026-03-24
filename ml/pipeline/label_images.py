"""
Interactive image labeler for peptide bond ring classification.

Controls:
    t / right arrow  → True (has rings)
    f / left arrow   → False (no rings)
    u                → Uncertain
    z                → Undo last label
    q                → Save and quit
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path
import sys

# ── Config ────────────────────────────────────────────────────────────────────
TSV_PATH  = Path("ml/data/peptide_bonds_data.tsv")
IMAGE_DIR = Path("ml/data/images/peptide_bonds")
CLASSIFIER = "human"
# ──────────────────────────────────────────────────────────────────────────────

def save(df):
    df.to_csv(TSV_PATH, sep="\t", index=False)
    print(f"  Saved → {TSV_PATH}")

def run():
    df = pd.read_csv(TSV_PATH, sep="\t", dtype=str)

    # Find unclassified rows
    unlabeled = df[df["has_rings"].isna()].sample(frac=1, random_state=42).index.tolist()
    total     = len(unlabeled)

    if total == 0:
        print("Nothing left to classify!")
        return

    # Summary of current state
    n_labeled = df["has_rings"].notna().sum()
    print(f"\n{n_labeled} already labeled, {total} remaining.")
    print("  t / → = True | f / ← = False | u = Uncertain | z = Undo | q = Quit\n")

    fig, ax = plt.subplots(figsize=(6, 6))
    plt.subplots_adjust(bottom=0.15)
    fig.canvas.manager.set_window_title("Ring Classifier")

    state = {"pos": 0, "history": []}

    def show(idx):
        row = df.loc[unlabeled[idx]]
        img = mpimg.imread(IMAGE_DIR / row["image_name"])
        ax.clear()
        ax.imshow(img, cmap="gray")
        ax.set_title(
            f"{row['pdb_code']}  |  {row['aa']}  |  {row['resolution']}Å  |  "
            f"{idx+1}/{total}",
            fontsize=10
        )
        ax.axis("off")
        fig.canvas.draw()

    def label(value):
        idx     = state["pos"]
        row_idx = unlabeled[idx]

        # Record label + provenance
        df.at[row_idx, "has_rings"]         = value
        df.at[row_idx, "classified_by"]     = CLASSIFIER
        df.at[row_idx, "manually_verified"] = "True"

        state["history"].append(row_idx)

        labeled = df["has_rings"].notna().sum()
        print(f"  [{labeled} labeled]  {df.loc[row_idx,'image_name']} → {value}")

        # Autosave every 10
        if labeled % 10 == 0:
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
                row_idx = state["history"].pop()
                df.at[row_idx, "has_rings"]         = None
                df.at[row_idx, "classified_by"]     = None
                df.at[row_idx, "manually_verified"] = None
                state["pos"] = max(0, state["pos"] - 1)
                print(f"  Undo → {df.loc[row_idx,'image_name']}")
                show(state["pos"])
        elif k == "q":
            save(df)
            plt.close()

    fig.canvas.mpl_connect("key_press_event", on_key)
    show(0)
    plt.show()

if __name__ == "__main__":
    run()