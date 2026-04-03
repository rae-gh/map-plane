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
ls_geos.append("N:N+1")
ls_geos.append("C:N+1")
ls_geos.append("C:O")
ls_geos.append("N:O")
ls_geos.append("CA:CA+1")
ls_geos.append("CA-1:CA")
ls_geos.append("O-1:N")

ls_geos.append("N:CA:C:N+1")
ls_geos.append("C-1:N:CA:C")
ls_geos.append("N:CA:C:O")
ls_geos.append("CA-1:C-1:N:CA")
ls_geos.append("CA:C:N+1:CA+1")

ls_geos.append("N:CA:C")
ls_geos.append("CA:C:N+1")
ls_geos.append("C-1:N:CA")
ls_geos.append("N:CA:O")
ls_geos.append("CA-1:CA:CA+1")
ls_geos.append("N-1:O-1:N")

ls_extra = []
ls_extra.append("dssp")
ls_extra.append("motif_CA-1:CA:CA+1")
ls_extra.append("bf_N:CA:C")
ls_extra.append("bf_C:O")

out_tsv = f"{DATA_DIR}/peptide_bonds_data.tsv"
with open(out_tsv, "w") as out_f:
    out_f.write("pdb_code\tresolution\trid\tchain\taa\timage_name")
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
    print(f"{count}/{len(pdb_codes)}------ {pdb_code} {resolution} ------")
    ml = mman.MapsManager().get_or_create(pdb_code,file=1,header=1,values=1)
    mf = mfun.MapFunctions(pdb_code,ml.mobj,ml.pobj,interpolation)
    pobj = mf.pobj

    geomm = geom_maker([pobj])

    df_geos = geomm.calculateGeometry(ls_geos)
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
            out_f.write(f"{pdb_code}\t{resolution}\t{rid}\t{a1['chain']}\t{aa}\t{image_name}")
            for geocol in ls_extra + ls_geos:
                # match on chain and rid to get the geo value for this residue
                chain_df = df_geos[df_geos['chain'] == chn]
                rid_df = chain_df[chain_df['rid'] == rid]
                geoval = rid_df[geocol].values[0] if not rid_df.empty else None
                out_f.write(f"\t{str(geoval)}")
            out_f.write("\n")
            out_f.flush()
        ##########################################
        key1, a1 =pobj.get_next_key(key1)
        key2, a2 =pobj.get_next_key(key2)
        key3, a3 =pobj.get_next_key(key3)



