import streamlit as st
from streamlit import session_state as ss
import peptide.c0_human_label_images_streamlit as human_label
import peptide.c2_report_stats as report_stats
import peptide.c1_machine_train as machine_train

import pandas as pd
from pathlib import Path

st.set_page_config(
        page_title="classifier",
        page_icon="🔮",
        layout="wide",
)
st.title("🔮 Peptide Bond Classifier - Web App")


###########################################################
from contextlib import contextmanager, redirect_stdout
from io import StringIO
@contextmanager
def st_capture(output_func):
    try:
        with StringIO() as stdout, redirect_stdout(stdout):
            old_write = stdout.write

            def new_write(string):
                ret = old_write(string)
                output_func(stdout.getvalue())
                return ret

            stdout.write = new_write
            yield
    except Exception as e:
        st.error(str(e))
###########################################################


tab_config, tab_data, tab_images, tab_human_label, tab_review_stats, tab_machine_train = st.tabs(["Config", "Data", "Images", "human:label", "review:stats", "machine:train"])
with tab_config:
    ######################################
    ss.tsv_file = ss.get("tsv_file", "ml/data/peptide_bonds_data.tsv") if "tsv_file" in ss else "ml/data/peptide_bonds_data.tsv"
    ss.image_dir = ss.get("image_dir", "ml/data/images/peptide_bonds") if "image_dir" in ss else "ml/data/images/peptide_bonds"
    ss.tsv_data = ss.get("tsv_data", None) if "tsv_data" in ss else None
    ss.model_path = ss.get("model_path", "ml/models") if "model_path" in ss else "ml/models"
    ss.model_name = ss.get("model_name", "ring_classifier") if "model_name" in ss else "ring_classifier"
    ss.model_version = ss.get("model_version", 3) if "model_version" in ss else 3
    ss.need_new_image = ss.get("need_new_image", True) if "need_new_image" in ss else True
    ss.image = ss.get("image", None) if "image" in ss else None
    ss.row = ss.get("row", None) if "row" in ss else None
    ss.pos_weight = ss.get("pos_weight", 2.0) if "pos_weight" in ss else 2.0
    ss.decision_threshold = ss.get("decision_threshold", 0.40) if "decision_threshold" in ss else 0.40
    ss.backbone = ss.get("backbone", "uni") if "backbone" in ss else "uni"
    ss.idx = ss.get("idx", None) if "idx" in ss else None
    ######################################
    ss.tsv_file = st.text_input("Path to TSV data file", ss.tsv_file)
    ss.image_dir = st.text_input("Path to images directory", ss.image_dir)
    ss.model_path = st.text_input("Path to model directory", ss.model_path)
    ss.model_name = st.text_input("Model name", ss.model_name)
    ss.model_version = st.number_input("Model version (numeric)", value=ss.model_version, step=1)
    ss.pos_weight = st.number_input("Positive class weight (for imbalance)", value=ss.pos_weight, step=0.1, key="pos_weight_input")
    ss.decision_threshold = st.number_input("Decision threshold (0-1)", value=ss.decision_threshold, step=0.01, key="decision_threshold_input")
    ss.backbone = st.selectbox("Model backbone", options=["resnet18", "uni"], index=0 if ss.backbone=="resnet18" else 1)
    ######################################
with tab_data:
    if st.button("Reload Data") or ss.tsv_data is None:
        try:
            ss.tsv_data = pd.read_csv(ss.tsv_file, sep="\t", dtype=str)
            st.write(f"Loaded {len(ss.tsv_data)} rows from {ss.tsv_file}")
        except Exception as e:
            st.error(f"Error loading data: {e}")
    if ss.tsv_data is not None:
        st.dataframe(ss.tsv_data)
with tab_images:
    st.write("Image directory:")
    st.write(ss.image_dir)
    if st.button("Show Sample Images"):
        try:
            sample_images = list(Path(ss.image_dir).glob("*"))[:8]
            image_cols = st.columns(4)
            ic = 0
            for img_path in sample_images:
                with image_cols[ic%4]:
                    st.image(str(img_path), caption=img_path.name)
                ic += 1
        except Exception as e:
            st.error(f"Error loading images: {e}")
with tab_human_label:
    label_cols = st.columns(2)
    stats = human_label.get_stats(ss.tsv_data)
    narrowed_df=ss.tsv_data.copy()
    with label_cols[0]:
        resolution_max = st.slider("Max resolution to include", min_value=0.48, max_value=0.8, value=0.8, step=0.01)
        narrowed_df = narrowed_df[pd.to_numeric(narrowed_df["resolution"], errors='coerce') <= resolution_max]
        pdbs = narrowed_df["pdb_code"].dropna().unique()
    with label_cols[1]:
        st.write(f"Unclassified: {stats['unclassified']}  |  True: {stats['true']}  |  False: {stats['false']}")
        pdbs = st.multiselect("Select PDB codes to narrow down (multi-select)", options=sorted(pdbs), default=sorted(pdbs))
        narrowed_df = narrowed_df[narrowed_df["pdb_code"].isin(pdbs)]
    with label_cols[0]:
        aas = st.multiselect("Select Amino Acids to narrow down (multi-select)", options=sorted(narrowed_df["aa"].dropna().unique()), default=sorted(narrowed_df["aa"].dropna().unique()))
        narrowed_df = narrowed_df[narrowed_df["aa"].isin(aas)]
    with label_cols[1]:
        date_cols = st.columns(2)
        with date_cols[0]:
            date_before = st.date_input("images classified before this date)", value=None, key="date_before")
        with date_cols[1]:
            date_after = st.date_input("images classified after this date)", value=None, key="date_after")
        if date_before is not None:
            narrowed_df = narrowed_df[pd.to_datetime(narrowed_df["classified_datetime"], errors='coerce') <= pd.to_datetime(date_before)]
        if date_after is not None:
            narrowed_df = narrowed_df[pd.to_datetime(narrowed_df["classified_datetime"], errors='coerce') >= pd.to_datetime(date_after)]
    with label_cols[0]:
        ring_status = st.radio("Ring status", options=["True", "False", "Unclassified"], index=2, horizontal=True)
        if ring_status == "Unclassified":
            narrowed_df = narrowed_df[narrowed_df["classified_by"].isnull()]
        else:
            narrowed_df = narrowed_df[narrowed_df["has_rings"] == ring_status]
    with st.expander(f"Found {len(narrowed_df)} matching entries."):
        st.dataframe(narrowed_df)
    if st.button("Start Human Labeling Session"):
        ss.need_new_image = True
    if ss.need_new_image:
        ss.image, ss.row, ss.idx = human_label.get_next_image(
            df=narrowed_df,
            IMAGE_DIR=Path(ss.image_dir),
            last_idx=ss.idx
            )
        ss.need_new_image = False
    if ss.image is not None:
        st.write("---  ")
        image_cols = st.columns([2, 2, 2])
        with image_cols[0]:
            true_container = st.empty()
            marked_as = st.empty()
        with image_cols[1]:
            false_container = st.empty()
        with image_cols[0]:
            st.image(str(ss.image))
        with image_cols[2]:
            st.caption(f"Index: {ss.row.name}")
        count = 1
        for key,val in ss.row.items():
            count += 1
            with image_cols[count%2+1]:
                st.caption(f"{key}: {val}")
            #st.caption(f"PDB: {ss.row['pdb_code']}  |  Res: {ss.row['resolution']}  |  Classified by: {ss.row.get('classified_by', 'N/A')}")
        with true_container:
                if st.button("Mark as True (has rings)", type="primary"):
                    human_label.save_response(ss.tsv_data, ss.row, ss.tsv_file, "True")
                    marked_as.write("Marked as True")
                    ss.need_new_image = True

        with false_container:
                if st.button("Mark as False (no rings)", type="primary" ):
                    human_label.save_response(ss.tsv_data, ss.row, ss.tsv_file, "False")
                    marked_as.write("Marked as False")
                    ss.need_new_image = True

        st.write("---  ")
    else:
        st.write("No unclassified images found in the queue.")
with tab_review_stats:
    stats = report_stats.get_stats(ss.tsv_data)
    st.code(stats)
with tab_machine_train:
    if st.button("Start Machine Training Session"):
        with st.spinner("Training model... This may take a while.", show_time=True):
            output = st.empty()
            with st_capture(output.code):
                print("Starting training with settings:")
                print(f"  Positive class weight: {ss.pos_weight}")
                print(f"  Decision threshold: {ss.decision_threshold}")
                print(f"  Image directory: {ss.image_dir}")
                print(f"  Model path: {ss.model_path}")
                print(f"  Model name: {ss.model_name}")
                print(f"  Model version: {ss.model_version}")

                machine_train.train_model(ss.pos_weight,
                                        ss.decision_threshold,
                                        ss.tsv_data,
                                        ss.image_dir,
                                        ss.model_path,
                                        ss.model_name,
                                        ss.model_version,
                                        ss.backbone)
