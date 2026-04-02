import plotly
import streamlit as st
from streamlit import session_state as ss


import pandas as pd
from pathlib import Path
from pipeline.peptide.config import GEOM_PARAMS
from pipeline.peptide.config import ADD_PARAMS
from pipeline.peptide.config import DSSP_MAP



import plotly.express as px

st.set_page_config(
        page_title="classifier",
        page_icon="🔮",
        layout="wide",
)
st.title("🔮 Peptide Bond Features - Web App")

tabAll, tabImages, tabGroup, tabGeom, tabPCA = st.tabs(["All data", "Chosen images", "Group by", "Geometry", "PCA"])

with tabAll:

    df_all_features = pd.read_csv("data/peptide_bonds_data.tsv", sep="\t", dtype=str)
    # specify coluim types to avoid warnings
    numeric_cols = GEOM_PARAMS + ["resolution", "bf_N:CA:C", "bf_C:O", "O-1:N"]
    for col in numeric_cols:
        if col in df_all_features.columns:
            df_all_features[col] = pd.to_numeric(df_all_features[col], errors="coerce")

    st.write(f"Loaded {len(df_all_features)} rows of peptide bond data.")

    query = st.text_input("Filter (pandas query syntax)",
                        placeholder="aa == 'CYS' and resolution < 0.7 and dssp.notna()",
                        help = "Use pandas query syntax to filter the data. For example: aa == 'CYS' and resolution < 0.7 and dssp.notna()")
    try:
        filtered = df_all_features.query(query) if query else df_all_features
        st.write(f"{len(filtered)} rows")
    except Exception as e:
        st.error(f"Invalid query: {e}")
        filtered = df_all_features

    st.dataframe(filtered)

with tabImages:
    if len(filtered) > 500:
        st.warning("Too many rows to show images. Please filter down to 200 or fewer.")
    else:
        st.write("Showing images for filtered data:")
        pdb = ""
        count = 0
        for idx, row in filtered.iterrows():
            new_pdb = row["pdb_code"]
            if new_pdb != pdb:
                pdb = new_pdb
                st.write(f"### {pdb} - {row['resolution']} Å")
                cols = st.columns(4)
                count = 0
            with cols[count % 4]:
                count += 1
                st.write(row["pdb_code"], row["chain"], row["rid"], row["aa"], row["dssp"], f"resolution: {row['resolution']}")
                image_path = Path(f"data/images/peptide_bonds/{row['image_name']}")
                if image_path.exists():
                    st.image(str(image_path), width=200)
                else:
                    st.warning(f"Image not found: {image_path}")
with tabGroup:
    cols = st.columns(3)
    with cols[0]:
        group_col1 = st.selectbox("Group by 1", options=df_all_features.columns, index=0)
    with cols[1]:
        group_col2 = st.selectbox("Group by 2", options=df_all_features.columns, index=1)
    with cols[2]:
        st.write("DSSP categories")
        st.write(DSSP_MAP)

    if group_col1 == group_col2:
        st.warning("Please select two different columns to group by.")
    else:

        if group_col1 and group_col2:
            group_counts = df_all_features.groupby([group_col1, group_col2]).size()
            group_counts = group_counts.reset_index(name="count").sort_values("count", ascending=False)
            st.write(f"Counts by {group_col1} and {group_col2}:")
            st.dataframe(group_counts, use_container_width=False, hide_index=True)

with tabGeom:
    st.write("Geometry features...")
    cols = st.columns(3)
    with cols[0]:
        x_axis = st.selectbox("X-axis", options=df_all_features.columns, index=10)
    with cols[1]:
        y_axis = st.selectbox("Y-axis", options=df_all_features.columns, index=11)
    with cols[2]:
        hue_axis = st.selectbox("Colour by", options=df_all_features.columns, index=9)

    fig = px.scatter(df_all_features, x=x_axis, y=y_axis, color=hue_axis, opacity=0.5, title=f"{y_axis} vs {x_axis} coloured by {hue_axis}",
                     color_continuous_scale="Spectral",
                     color_discrete_sequence=px.colors.qualitative.Vivid_r)
    st.plotly_chart(fig)



with tabPCA:
    st.write("PCA features coming soon...")

st.write("---  ")
st.write("**References**")
st.caption("Hekkelman ML, Salmoral DÁ, Perrakis A, Joosten RP DSSP 4: FAIR annotation of protein secondary structure. Protein Science. 2025; 34(8):e70208.")
st.caption("Kabsch W, Sander C. Dictionary of protein secondary structure: pattern recognition of hydrogen-bonded and geometrical features. Biopolymers 1983; 22:2577-2637.")

