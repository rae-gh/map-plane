from pathlib import Path

from map_plane.vxyz import vectorthree as v3
import map_plane.dmap.mapsmanager as mman
import map_plane.dmap.mapfunctions as mfun
import map_plane.dmap.mapplothelp as mph
from map_plane import MPDATA_DIR


from map_plane.geom.pdbgeometry import GeometryMaker as geom_maker

import pandas as pd
import uuid
import os


####### CONFIGURATION ####################
width = 15
samples = 200
interpolation = "bspline"
classify_mode = False
count_max = 1000000  # Set a maximum number of iterations
skip_mode = False
#############################################
RESULTS_DIR = "results"
DATA_DIR = "data"
IMAGE_DIR = Path(f"{DATA_DIR}/images/hydrogen_bonds")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

if not skip_mode:
    # empty dir first
    for f in IMAGE_DIR.glob("*"):
        f.unlink()

print("Data directory set to: ", MPDATA_DIR)
print("Image directory set to: ", IMAGE_DIR)
print("Results directory set to: ", RESULTS_DIR)
print("Classify mode: ", classify_mode)


pbd_query_df = pd.read_csv(f"data/query_results/pdb_query_results.tsv", delimiter="\t")
pdb_codes = pbd_query_df["pdb_code"].tolist()

print(f"Loaded {len(pdb_codes)} PDB codes from query results.")
mman.MapsManager().set_dir(MPDATA_DIR)
print("Data directory set to: ", MPDATA_DIR)

# geom_params
ls_geos = ["NZ[aa|20]:(O)[dis|2.1><2.9,rid|>1,aa|20]"]
ls_extra = ["dssp"]

out_tsv = f"{DATA_DIR}/hydrogen_bonds_data.tsv"
with open(out_tsv, "w") as out_f:
    out_f.write("pdb_code\tresolution\trid\tchain\taa\timage_name\tsoftware\trefinement\tr_work\tr_free\tstereo_target\tis_multipole")
    for gp in ls_extra:
        out_f.write(f"\t{gp}")
    for gp in ls_geos:
        out_f.write(f"\t{gp}")
        out_f.write(f"\tinfo_{gp}")
    out_f.write("\n")
    out_f.flush()

count=0
for row in pbd_query_df.itertuples():
    if count > count_max:
        break
    count += 1
    pdb_code = row.pdb_code
    resolution = row.resolution
    software = row.software
    refinement = row.refinement
    r_work = row.r_work
    r_free = row.r_free
    stereo_target = row.stereo_target
    is_multipole = row.is_multipole

    print(f"{count}/{len(pdb_codes)}------ {pdb_code} {resolution} ------")
    ml = mman.MapsManager().get_or_create(pdb_code,file=1,header=1,values=1)
    mf = mfun.MapFunctions(pdb_code,ml.mobj,ml.pobj,interpolation)
    pobj = mf.pobj

    geomm = geom_maker([pobj])
    df_hb1 = geomm.calculateGeometry(ls_geos)

    if len(df_hb1) == 0:
        #print(f"No hydrogen bonds found for {pdb_code}, skipping...")
        continue
    print(f"Found {len(df_hb1)} hydrogen bonds for {pdb_code}.")
    #print(df_hb1.head(3).T)

    for idx, hb_row in df_hb1.iterrows():
        geo = ls_geos[0]
        chn = hb_row['chain']
        rid = hb_row['rid']
        aa = hb_row['aa']
        dis = hb_row[geo]
        info = hb_row[f"info_{geo}"]
        print(f"Processing {pdb_code} chain {chn} rid {rid} aa {aa} with distance {dis} and info {info}")
        #atm_key = f"{atm['chain']}:{ridn}@{atm['atm']}.{atm['version']}"
        #(A|LYS|36|NZ|488)(A|GLN|221|O|3101)
        info_split=info.split(")")
        info1=info_split[0].replace("(","").split("|")
        info2=info_split[1].replace("(","").split("|")
        key1=f"{info1[0]}:{info1[2]}@{info1[3]}.A"
        key2=f"{info2[0]}:{info2[2]}@{info2[3]}.A"
        key3=f"{info1[0]}:{info1[2]}@O.A"
        print(f"Keys: {key1}, {key2}, {key3}")

        image_name = f"{pdb_code}_{info1[1]}_{info2[1]}_{key1}_{key2}_".replace(":", "_").replace("@", "_").replace(".", "_")
        image_name1 = f"{image_name}heatmap.png"
        image_name2 = f"{image_name}contour.png"
        # check if image already exists
        exists_image = Path(f"{IMAGE_DIR}/{image_name1}").exists() and Path(f"{IMAGE_DIR}/{image_name2}").exists()
        if skip_mode and exists_image:
            print(f"Already exists: {image_name1} or {image_name2}, skipping...")
        else:

            if classify_mode:
                image_name = f"{uuid.uuid4().hex}_"
                image_name1 = f"{uuid.uuid4().hex}_heatmap.png"
                image_name2 = f"{uuid.uuid4().hex}_contour.png"
            print(f"Image name: {image_name1} and {image_name2}")

            cc = v3.VectorThree().from_coords(pobj.get_coords_key(key1))
            ll = v3.VectorThree().from_coords(pobj.get_coords_key(key2))
            pp = v3.VectorThree().from_coords(pobj.get_coords_key(key3))

            vals2d = mf.get_slice(cc,ll,pp,width,samples,interpolation,deriv=0,ret_type="2d")
            mplot1 = mph.MapPlotHelp(f"{IMAGE_DIR}/{image_name1}")
            mplot1.make_plot_slice_2d(vals2d,
                                        points = [cc,ll,pp],
                                        min_percent=5,
                                        max_percent=95,
                                        samples=samples,
                                        width=width,
                                        title="",
                                        plot_type="heatmap",
                                        hue="WB",
                                        plotwidth=1000)
            mplot2 = mph.MapPlotHelp(f"{IMAGE_DIR}/{image_name2}")
            mplot2.make_plot_slice_2d(vals2d,
                                        points = [cc,ll,pp],
                                        min_percent=3,
                                        max_percent=97,
                                        samples=samples,
                                        width=width,
                                        title="",
                                        plot_type="contour",
                                        hue="GBR",
                                        plotwidth=1000)

        ##########################################
        with open(out_tsv, "a") as out_f:
            out_f.write(f"{pdb_code}\t{resolution}\t{rid}\t{chn}\t{aa}\t{image_name}\t{software}\t{refinement}\t{r_work}\t{r_free}\t{stereo_target}\t{is_multipole}")
            for geocol in ls_extra:
                # match on chain and rid to get the geo value for this residue
                chain_df = df_hb1[df_hb1['chain'] == chn]
                rid_df = chain_df[chain_df['rid'] == rid]
                geoval = rid_df[geocol].values[0] if not rid_df.empty else None
                out_f.write(f"\t{str(geoval)}")
            for geocol in ls_geos:
                # match on chain and rid to get the geo value for this residue
                chain_df = df_hb1[df_hb1['chain'] == chn]
                rid_df = chain_df[chain_df['rid'] == rid]
                geoval = rid_df[geocol].values[0] if not rid_df.empty else None
                geoinfo = rid_df[f"info_{geocol}"].values[0] if not rid_df.empty else None
                out_f.write(f"\t{str(geoval)}")
                out_f.write(f"\t{str(geoinfo)}")
            out_f.write("\n")
            out_f.flush()



