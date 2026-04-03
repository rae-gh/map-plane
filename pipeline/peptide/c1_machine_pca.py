"""
PCA exploration of peptide bond features.

Runs PCA on the full feature set and produces:
1. Variance explained plot — how many components matter
2. Feature loadings — which features drive each component
3. PCA scatter plots — coloured by key structural properties
4. Summary report

Usage:
    python pipeline/c_machine_pca.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────
TSV_PATH    = Path("data/peptide_bonds_data.tsv")
RESULTS_DIR = Path("results/pca")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
from config import GEOM_PARAMS
from config import ADD_PARAMS


NUMERIC_FEATURES = [
    "resolution",
    "bf_N:CA:C", "bf_C:O"] + GEOM_PARAMS


CATEGORICAL_FEATURES = ["dssp", "aa"]

# Colour by these structural properties in scatter plots
COLOUR_BY = ["resolution", "aa_code", "dssp_code", "bf_N:CA:C"]
# ──────────────────────────────────────────────────────────────────────────────


def load_and_prepare(tsv_path):
    df = pd.read_csv(tsv_path, sep="\t", dtype=str)
    print(f"Loaded {len(df)} rows")
    df.dropna(subset=["dssp"], inplace=True)
    print(f"After dropping missing pdb_code/rid: {len(df)} rows")

    # Convert numeric
    for col in NUMERIC_FEATURES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            print(f"  Warning: missing column {col}")

    # Encode categorical
    df["dssp_code"] = df["dssp"].astype("category").cat.codes
    df["aa_code"]   = df["aa"].astype("category").cat.codes

    feature_cols = [c for c in NUMERIC_FEATURES if c in df.columns] + \
                   ["dssp_code", "aa_code"]

    # Drop rows with missing features
    df_clean = df.dropna(subset=feature_cols).copy()
    n_dropped = len(df) - len(df_clean)
    print(f"Clean rows: {len(df_clean)} ({n_dropped} dropped for missing features)")

    return df_clean, feature_cols


def run_pca(df, feature_cols):
    X = df[feature_cols].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)

    return pca, X_pca, scaler, feature_cols


def plot_variance_explained(pca, save_path, save=False):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Individual variance
    axes[0].bar(range(1, len(pca.explained_variance_ratio_) + 1),
                pca.explained_variance_ratio_ * 100)
    axes[0].set_xlabel("Principal Component")
    axes[0].set_ylabel("Variance Explained (%)")
    axes[0].set_title("Variance per Component")
    axes[0].set_xlim(0.5, min(20, len(pca.explained_variance_ratio_)) + 0.5)

    # Cumulative variance
    cumvar = np.cumsum(pca.explained_variance_ratio_) * 100
    axes[1].plot(range(1, len(cumvar) + 1), cumvar, marker="o", markersize=3)
    axes[1].axhline(80, color="red", linestyle="--", label="80%")
    axes[1].axhline(90, color="orange", linestyle="--", label="90%")
    axes[1].set_xlabel("Number of Components")
    axes[1].set_ylabel("Cumulative Variance Explained (%)")
    axes[1].set_title("Cumulative Variance")
    axes[1].legend()
    axes[1].set_xlim(0.5, min(20, len(cumvar)) + 0.5)

    plt.tight_layout()
    if save:
        plt.savefig(save_path, dpi=150)
        print(f"  Saved → {save_path}")
    print(f"Number of axes: {len(fig.axes)}")
    return fig



def plot_loadings(pca, feature_cols, n_components=4, save_path=None, save=False):
    fig, axes = plt.subplots(1, n_components, figsize=(5 * n_components, 6))

    for i, ax in enumerate(axes):
        loadings = pca.components_[i]
        sorted_idx = np.argsort(np.abs(loadings))[::-1]
        sorted_loadings = loadings[sorted_idx]
        sorted_features = [feature_cols[j] for j in sorted_idx]

        colors = ["red" if l < 0 else "steelblue" for l in sorted_loadings]
        ax.barh(range(len(sorted_features)), sorted_loadings, color=colors)
        ax.set_yticks(range(len(sorted_features)))
        ax.set_yticklabels(sorted_features, fontsize=7)
        ax.set_title(f"PC{i+1}\n({pca.explained_variance_ratio_[i]*100:.1f}%)")
        ax.axvline(0, color="black", linewidth=0.5)
        ax.set_xlabel("Loading")

    plt.tight_layout()
    if save:
        plt.savefig(save_path, dpi=150)
        print(f"  Saved → {save_path}")
    return fig


def plot_scatter(df, X_pca, save_path,save=False):
    n_plots = len(COLOUR_BY)
    fig, axes = plt.subplots(1, n_plots, figsize=(6 * n_plots, 5))

    for ax, col in zip(axes, COLOUR_BY):
        if col not in df.columns:
            continue

        values = pd.to_numeric(df[col], errors="coerce")

        # Check if categorical (low number of unique values)
        unique_vals = df[col].nunique()

        if unique_vals <= 20:  # categorical — use legend
            categories = df[col].dropna().unique()
            colors = cm.tab20(np.linspace(0, 1, len(categories)))
            for cat, color in zip(sorted(categories), colors):
                mask = df[col] == cat
                ax.scatter(X_pca[mask, 0], X_pca[mask, 1],
                          c=[color], label=str(cat),
                          s=1, alpha=0.4)
            ax.legend(markerscale=5, fontsize=7,
                     loc="best", ncol=2)
        else:  # continuous — use colorbar
            sc = ax.scatter(X_pca[:, 0], X_pca[:, 1],
                           c=values, cmap="viridis",
                           s=1, alpha=0.4)
            plt.colorbar(sc, ax=ax)

        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.set_title(f"Coloured by {col}")

    plt.tight_layout()
    if save:
        plt.savefig(save_path, dpi=150)
        print(f"  Saved → {save_path}")
    return fig



def print_report(pca, feature_cols, on_progress=print):
    on_progress(f"\n{'='*50}")
    on_progress(f"  PCA SUMMARY")
    on_progress(f"{'='*50}")

    cumvar = np.cumsum(pca.explained_variance_ratio_) * 100
    for threshold in [50, 80, 90, 95]:
        n = np.argmax(cumvar >= threshold) + 1
        on_progress(f"  Components for {threshold}% variance: {n}")

    on_progress(f"\n  Top features per component:")
    for i in range(min(4, len(pca.components_))):
        loadings = pca.components_[i]
        top_idx = np.argsort(np.abs(loadings))[::-1][:3]
        top = [f"{feature_cols[j]} ({loadings[j]:.2f})" for j in top_idx]
        on_progress(f"  PC{i+1} ({pca.explained_variance_ratio_[i]*100:.1f}%): {', '.join(top)}")
    on_progress(f"{'='*50}\n")


def main(save=False, on_progress=print):
    print(f"\nLoading data...")
    df, feature_cols = load_and_prepare(TSV_PATH)

    print(f"\nRunning PCA on {len(feature_cols)} features...")
    pca, X_pca, scaler, feature_cols = run_pca(df, feature_cols)

    # Save PCA coordinates back to df
    df["pca_1"] = X_pca[:, 0]
    df["pca_2"] = X_pca[:, 1]

    print(f"\nGenerating plots...")
    fig1 = plot_variance_explained(pca, RESULTS_DIR / "variance_explained.png", save=save)
    fig2 = plot_loadings(pca, feature_cols, n_components=4,
                  save_path=RESULTS_DIR / "feature_loadings.png", save=save)
    fig3 = plot_scatter(df, X_pca, RESULTS_DIR / "pca_scatter.png", save=save)

    print_report(pca, feature_cols, on_progress=on_progress)

    # Save loadings to CSV for inspection
    loadings_df = pd.DataFrame(
        pca.components_[:10].T,
        index=feature_cols,
        columns=[f"PC{i+1}" for i in range(10)]
    )
    loadings_df.to_csv(RESULTS_DIR / "loadings.csv")
    print(f"  Loadings saved → {RESULTS_DIR / 'loadings.csv'}")

    # Save PCA coordinates
    df[["pdb_code", "rid", "aa", "pca_1", "pca_2"]].to_csv(
        RESULTS_DIR / "pca_coordinates.csv", index=False
    )
    print(f"  Coordinates saved → {RESULTS_DIR / 'pca_coordinates.csv'}")

    return fig1, fig2, fig3


if __name__ == "__main__":
    fig1, fig2, fig3 = main(save=True)

