"""
Correlation matrix exploration of peptide bond features.

Produces:
1. Full correlation heatmap (interactive HTML + static PNG)
2. Clustered correlation heatmap
3. High correlation pairs report (redundant features)

Usage:
    python pipeline/c_machine_correlation.py
"""

import pandas as pd
import numpy as np
import plotly.express as px
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform
from pathlib import Path
from config import GEOM_PARAMS

# ── Config ─────────────────────────────────────────────────────────────────────
TSV_PATH    = Path("data/peptide_bonds_data.tsv")
RESULTS_DIR = Path("results/correlation")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
NUMERIC_FEATURES = ["resolution", "bf_N:CA:C", "bf_C:O"] + GEOM_PARAMS
HIGH_CORR_THRESHOLD = 0.8
# ──────────────────────────────────────────────────────────────────────────────


def load_and_prepare(tsv_path):
    df = pd.read_csv(tsv_path, sep="\t", dtype=str)
    print(f"Loaded {len(df)} rows")

    for col in NUMERIC_FEATURES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            print(f"  Warning: missing column {col}")

    feature_cols = [c for c in NUMERIC_FEATURES if c in df.columns]
    df_clean = df.dropna(subset=feature_cols).copy()
    print(f"Clean rows: {len(df_clean)} ({len(df) - len(df_clean)} dropped)")

    return df_clean[feature_cols]


def plot_heatmap(corr, title):
    fig = px.imshow(
        corr,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        text_auto=".2f",
        aspect="auto",
        title=title,
    )
    fig.update_traces(textfont_size=8)
    fig.update_layout(
        width=900, height=800,
        coloraxis_colorbar=dict(title="r")
    )

    return fig


def plot_clustered_heatmap(corr):
    # Cluster features by correlation similarity
    dist = 1 - corr.abs()
    np.fill_diagonal(dist.values, 0)
    linkage_matrix = linkage(squareform(dist.values), method="average")
    order = leaves_list(linkage_matrix)

    corr_clustered = corr.iloc[order, order]

    fig = px.imshow(
        corr_clustered,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        text_auto=".2f",
        aspect="auto",
        title="Clustered Correlation Matrix",
    )
    fig.update_traces(textfont_size=8)
    fig.update_layout(
        width=900, height=800,
        coloraxis_colorbar=dict(title="r")
    )

    return fig

def report_high_correlations(corr, threshold, on_progress):
    on_progress(f"\n{'='*60}")
    on_progress(f"  HIGH CORRELATIONS (|r| > {threshold})")
    on_progress(f"{'='*60}")

    pairs = []
    cols = corr.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = corr.iloc[i, j]
            if abs(r) > threshold:
                pairs.append((cols[i], cols[j], r))

    if not pairs:
        on_progress(f"  None found above threshold {threshold}")
    else:
        pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        on_progress(f"  {'Feature A':<25}  {'Feature B':<25}  {'r':>6}")
        on_progress(f"  {'-'*60}")
        for a, b, r in pairs:
            on_progress(f"  {a:<25}  {b:<25}  {r:>6.3f}")

    on_progress(f"{'='*60}\n")
    return pairs


def main(on_progress):
    print(f"\nLoading data...")
    X = load_and_prepare(TSV_PATH)

    print(f"\nComputing correlation matrix ({len(X.columns)} features)...")
    corr = X.corr()

    print(f"\nGenerating plots...")
    fig1 = plot_heatmap(
        corr,
        title="Correlation Matrix"
    )
    fig2 = plot_clustered_heatmap(
        corr,
    )

    report_high_correlations(corr, HIGH_CORR_THRESHOLD, on_progress)

    return corr, fig1, fig2


if __name__ == "__main__":
    def on_progress(message):
        print(message)
    corr, fig1, fig2 = main(on_progress)

    corr.to_csv(RESULTS_DIR / "correlation_matrix.csv")
    on_progress(f"  Saved → {RESULTS_DIR / 'correlation_matrix.csv'}")

    save_path1 = RESULTS_DIR / "correlation_heatmap.png"
    fig1.write_html(save_path1.with_suffix(".html"))
    fig1.write_image(save_path1)
    on_progress(f"  Saved → {save_path1.with_suffix('.html')}")
    on_progress(f"  Saved → {save_path1}")

    save_path2 = RESULTS_DIR / "correlation_clustered.png"
    fig2.write_html(save_path2.with_suffix(".html"))
    fig2.write_image(save_path2)
    on_progress(f"  Saved → {save_path2.with_suffix('.html')}")
    on_progress(f"  Saved → {save_path2}")
