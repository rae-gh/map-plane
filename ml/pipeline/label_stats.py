"""
Quick stats on labeling progress for peptide_bonds.tsv
"""

import pandas as pd
from pathlib import Path

TSV_PATH = Path("ml/data/peptide_bonds_data.tsv")

df = pd.read_csv(TSV_PATH, sep="\t", dtype=str)
total = len(df)

# ── Overall progress ───────────────────────────────────────────────────────────
labeled    = df["has_rings"].notna().sum()
unlabeled  = total - labeled
pct        = labeled / total * 100

print(f"\n{'='*40}")
print(f"  LABELING PROGRESS")
print(f"{'='*40}")
print(f"  Total images     : {total:>6}")
print(f"  Labeled          : {labeled:>6}  ({pct:.1f}%)")
print(f"  Unlabeled        : {unlabeled:>6}  ({100-pct:.1f}%)")

# ── Label breakdown ────────────────────────────────────────────────────────────
print(f"\n{'='*40}")
print(f"  LABEL BREAKDOWN")
print(f"{'='*40}")
counts = df["has_rings"].value_counts(dropna=False)
for label, count in counts.items():
    name = str(label) if pd.notna(label) else "Unlabeled"
    pct_l = count / total * 100
    print(f"  {name:<12} : {count:>6}  ({pct_l:.1f}%)")

# ── Classified by ──────────────────────────────────────────────────────────────
print(f"\n{'='*40}")
print(f"  CLASSIFIED BY")
print(f"{'='*40}")
by_counts = df["classified_by"].value_counts(dropna=True)
if len(by_counts) == 0:
    print("  None yet")
else:
    for classifier, count in by_counts.items():
        print(f"  {classifier:<16} : {count:>6}")

# ── Manual verification ────────────────────────────────────────────────────────
print(f"\n{'='*40}")
print(f"  MANUAL VERIFICATION")
print(f"{'='*40}")
verified   = (df["manually_verified"] == "True").sum()
unverified = labeled - verified
print(f"  Manually verified  : {verified:>6}")
print(f"  Not verified       : {unverified:>6}")

# ── Coverage across structures ─────────────────────────────────────────────────
print(f"\n{'='*40}")
print(f"  COVERAGE BY STRUCTURE")
print(f"{'='*40}")
struct_stats = df.groupby("pdb_code").apply(
    lambda x: pd.Series({
        "total"  : len(x),
        "labeled": x["has_rings"].notna().sum(),
        "pct"    : x["has_rings"].notna().sum() / len(x) * 100
    })
).reset_index()

# ── Verified breakdown by structure ───────────────────────────────────────────
print(f"\n{'='*40}")
print(f"  HUMAN VS MODEL BY STRUCTURE")
print(f"{'='*40}")
print(f"  {'PDB':<8} {'Human':>6} {'Model':>6} {'Verified':>9}")
print(f"  {'-'*35}")
for _, row in struct_stats.sort_values("pdb_code").iterrows():
    pdb = row["pdb_code"]
    subset = df[df["pdb_code"] == pdb]
    human    = (subset["classified_by"] == "human").sum()
    model    = (subset["classified_by"] != "human") & subset["classified_by"].notna()
    verified = (subset["manually_verified"] == "True").sum()
    print(f"  {pdb:<8} {int(human):>6} {int(model.sum()):>6} {int(verified):>9}")

# Show structures with any labels first
labeled_structs   = struct_stats[struct_stats["labeled"] > 0]
unlabeled_structs = struct_stats[struct_stats["labeled"] == 0]

if len(labeled_structs) > 0:
    print(f"  {'PDB':<8} {'Total':>6} {'Labeled':>8} {'%':>6}")
    print(f"  {'-'*32}")
    for _, row in labeled_structs.sort_values("pct", ascending=False).iterrows():
        print(f"  {row['pdb_code']:<8} {int(row['total']):>6} {int(row['labeled']):>8} {row['pct']:>5.1f}%")

print(f"\n  {len(unlabeled_structs)} structures with no labels yet")
print(f"{'='*40}\n")