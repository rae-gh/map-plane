"""
UMAP + HDBSCAN exploration of peptide bond features.

Order of operations:
1. Load and prepare features (sin/cos encode dihedrals, encode categoricals)
2. Scale features
3. Run UMAP — project to 2D
4. Run HDBSCAN — label clusters in the UMAP embedding
5. Plot UMAP coloured by:
   - Each structural property (resolution, aa, dssp etc)
   - HDBSCAN cluster label
6. Report mean feature values per cluster — what drives the separation?
7. Save coordinates and cluster labels to CSV

Usage:
    python pipeline/d_machine_umap.py
"""

import pandas as pd
import numpy as np
import plotly.express as px
import umap
import hdbscan
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from config import GEOM_PARAMS

# ── Config ─────────────────────────────────────────────────────────────────────
TSV_PATH    = Path("data/peptide_bonds_data.tsv")
RESULTS_DIR = Path("results/umap")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

NUMERIC_FEATURES = [
    "resolution",
    "bf_N:CA:C", "bf_C:O",] + GEOM_PARAMS

DIHEDRAL_FEATURES = [
    "N:CA:C:N+1", "C-1:N:CA:C", "N:CA:C:O",
    "CA-1:C-1:N:CA", "CA:C:N+1:CA+1", "CA-1:CA:CA+1"
]

# UMAP parameters
N_NEIGHBORS  = 15
MIN_DIST     = 0.1
RANDOM_SEED  = 42

# HDBSCAN parameters
MIN_CLUSTER_SIZE = 50   # minimum points to form a cluster

# Colour by these structural properties
COLOUR_BY = ["resolution", "aa", "dssp", "bf_N:CA:C", "C:N+1"]
# ──────────────────────────────────────────────────────────────────────────────


# ── 1. Load and prepare ────────────────────────────────────────────────────────
def load_and_prepare(tsv_path):
    df = pd.read_csv(tsv_path, sep="\t", dtype=str)
    print(f"Loaded {len(df)} rows")

    for col in NUMERIC_FEATURES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            print(f"  Warning: missing column {col}")

    # Sin/cos encode dihedral angles — PCA and UMAP can't handle circular data
    for col in DIHEDRAL_FEATURES:
        if col in df.columns:
            df[f"{col}_sin"] = np.sin(np.radians(df[col]))
            df[f"{col}_cos"] = np.cos(np.radians(df[col]))

    # Encode categorical as numeric codes
    df["dssp_code"] = df["dssp"].astype("category").cat.codes
    df["aa_code"]   = df["aa"].astype("category").cat.codes

    # Build feature list — replace raw dihedrals with sin/cos pairs
    non_dihedral = [c for c in NUMERIC_FEATURES if c not in DIHEDRAL_FEATURES]
    sin_cos      = [f"{c}_sin" for c in DIHEDRAL_FEATURES if c in df.columns] + \
                   [f"{c}_cos" for c in DIHEDRAL_FEATURES if c in df.columns]
    feature_cols = non_dihedral + sin_cos + ["dssp_code", "aa_code"]
    feature_cols = [c for c in feature_cols if c in df.columns]

    df_clean = df.dropna(subset=feature_cols).copy()
    print(f"Clean rows: {len(df_clean)} ({len(df) - len(df_clean)} dropped)")

    return df_clean, feature_cols


# ── 2. Scale ───────────────────────────────────────────────────────────────────
def scale(df, feature_cols):
    X = df[feature_cols].values
    scaler = StandardScaler()
    return scaler.fit_transform(X)


# ── 3. UMAP ────────────────────────────────────────────────────────────────────
def run_umap(X_scaled):
    print(f"\nRunning UMAP (n_neighbors={N_NEIGHBORS}, min_dist={MIN_DIST})...")
    reducer = umap.UMAP(
        n_neighbors=N_NEIGHBORS,
        min_dist=MIN_DIST,
        n_components=2,
        random_state=RANDOM_SEED
    )
    embedding = reducer.fit_transform(X_scaled)
    print(f"Done.")
    return embedding


# ── 4. HDBSCAN ─────────────────────────────────────────────────────────────────
def run_hdbscan(embedding):
    print(f"\nRunning HDBSCAN (min_cluster_size={MIN_CLUSTER_SIZE})...")
    clusterer = hdbscan.HDBSCAN(min_cluster_size=MIN_CLUSTER_SIZE)
    labels = clusterer.fit_predict(embedding)
    counts = pd.Series(labels).value_counts().sort_index()
    for label, count in counts.items():
        name = f"Cluster {label}" if label >= 0 else "Noise"
        print(f"  {name}: {count} points")
    return labels


# ── 5. Plot ────────────────────────────────────────────────────────────────────
def plot_umap(df, save_dir):
    hover = ["pdb_code", "aa", "dssp", "resolution"]

    # Plot coloured by each structural property
    for col in COLOUR_BY:
        if col not in df.columns:
            continue

        is_numeric = col in NUMERIC_FEATURES

        if is_numeric:
            values = pd.to_numeric(df[col], errors="coerce")
            q_low  = values.quantile(0.05)
            q_high = values.quantile(0.95)
            fig = px.scatter(df, x="umap_x", y="umap_y",
                             color=col,
                             color_continuous_scale="Spectral",
                             range_color=[q_low, q_high],
                             opacity=0.4,
                             title=f"UMAP — {col}",
                             hover_data=hover)
        else:
            fig = px.scatter(df, x="umap_x", y="umap_y",
                             color=col,
                             color_discrete_sequence=px.colors.qualitative.Vivid,
                             opacity=0.4,
                             title=f"UMAP — {col}",
                             hover_data=hover)

        fig.update_traces(marker=dict(size=3))
        fig.update_layout(width=900, height=800)
        save_path = save_dir / f"umap_{col}.html"
        fig.write_html(save_path)
        print(f"  Saved → {save_path}")

    # Plot coloured by HDBSCAN cluster
    fig = px.scatter(df, x="umap_x", y="umap_y",
                     color=df["cluster"].astype(str),
                     color_discrete_sequence=px.colors.qualitative.Vivid,
                     opacity=0.4,
                     title="UMAP — HDBSCAN clusters",
                     hover_data=hover)
    fig.update_traces(marker=dict(size=3))
    fig.update_layout(width=900, height=800)
    fig.write_html(save_dir / "umap_clusters.html")
    print(f"  Saved → {save_dir / 'umap_clusters.html'}")
    return fig


# ── 6. Cluster report ──────────────────────────────────────────────────────────
def cluster_report(df):
    print(f"\n{'='*60}")
    print(f"  MEAN FEATURE VALUES PER CLUSTER")
    print(f"{'='*60}")

    # Numeric features per cluster
    means = df.groupby("cluster")[NUMERIC_FEATURES].mean()
    print(means.T.to_string())

    print(f"\n  DOMINANT AA PER CLUSTER:")
    for cluster in sorted(df["cluster"].unique()):
        subset = df[df["cluster"] == cluster]
        top_aa = subset["aa"].value_counts().head(3)
        print(f"  Cluster {cluster}: {dict(top_aa)}")

    print(f"\n  DOMINANT DSSP PER CLUSTER:")
    for cluster in sorted(df["cluster"].unique()):
        subset = df[df["cluster"] == cluster]
        top_dssp = subset["dssp"].value_counts().head(3)
        print(f"  Cluster {cluster}: {dict(top_dssp)}")

    print(f"{'='*60}\n")

    print(df[df["cluster"]==2]["aa"].value_counts().head(5))
    print(df[df["cluster"]==2]["pdb_code"].value_counts().head(10))

    fig = px.scatter(df, x="C-1:N:CA:C", y="N:CA:C:N+1",
                 color=df["cluster"].astype(str),
                 color_discrete_sequence=px.colors.qualitative.Vivid,
                 opacity=0.4,
                 title="Ramachandran coloured by HDBSCAN cluster",
                 hover_data=["pdb_code", "aa", "dssp"])
    fig.update_traces(marker=dict(size=3))
    fig.write_html(RESULTS_DIR / "ramachandran_clusters.html")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    # 1. Load
    df, feature_cols = load_and_prepare(TSV_PATH)

    # 2. Scale
    X_scaled = scale(df, feature_cols)

    # 3. UMAP
    embedding = run_umap(X_scaled)
    df["umap_x"] = embedding[:, 0]
    df["umap_y"] = embedding[:, 1]

    # 4. HDBSCAN
    df["cluster"] = run_hdbscan(embedding)

    # 5. Plot
    print(f"\nGenerating plots...")
    fig = plot_umap(df, RESULTS_DIR)

    # 6. Report
    cluster_report(df)

    # 7. Save
    save_cols = ["pdb_code", "rid", "aa", "dssp", "resolution",
                 "umap_x", "umap_y", "cluster"]
    df[save_cols].to_csv(RESULTS_DIR / "umap_coordinates.csv", index=False)
    print(f"Coordinates saved → {RESULTS_DIR / 'umap_coordinates.csv'}")

    return fig, df


if __name__ == "__main__":
    main()