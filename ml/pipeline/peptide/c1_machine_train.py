"""
Train a binary ring classifier on labeled peptide bond images.
Fine-tunes a pretrained ResNet18 on has_rings True/False labels.

Usage:
    python ml/training/train_classifier.py
"""

import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from torchvision.models import ResNet18_Weights
from pathlib import Path
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import timm
from huggingface_hub import login
import json
from datetime import datetime



# ── Config ─────────────────────────────────────────────────────────────────────
IMAGE_DIR = Path("ml/data/images/peptide_bonds")
MODEL_DIR = Path("ml/models")
MODEL_DIR.mkdir(exist_ok=True)

BACKBONE    = "uni"  # "resnet18" or "uni"
IMAGE_SIZE  = 224          # ResNet expects 224x224
BATCH_SIZE  = 16
EPOCHS      = 20
LR          = 1e-4         # low lr for fine-tuning
VAL_SPLIT   = 0.2          # 20% validation
RANDOM_SEED = 42
MODEL_NAME  = f"ring_classifier_v1"
DECISION_THRESHOLD = 0.40    # > 0.5 makes model more conservative about predicting True
POS_WEIGHT = 2.0 # Weight for positive class - reduce below 1.0 to penalise has_rings bias


# ──────────────────────────────────────────────────────────────────────────────


# ── Dataset ────────────────────────────────────────────────────────────────────
class RingDataset(Dataset):
    def __init__(self, df, image_dir, transform=None):
        self.df        = df.reset_index(drop=True)
        self.image_dir = Path(image_dir)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row   = self.df.iloc[idx]
        img   = Image.open(self.image_dir / row["image_name"]).convert("RGB")
        label = 1 if str(row["has_rings"]).strip().lower() == "true" else 0
        if self.transform:
            img = self.transform(img)
        return img, label, row["image_name"]


# ── Transforms ─────────────────────────────────────────────────────────────────
# ── Transforms ─────────────────────────────────────────────────────────────────
# ResNet18 — ImageNet normalisation
resnet_train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.Grayscale(num_output_channels=3),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.ColorJitter(brightness=0.1, contrast=0.1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

resnet_val_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# UNI — same normalisation but no ColorJitter (pathology model)
uni_train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.Grayscale(num_output_channels=3),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

uni_val_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


def get_transforms():
    if BACKBONE == "uni":
        return uni_train_transform, uni_val_transform
    else:
        return resnet_train_transform, resnet_val_transform


# ── Model ──────────────────────────────────────────────────────────────────────
def build_model_resnet18():
    model = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
    for param in model.parameters():
        param.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, 1)
    return model, model.fc.parameters()


def build_model_uni():
    from huggingface_hub import login, hf_hub_download
    import timm
    login()

    # Create model architecture without pretrained weights
    model = timm.create_model(
        "vit_large_patch16_224",
        pretrained=False,
        num_classes=0
    )

    # Load weights manually with strict=False
    weights_path = hf_hub_download(
        repo_id="MahmoodLab/UNI",
        filename="pytorch_model.bin"
    )
    state_dict = torch.load(weights_path, map_location="cpu")
    model.load_state_dict(state_dict, strict=False)

    # Freeze and add head
    for param in model.parameters():
        param.requires_grad = False
    in_features = model.num_features
    model.head = nn.Linear(in_features, 1)
    return model, model.head.parameters()


def build_model():
    if BACKBONE == "uni":
        return build_model_uni()
    else:
        return build_model_resnet18()


# ── Training loop ──────────────────────────────────────────────────────────────
def train(model, loader, optimizer, criterion, device):
    model.train()
    total_loss, correct, total = 0, 0, 0
    for imgs, labels, _ in loader:
        imgs, labels = imgs.to(device), labels.float().to(device)
        optimizer.zero_grad()
        outputs = model(imgs).squeeze(1)
        loss    = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        preds    = (torch.sigmoid(outputs) > DECISION_THRESHOLD).long()
        correct += (preds == labels.long()).sum().item()
        total   += len(labels)
    return total_loss / len(loader), correct / total


def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0, 0, 0
    all_preds, all_labels = [], []
    with torch.no_grad():
        for imgs, labels, _ in loader:
            imgs, labels = imgs.to(device), labels.float().to(device)
            outputs = model(imgs).squeeze(1)
            loss    = criterion(outputs, labels)
            total_loss += loss.item()
            preds    = (torch.sigmoid(outputs) > 0.5).long()
            correct += (preds == labels.long()).sum().item()
            total   += len(labels)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.long().cpu().numpy())
    return total_loss / len(loader), correct / total, all_preds, all_labels


# ── Main ───────────────────────────────────────────────────────────────────────
def train_model(pos_weight, decision_threshold, tsv_data, image_dir, model_path, model_name, model_version, backbone):
    POS_WEIGHT = pos_weight
    DECISION_THRESHOLD = decision_threshold
    IMAGE_DIR = Path(image_dir)
    MODEL_DIR = Path(model_path)
    MODEL_DIR.mkdir(exist_ok=True)
    MODEL_NAME = f"{model_name}_v{model_version}"
    BACKBONE = backbone


    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nDevice: {device}")

    # Load and filter labeled data (True/False only, skip Uncertain)
    df = tsv_data[tsv_data["has_rings"].isin(["True", "False"]) & (tsv_data["manually_verified"] == "True")].copy()
    print(f"Labeled images: {len(df)}  "
          f"(True: {(df['has_rings']=='True').sum()}, "
          f"False: {(df['has_rings']=='False').sum()})")

    # Train/val split — stratified to keep class balance
    train_df, val_df = train_test_split(
        df, test_size=VAL_SPLIT, random_state=RANDOM_SEED,
        stratify=df["has_rings"]
    )
    print(f"Train: {len(train_df)}  Val: {len(val_df)}")

    # Datasets and loaders
    train_transform, val_transform = get_transforms()
    train_ds = RingDataset(train_df, IMAGE_DIR, train_transform)
    val_ds   = RingDataset(val_df,   IMAGE_DIR, val_transform)
    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_dl   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False)

    # Model, loss, optimizer
    model, trainable_params = build_model()
    model     = model.to(device)
    pos_weight = torch.tensor([POS_WEIGHT]).to(device)
    criterion  = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.Adam(trainable_params, lr=LR)

    # Training
    print(f"\nTraining for {EPOCHS} epochs...\n")
    best_val_acc = 0
    history = []

    for epoch in range(1, EPOCHS + 1):
        train_loss, train_acc = train(model, train_dl, optimizer, criterion, device)
        val_loss,   val_acc, val_preds, val_labels = evaluate(model, val_dl, criterion, device)

        history.append({
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc":  round(train_acc,  4),
            "val_loss":   round(val_loss,   4),
            "val_acc":    round(val_acc,    4),
        })

        print(f"Epoch {epoch:>2}/{EPOCHS}  "
              f"train_loss={train_loss:.4f}  train_acc={train_acc:.3f}  "
              f"val_loss={val_loss:.4f}  val_acc={val_acc:.3f}")

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), MODEL_DIR / f"{MODEL_NAME}.pth")
            print(f"             ✓ Saved best model (val_acc={val_acc:.3f})")

    # Final report on validation set
    print(f"\n{'='*50}")
    print(f"Best val accuracy: {best_val_acc:.3f}")
    print(f"\nClassification Report:")
    print(classification_report(val_labels, val_preds,
                                target_names=["no_rings", "has_rings"]))
    print(f"Confusion Matrix:")
    print(confusion_matrix(val_labels, val_preds))

    # Save metadata alongside the model
    metadata = {
        "model_name":    MODEL_NAME,
        "trained_at":    datetime.now().isoformat(),
        "n_train":       len(train_df),
        "n_val":         len(val_df),
        "n_true":        int((df["has_rings"] == "True").sum()),
        "n_false":       int((df["has_rings"] == "False").sum()),
        "best_val_acc":  round(best_val_acc, 4),
        "epochs":        EPOCHS,
        "image_size":    IMAGE_SIZE,
        "architecture":  BACKBONE,
        "history":       history,
        "decision_threshold": DECISION_THRESHOLD,
    }
    with open(MODEL_DIR / f"{MODEL_NAME}_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nModel saved → {MODEL_DIR / MODEL_NAME}.pth")
    print(f"Metadata   → {MODEL_DIR / MODEL_NAME}_metadata.json\n")


