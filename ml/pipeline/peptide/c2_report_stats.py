"""
Quick stats on labeling progress for peptide_bonds.tsv
"""

import pandas as pd
from pathlib import Path



def get_stats(tsv_data):

    report_string = ""

    total = len(tsv_data)

    # ── Overall progress ───────────────────────────────────────────────────────────
    labeled    = tsv_data["has_rings"].notna().sum()
    unlabeled  = total - labeled
    pct        = labeled / total * 100

    report_string += f"\n{'='*40}\n"
    report_string += f"  LABELING PROGRESS\n"
    report_string += f"{'='*40}\n"
    report_string += f"  Total images     : {total:>6}\n"
    report_string += f"  Labeled          : {labeled:>6}  ({pct:.1f}%)\n"
    report_string += f"  Unlabeled        : {unlabeled:>6}  ({100-pct:.1f}%)\n"

    # ── Label breakdown ────────────────────────────────────────────────────────────
    report_string += f"\n{'='*40}\n"
    report_string += f"  LABEL BREAKDOWN\n"
    report_string += f"{'='*40}\n"
    counts = tsv_data["has_rings"].value_counts(dropna=False)
    for label, count in counts.items():
        name = str(label) if pd.notna(label) else "Unlabeled"
        pct_l = count / total * 100
        report_string += f"  {name:<12} : {count:>6}  ({pct_l:.1f}%)\n"

    # ── Classified by ──────────────────────────────────────────────────────────────
    report_string += f"\n{'='*40}\n"
    report_string += f"  CLASSIFIED BY\n"
    report_string += f"{'='*40}\n"
    by_counts = tsv_data["classified_by"].value_counts(dropna=True)
    if len(by_counts) == 0:
        report_string += f"  None yet\n"
    else:
        for classifier, count in by_counts.items():
            report_string += f"  {classifier:<16} : {count:>6}\n"

    # ── Manual verification ────────────────────────────────────────────────────────
    report_string += f"\n{'='*40}\n"
    report_string += f"  MANUAL VERIFICATION\n"
    report_string += f"{'='*40}\n"
    verified   = (tsv_data["manually_verified"] == "True").sum()
    unverified = labeled - verified
    report_string += f"  Manually verified  : {verified:>6}\n"
    report_string += f"  Not verified       : {unverified:>6}\n"

    # ── Coverage across structures ─────────────────────────────────────────────────
    report_string += f"\n{'='*40}\n"
    report_string += f"  COVERAGE BY STRUCTURE\n"
    report_string += f"{'='*40}\n"
    struct_stats = tsv_data.groupby("pdb_code").apply(
        lambda x: pd.Series({
            "total"  : len(x),
            "labeled": x["has_rings"].notna().sum(),
            "pct"    : x["has_rings"].notna().sum() / len(x) * 100
        })
    ).reset_index()

    # ── Verified breakdown by structure ───────────────────────────────────────────
    report_string += f"\n{'='*40}\n"
    report_string += f"  HUMAN VS MODEL BY STRUCTURE\n"
    report_string += f"  {'PDB':<8} {'Human':>6} {'Model':>6} {'Verified':>9}\n"
    report_string += f"  {'-'*35}\n"
    for _, row in struct_stats.sort_values("pdb_code").iterrows():
        pdb = row["pdb_code"]
        subset = tsv_data[tsv_data["pdb_code"] == pdb]
        human    = (subset["classified_by"] == "human").sum()
        model    = (subset["classified_by"] != "human") & subset["classified_by"].notna()
        verified = (subset["manually_verified"] == "True").sum()
        report_string += f"  {pdb:<8} {int(human):>6} {int(model.sum()):>6} {int(verified):>9}\n"

    # Show structures with any labels first
    labeled_structs   = struct_stats[struct_stats["labeled"] > 0]
    unlabeled_structs = struct_stats[struct_stats["labeled"] == 0]

    if len(labeled_structs) > 0:
        report_string += f"  {'PDB':<8} {'Total':>6} {'Labeled':>8} {'%':>6}\n"
        report_string += f"  {'-'*32}\n"
        for _, row in labeled_structs.sort_values("pct", ascending=False).iterrows():
            report_string += f"  {row['pdb_code']:<8} {int(row['total']):>6} {int(row['labeled']):>8} {row['pct']:>5.1f}%\n"

    report_string += f"\n  {len(unlabeled_structs)} structures with no labels yet"
    report_string += f"\n  {len(labeled_structs)} structures with labels"
    report_string += f"\n{'='*40}\n"

    return report_string