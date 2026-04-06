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

from config import GEOM_PARAMS
from config import ADD_PARAMS



####### CONFIGURATION ####################
width = 6
samples = 100
interpolation = "bspline"
classify_mode = False
count_max = 10000000000  # Set a maximum number of iterations
skip_mode = True
#############################################
RESULTS_DIR = "results"
DATA_DIR = "data"
IMAGE_DIR = Path(f"{DATA_DIR}/images/peptide_bonds")
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
ls_geos = []
for gp in GEOM_PARAMS:
    ls_geos.append(gp)

ls_extra = []
for ap in ADD_PARAMS:
    ls_extra.append(ap)

out_tsv = f"{DATA_DIR}/peptide_bonds_data.tsv"
with open(out_tsv, "w") as out_f:
    out_f.write("pdb_code\tresolution\trid\tchain\taa\timage_name\tsoftware\trefinement\tr_work\tr_free\tstereo_target\tis_multipole")
    for gp in ls_extra + ls_geos:
        out_f.write(f"\t{gp}")
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

    core_list = []
    prev_list = []
    next_list = []
    both_list = []
    for col in ls_geos:
        if "-" not in col and "+" not in col:
            core_list.append(col)
        elif "-" in col and "+" not in col:
            prev_list.append(col)
        elif "+" in col and "-" not in col:
            next_list.append(col)
        else:
            both_list.append(col)
    df_core = geomm.calculateGeometry(core_list)
    df_prev = geomm.calculateGeometry(prev_list)
    df_next = geomm.calculateGeometry(next_list)
    df_both = geomm.calculateGeometry(both_list)

    #df_geos.to_csv(f"{DATA_DIR}/geometry_{pdb_code}.tsv", sep="\t", index=False)
    # this returns a dataframe with columns for each geometry and also columns for
    # residue level: aa, dssp
    # averaged atom level: bfactor, occupancy
    # we will choose 2 occupancy measures:
    # The tau angle for the bfactor and occupancy average for the backbone atoms only N:CA:C
    # The C:O bond length for an indication of O quality

   #print(df_geos.head(10))

    a1,a2,a3 = pobj.get_first_three()
    #print(f"First three keys: {a1}, {a2}, {a3}")
    key1=pobj.get_key(a1)
    key2=pobj.get_key(a2)
    key3=pobj.get_key(a3)

    while key1 != "" and key2 != "" and key3 != "":
        print(f"Keys: {key1}, {key2}, {key3}")
        chn = a1["chain"]
        rid = int(a1["rid"])
        aa = a1["aa"]
        image_name = f"{pdb_code}_{chn}_{rid}_{aa}.png"
        # check if image already exists
        exists_image = Path(f"{IMAGE_DIR}/{image_name}").exists()
        if skip_mode and exists_image:
            print(f"Already exists: {image_name}")
        else:

            if classify_mode:
                image_name = f"{uuid.uuid4().hex}.png"
            print(f"Image name: {image_name}")

            cc = v3.VectorThree().from_coords(pobj.get_coords_key(key2))
            ll = v3.VectorThree().from_coords(pobj.get_coords_key(key1))
            pp = v3.VectorThree().from_coords(pobj.get_coords_key(key3))

            vals2d = mf.get_slice(cc,ll,pp,width,samples,interpolation,deriv=0,ret_type="2d")
            mplot = mph.MapPlotHelp(f"{IMAGE_DIR}/{image_name}")
            mplot.make_plot_slice_2d(vals2d,
                                        min_percent=1,
                                        max_percent=0.15,
                                        samples=samples,
                                        width=width,
                                        title="",
                                        plot_type="heatmap",
                                        hue="WB",
                                        plotwidth=1000)

        ##########################################
        with open(out_tsv, "a") as out_f:
            out_f.write(f"{pdb_code}\t{resolution}\t{rid}\t{a1['chain']}\t{aa}\t{image_name}\t{software}\t{refinement}\t{r_work}\t{r_free}\t{stereo_target}\t{is_multipole}")
            for geocol in ls_extra + ls_geos:
                # match on chain and rid to get the geo value for this residue
                use_df = None
                if geocol in df_core.columns:
                    use_df = df_core
                elif geocol in df_prev.columns:
                    use_df = df_prev
                elif geocol in df_next.columns:
                    use_df = df_next
                elif geocol in df_both.columns:
                    use_df = df_both

                if use_df is not None:
                    chain_df = use_df[use_df['chain'] == chn]
                    rid_df = chain_df[chain_df['rid'] == rid]
                    geoval = rid_df[geocol].values[0] if not rid_df.empty else None
                    out_f.write(f"\t{str(geoval)}")
                else:
                    out_f.write("\t")
            out_f.write("\n")
            out_f.flush()
        ##########################################
        key1, a1 =pobj.get_next_key(key1)
        key2, a2 =pobj.get_next_key(key2)
        key3, a3 =pobj.get_next_key(key3)



