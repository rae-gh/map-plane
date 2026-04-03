import plotly
import streamlit as st
from streamlit import session_state as ss


import pandas as pd
from pathlib import Path
from pipeline.peptide.config import GEOM_PARAMS
from pipeline.peptide.config import ADD_PARAMS
from pipeline.peptide.config import DSSP_MAP
from pipeline.peptide import c0_machine_correlation as corr_module
from pipeline.peptide import c1_machine_pca as pca_module
from pipeline.peptide import c2_machine_umap as c2_machine_umap



import plotly.express as px

st.set_page_config(
        page_title="classifier",
        page_icon="🔮",
        layout="wide",
)
st.title("🔮 Peptide Bond Features - Web App")

all_tabs = []
all_tabs.append("All data")
all_tabs.append("Chosen images")
all_tabs.append("Group by")
all_tabs.append("Geometry")
all_tabs.append("Correlation")
all_tabs.append("PCA")
all_tabs.append("Umap")

(tabAll, tabImages, tabGroup, tabGeom, tabCorr, tabPCA, tabUmap) = st.tabs(all_tabs)

with tabAll:

    df_all_features = pd.read_csv("data/peptide_bonds_data.tsv", sep="\t", dtype=str)
    # specify coluim types to avoid warnings
    numeric_cols = GEOM_PARAMS + ["resolution", "bf_N:CA:C", "bf_C:O", "O-1:N", "count"]
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

    # drop all NA rows in dssp and aa for the group by tab
    filtered.dropna(subset=["dssp", "aa"], inplace=True)
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
    dssps = " ".join([f"{code}: {desc}" for code, desc in DSSP_MAP.items()])
    st.code(f"{dssps}", language="text")

    if group_col1 == group_col2:
        st.warning("Please select two different columns to group by.")
    else:

        if group_col1 and group_col2:
            group_counts = df_all_features.groupby([group_col1, group_col2]).size()
            group_counts = group_counts.reset_index(name="count").sort_values("count", ascending=False)
            st.write(f"Counts by {group_col1} and {group_col2}:")
            st.dataframe(group_counts, width="stretch", hide_index=True)

with tabGeom:

    sel_lengths = [col for col in df_all_features.columns if col.count(":") == 1 and "_" not in col]
    sel_angles = [col for col in df_all_features.columns if col.count(":") == 2 and "_" not in col]
    sel_dihedrals = [col for col in df_all_features.columns if col.count(":") == 3 and "_" not in col]
    sel_lengths.sort()
    sel_angles.sort()
    sel_dihedrals.sort()
    #st.write(sel_lengths)
    #st.write(sel_angles)
    #st.write(sel_dihedrals)

    st.write("Geometry features on filtered subset...")
    use_df_for_geom = filtered.copy()
    cols = st.columns(3)
    hue_cols = ["count"]
    for col in df_all_features.columns:
        hue_cols.append(col)

    def get_list(x, axis=None):
        if x == "lengths":
            return sel_lengths
        elif x == "angles":
            return sel_angles
        elif x == "dihedrals":
            return sel_dihedrals
        else:
            if axis == "hue":
                return ["count"] + [col for col in df_all_features.columns if col not in sel_lengths + sel_angles + sel_dihedrals]
            else:
                return [col for col in df_all_features.columns if col not in sel_lengths + sel_angles + sel_dihedrals]

    with cols[0]:
        x_opts = st.radio("X-axis type", options=["lengths", "angles", "dihedrals", "other"], index=1, horizontal=True)
        x_axis = st.selectbox("X-axis", options=get_list(x_opts), index=0)
    with cols[1]:
        y_opts = st.radio("Y-axis type", options=["lengths", "angles", "dihedrals", "other"], index=2, horizontal=True)
        y_axis = st.selectbox("Y-axis", options=get_list(y_opts), index=1)
    with cols[2]:
        hue_opts = st.radio("Colour by type", options=["lengths", "angles", "dihedrals", "other"], index=3, horizontal=True)
        hue_axis = st.selectbox("Colour by", options=get_list(hue_opts, "hue"), index=0)


    if x_axis == y_axis:
        st.warning("Please select different columns for x and y axes.")
    else:

        # Modes are:
        #1. All numerical
        #2. All categorical
        # Pick color args based on hue type
        if hue_axis in numeric_cols and hue_axis != "count":
            color_kwargs = {"color_continuous_scale": "Spectral"}
            q_low  = df_all_features[hue_axis].quantile(0.05)
            q_high = df_all_features[hue_axis].quantile(0.95)
            range_color = [q_low, q_high]
            st.write(f"""
                    Hue range: {hue_axis} **{df_all_features[hue_axis].min():.2f}** : **{df_all_features[hue_axis].max():.2f}**
                    Clipping to: **{range_color[0]:.2f}** : **{range_color[1]:.2f}** (5th to 95th percentile)
            """)


        else:
            color_kwargs = {"color_discrete_sequence": px.colors.qualitative.Vivid_r}


        mode = "mixed"
        if x_axis in numeric_cols and y_axis in numeric_cols:
            mode = "numeric"
        elif x_axis not in numeric_cols and y_axis not in numeric_cols:
            mode = "categorical"

        # a numerical hue needs clipping for outliers


        if hue_axis == "count":
            if mode == "categorical":
                df_grouped = (use_df_for_geom
                    .groupby([x_axis, y_axis])
                    .size()
                    .reset_index(name="count"))
                categories_y = df_grouped[y_axis].unique().tolist()
                fig = px.scatter(df_grouped, x=x_axis, y=y_axis,
                        color="count", size="count",
                        color_continuous_scale="matter",
                        opacity=0.7,
                        size_max = 15,
                        title=f"{y_axis} vs {x_axis} coloured by count")
            else:
            # in this case we are looking at the opcatiy rather than the count
                fig = px.scatter(df_all_features, x=x_axis, y=y_axis,
                        opacity=0.1,
                        title=f"{y_axis} vs {x_axis} coloured by count")
                fig.update_traces(marker=dict(color="firebrick", size=8))

        else:
            if mode == "categorical":
                top_50 = df_all_features[y_axis].value_counts().head(50).index
                df_plot = df_all_features[df_all_features[y_axis].isin(top_50)].copy()

                #df_plot = df_all_features[df_all_features[y_axis].notna()].copy()
                df_plot[y_axis] = df_plot[y_axis].astype(str)

                categories = sorted(df_plot[y_axis].dropna().unique())
                n_categories = len(categories)
                height = max(600, n_categories * 20)

                fig = px.scatter(df_plot, x=x_axis, y=y_axis, color=hue_axis,
                    title=f"{y_axis} vs {x_axis} coloured by {hue_axis}",
                    **color_kwargs,
                    category_orders={y_axis: categories})
                fig.update_layout(height=height)
                fig.update_traces(opacity=0.5)
                fig.update_yaxes(
                    type="category",
                    categoryorder="category ascending",
                    range=[-0.5, n_categories - 0.5]
                )
            else:
                fig = px.scatter(df_all_features, x=x_axis, y=y_axis,
                            color=hue_axis, opacity=0.5,
                            title=f"{y_axis} vs {x_axis} coloured by {hue_axis}",
                            **color_kwargs,
                            )

        if hue_axis in numeric_cols and hue_axis != "count":
            fig.update_coloraxes(cmin=range_color[0], cmax=range_color[1])

        # if the x and y are the same type, use the same axis range for better comparison
        if x_axis in sel_lengths and y_axis in sel_lengths:
            fig.update_layout(yaxis=dict(scaleanchor="x", scaleratio=1))
        elif x_axis in (sel_angles + sel_dihedrals) and y_axis in (sel_angles + sel_dihedrals):
            fig.update_layout(yaxis=dict(scaleanchor="x", scaleratio=1))


        fig.update_layout(
            xaxis=dict(autorange=True),
            yaxis=dict(autorange=True)
        )
        fig.update_layout(
            xaxis=dict(showgrid=True, gridcolor="lightgrey", gridwidth=0.5),
            yaxis=dict(showgrid=True, gridcolor="lightgrey", gridwidth=0.5)
        )
        fig.update_layout(height=650, width=650)

        st.plotly_chart(fig, width=700, height=700)



with tabCorr:
    cont = st.empty()
    lines = []
    def on_progress(msg):
        lines.append(msg)
        cont.code("\n".join(lines))
    corr, fig1, fig2 = corr_module.main(on_progress=on_progress)
    #st.dataframe(corr)
    cols = st.columns(2)
    with cols[0]:
        st.plotly_chart(fig1, width=700, height=700)
    with cols[1]:
        st.plotly_chart(fig2, width=700, height=700)

with tabPCA:
    cont = st.empty()
    lines = []
    def on_progress(msg):
        lines.append(msg)
        cont.code("\n".join(lines))
    fig1, fig2, fig3 = pca_module.main(save=False, on_progress=on_progress)
    with st.expander("PCA variance explained", expanded=True):
        st.write("The first plot shows the cumulative variance explained by the principal components. This helps to determine how many components are needed to capture most of the variance in the data.")
        st.pyplot(fig1, width="content")
    with st.expander("PCA feature loadings"):
        st.write("The second plot shows the loadings of each feature on the principal components. This helps to identify which features contribute most to each component.")
        st.pyplot(fig2, width="content")
    with st.expander("PCA scatter plot"):
        st.write("The third plot shows the data points projected onto the first two principal components, coloured by a selected structural property.")
        st.pyplot(fig3, width="content")

with tabUmap:
    st.write("UMAP analysis is coming soon...")
    with st.spinner("Running UMAP analysis...", show_time=True):
        fig, df = c2_machine_umap.main()
    st.plotly_chart(fig, width=700, height=700)
    st.dataframe(df)


st.write("---  ")
st.write("**References**")
st.caption("Hekkelman ML, Salmoral DÁ, Perrakis A, Joosten RP DSSP 4: FAIR annotation of protein secondary structure. Protein Science. 2025; 34(8):e70208.")
st.caption("Kabsch W, Sander C. Dictionary of protein secondary structure: pattern recognition of hydrogen-bonded and geometrical features. Biopolymers 1983; 22:2577-2637.")

