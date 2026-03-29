from pathlib import Path

from map_plane.vxyz import vectorthree as v3
import map_plane.dmap.mapsmanager as mman
import map_plane.dmap.mapfunctions as mfun
import map_plane.dmap.mapplothelp as mph
from map_plane import MPDATA_DIR
import pandas as pd
import uuid



####### CONFIGURATION ####################
width = 6
samples = 100
interpolation = "bspline"
classify_mode = True
count_max = 1000000  # Set a maximum number of iterations
#############################################

if classify_mode:
    SCRIPT_DIR = Path(__file__).parent.parent
    RESULTS_DIR = SCRIPT_DIR / "results"
    DATA_DIR = SCRIPT_DIR / "data"
    IMAGE_DIR = DATA_DIR / "images/peptide_bonds"
else:
    SCRIPT_DIR = Path(__file__).parent
    RESULTS_DIR = SCRIPT_DIR / "results"
    DATA_DIR = SCRIPT_DIR / "data"
    IMAGE_DIR = DATA_DIR / "images/peptide_bonds"
RESULTS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# empty dir first
IMAGE_DIR.mkdir(exist_ok=True, parents=True)
for f in IMAGE_DIR.glob("*"):
    f.unlink()

print("Data directory set to: ", MPDATA_DIR)
print("Image directory set to: ", IMAGE_DIR)
print("Results directory set to: ", RESULTS_DIR)
print("Classify mode: ", classify_mode)


pbd_query_df = pd.read_csv(f"{SCRIPT_DIR}/data/query/pdb_query_results.tsv", delimiter="\t")
pdb_codes = pbd_query_df["pdb_code"].tolist()
print(f"Loaded {len(pdb_codes)} PDB codes from query results.")

mman.MapsManager().set_dir(MPDATA_DIR)
print("Data directory set to: ", MPDATA_DIR)

out_tsv = f"{DATA_DIR}/peptide_bonds_data.tsv"
with open(out_tsv, "w") as out_f:
    out_f.write("pdb_code\tresolution\trid\tchain\taa\timage_name\thas_rings\n")

count=0
for row in pbd_query_df.itertuples():
    if count > count_max:
        break
    count += 1
    pdb_code = row.pdb_code
    resolution = row.resolution
    print("------", pdb_code, resolution, "------")
    ml = mman.MapsManager().get_or_create(pdb_code,file=1,header=1,values=1)
    mf = mfun.MapFunctions(pdb_code,ml.mobj,ml.pobj,interpolation)
    pobj = mf.pobj

    a1,a2,a3 = pobj.get_first_three()
    print(f"First three keys: {a1}, {a2}, {a3}")
    key1=pobj.get_key(a1)
    key2=pobj.get_key(a2)
    key3=pobj.get_key(a3)

    while key1 != "" and key2 != "" and key3 != "":
        print(f"Keys: {key1}, {key2}, {key3}")
        print(a1)
        rid = int(a1["rid"])
        aa = a1["aa"]
        image_name = f"{pdb_code}_{resolution}_{rid}_{aa}.png"
        if classify_mode:
            image_name = f"{uuid.uuid4().hex}.png"
        print(f"Image name: {image_name}")
        with open(out_tsv, "a") as out_f:
            out_f.write(f"{pdb_code}\t{resolution}\t{rid}\t{a1['chain']}\t{aa}\t{image_name}\t\n")

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
        key1, a1 =pobj.get_next_key(key1)
        key2, a2 =pobj.get_next_key(key2)
        key3, a3 =pobj.get_next_key(key3)





#         slice_vectors = []

#             central_atom = central_atoms[i]
#             linear_atom = linear_atoms[i]
#             planar_atom = planar_atoms[i]
#             # get the vectors
#             cc = v3.VectorThree().from_coords(ml.pobj.get_coords_key(central_atom))
#             ll = v3.VectorThree().from_coords(ml.pobj.get_coords_key(linear_atom))
#             pp = v3.VectorThree().from_coords(ml.pobj.get_coords_key(planar_atom))
#             slice_vectors.append((cc,ll,pp))

#         filename = f"{RESULTS_DIR}/{resolution}_{pdb_code}_peptide_{residue}.png"
#         for cc,ll,pp in slice_vectors:
#             vals2d = mf.get_slice(cc,ll,pp,width,samples,interpolation,deriv=0,ret_type="2d")
#             mplot = mph.MapPlotHelp(filename)
#             mplot.make_plot_slice_2d(vals2d,
#                                     min_percent=1,
#                                     max_percent=0.15,
#                                     samples=samples,
#                                     width=width,
#                                     #points=[cc,ll,pp],
#                                     title=f"{pdb_code}-{resolution}-{residue}-{aa}",
#                                     plot_type="heatmap",
#                                     hue="WB")


