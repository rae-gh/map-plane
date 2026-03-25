"""
Run trained classifier on all unlabeled images.
Saves predictions and confidence scores back to the TSV.

Usage:
    python ml/pipeline/classify_images.py
    python ml/pipeline/classify_images.py --model ring_classifier_v2
"""

import argparse
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from torchvision.models import ResNet18_Weights
from pathlib import Path
from PIL import Image
import json

# ── Config ─────────────────────────────────────────────────────────────────────
TSV_PATH   = Path("ml/data/peptide_bonds_data.tsv")
IMAGE_DIR  = Path("ml/data/images/peptide_bonds")
MODEL_DIR  = Path("ml/models")

IMAGE_SIZE         = 224
BATCH_SIZE         = 32
DECISION_THRESHOLD = 0.62
DEFAULT_MODEL      = "ring_classifier_v3"
# ──────────────────────────────────────────────────────────────────────────────


# ── Dataset ────────────────────────────────────────────────────────────────────
class UnlabeledDataset(Dataset):
    def __init__(self, df, image_dir, transform):
        self.df        = df.reset_index(drop=True)
        self.image_dir = Path(image_dir)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img = Image.open(self.image_dir / row["image_name"]).convert("RGB")
        return self.transform(img), row.name   # return original df index


# ── Transform ──────────────────────────────────────────────────────────────────
infer_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


# ── Model ──────────────────────────────────────────────────────────────────────
def load_model(model_name, device):
    model_path = MODEL_DIR / f"{model_name}.pth"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model    = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 1)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model


# ── Main ───────────────────────────────────────────────────────────────────────
def main(model_name):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nDevice : {device}")
    print(f"Model  : {model_name}")

    # Load TSV
    df = pd.read_csv(TSV_PATH, sep="\t", dtype=str)

    # Add confidence column if not present
    if "confidence" not in df.columns:
        df["confidence"] = None

    # Only classify unlabeled rows
    unlabeled_mask = df["manually_verified"] != "True"
    unlabeled_df   = df[unlabeled_mask].copy()
    n_unlabeled    = len(unlabeled_df)

    if n_unlabeled == 0:
        print("No unlabeled images found — nothing to do.")
        return

    print(f"Unlabeled images to classify: {n_unlabeled}\n")

    # Dataset and loader
    dataset = UnlabeledDataset(unlabeled_df, IMAGE_DIR, infer_transform)
    loader  = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)

    # Load model
    model = load_model(model_name, device)

    # Load metadata for threshold
    meta_path = MODEL_DIR / f"{model_name}_metadata.json"
    threshold = DECISION_THRESHOLD
    if meta_path.exists():
        with open(meta_path) as f:
            meta = json.load(f)
        threshold = meta.get("decision_threshold", DECISION_THRESHOLD)
        print(f"Decision threshold from metadata: {threshold}")
    else:
        print(f"Decision threshold (default): {threshold}")

    # Run inference
    all_indices, all_probs = [], []

    with torch.no_grad():
        for batch_num, (imgs, indices) in enumerate(loader):
            imgs    = imgs.to(device)
            outputs = model(imgs).squeeze(1)
            probs   = torch.sigmoid(outputs).cpu().numpy()
            all_probs.extend(probs)
            all_indices.extend(indices.numpy())

            if batch_num % 10 == 0:
                done = batch_num * BATCH_SIZE
                print(f"  {done}/{n_unlabeled} images processed "
                      f"({done/n_unlabeled*100:.0f}%)",
                      flush=True)

    # Write predictions back to df
    n_true = n_false = 0
    for idx, prob in zip(all_indices, all_probs):
        # Never overwrite a manually verified row
        if df.at[idx, "manually_verified"] == "True":
            continue

        predicted = "True" if prob > threshold else "False"
        df.at[idx, "has_rings"]         = predicted
        df.at[idx, "classified_by"]     = model_name
        df.at[idx, "manually_verified"] = "False"
        df.at[idx, "confidence"]        = str(round(float(prob), 4))
        if predicted == "True":
            n_true += 1
        else:
            n_false += 1

    # Save
    df.to_csv(TSV_PATH, sep="\t", index=False)

    print(f"\nResults:")
    print(f"  has_rings True  : {n_true:>6}  ({n_true/n_unlabeled*100:.1f}%)")
    print(f"  has_rings False : {n_false:>6}  ({n_false/n_unlabeled*100:.1f}%)")
    print(f"\nSaved → {TSV_PATH}")
    print(f"\nTo review low-confidence predictions:")
    print(f"  python ml/pipeline/review_predictions.py --model {model_name}\n")

    # Verify no human labels were touched
    n_verified = (df["manually_verified"] == "True").sum()
    print(f"  Manually verified rows intact: {n_verified}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="Model name (without .pth extension)")
    args = parser.parse_args()
    main(args.model)