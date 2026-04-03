# ML Pipeline — Ring Artefact Classifier


python -m streamlit run ml/pipeline/webapp.py

# stdout and stderr to console and file
python pipeline/b_machine_generate_features.py 2>&1 | tee logs/b_machine_generate_features.log

## Purpose

A binary image classifier to identify peptide bond planes exhibiting
unambiguous Fourier truncation rings, defined as the visible presence
of **more than one concentric ring** around atomic centres.

Intended as a personal research tool to accelerate identification of
clear ring examples across the full dataset of 8,810 peptide bond
images. Not designed as a definitive automated annotation.

---

## Pipeline Scripts

Scripts are named by execution order and type:
- **machine_** — machine does something active (fetches, generates, trains, classifies)
- **human_** — human does something active (labels, reviews, decides)
- **report_** — passive information output, no action required

```
a_machine_fetch_structures.py      # Query PDB for ultra-high resolution structures
b_machine_generate_images.py       # Generate peptide bond plane images
c0_human_label.py                  # Label images / review model predictions
c1_machine_train.py                # Train classifier on verified labels
c2_report_stats.py                 # Report on model performance and label balance
d_machine_classify.py              # Run final classifier on all unverified images
```

---

## First Run

```bash
# 1. Fetch structures from PDB (run once)
python ml/pipeline/a_machine_fetch_structures.py

# 2. Generate all peptide bond images (run once, ~790MB)
python ml/pipeline/b_machine_generate_images.py

# 3. Label images manually
python ml/pipeline/c0_human_label.py

# 4. Train classifier on your labels
python ml/pipeline/c1_machine_train.py

# 5. Check model performance and label balance
python ml/pipeline/c2_report_stats.py

# → Repeat c0 → c1 → c2 until happy with the model

# 6. Run final classifier on all unverified images
python ml/pipeline/d_machine_classify.py
```

---

## Iterative Loop

After the first run, iterate until the model is good enough:

```
c0 (label more images / review model predictions)
    ↓
c1 (retrain on all verified labels)
    ↓
c2 (check stats — is performance good enough?)
    ↓
repeat until happy
    ↓
d  (final classification of all unverified images)
```

```bash
# Label more images or review model predictions
python ml/pipeline/c0_human_label.py
python ml/pipeline/c0_human_label.py --mode review
python ml/pipeline/c0_human_label.py --mode review --filter true
python ml/pipeline/c0_human_label.py --mode review --filter false

# Retrain (increment version number in config first)
python ml/pipeline/c1_machine_train.py

# Check performance
python ml/pipeline/c2_report_stats.py

# When happy — final classification
python ml/pipeline/d_machine_classify.py --model ring_classifier_vN
```

---

## Labeling Guide

### Definition
**True** — more than one concentric ring is clearly visible around atomic centres.
This is an objective, countable criterion. If you cannot see at least two rings, label False.

### Rules
- **True** — two or more concentric rings visible around atoms
- **False** — fewer than two rings visible, or no rings
- No Uncertain category — if in doubt, label False

### Controls
| Key | Action |
|-----|--------|
| `t` or `→` | True |
| `f` or `←` | False |
| `u` | Uncertain (use sparingly) |
| `z` | Undo |
| `q` | Save and quit |

---

## Data

| File | Description |
|------|-------------|
| `ml/data/peptide_bonds_data.tsv` | Master dataset — all images, labels, provenance |
| `ml/data/pdb_query_results.csv` | PDB codes returned by query |
| `ml/data/query_metadata.json` | Query date, parameters, structure count |
| `ml/data/images/peptide_bonds/` | All generated images (~790MB) |

### TSV Columns

| Column | Values | Description |
|--------|--------|-------------|
| `pdb_code` | e.g. `1ejg` | PDB identifier |
| `resolution` | e.g. `0.54` | Structure resolution in Å |
| `rid` | integer | Residue index |
| `aa` | e.g. `CYS` | Amino acid |
| `image_name` | UUID4.png | Random filename (blinded) |
| `has_rings` | True / False | Classification |
| `classified_by` | `human` / `ring_classifier_vN` | Who classified it |
| `manually_verified` | True / False | Whether a human has verified it |
| `confidence` | 0.0–1.0 | Model confidence (blank for human labels) |

---

## Models

Trained models are saved to `ml/models/` (not committed to git).

| File | Description |
|------|-------------|
| `ring_classifier_vN.pth` | Model weights |
| `ring_classifier_vN_metadata.json` | Training parameters and performance |

Final model weights will be deposited to Zenodo at publication.

---

## Dataset Provenance

Structures queried from RCSB PDB on **23 March 2026**.
Query: X-ray crystallography, resolution ≤ 0.8 Å.
Result: 91 structures, 8,810 peptide bonds.

See `ml/data/query_metadata.json` for full query details.

## Development Notes

Initial labeling used a binary True/False definition of ring presence.
After several iterations it became clear that the True category was
inconsistent — conflating unambiguous multiple rings with subtler
evidential patterns. The classifier performed poorly as a result.

The definition was revised to require **more than one visible concentric
ring** around atomic centres, making the positive class objective and
consistent. All labels were cleared and labeling restarted from scratch
with this definition.

## Model Version History

| Version | Labels | val_acc | Notes |
|---------|--------|---------|-------|
| v1 | - | - | First model with multiple rings definition |