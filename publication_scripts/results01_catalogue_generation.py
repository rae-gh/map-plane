from pathlib import Path

from map_plane.vxyz import vectorthree as v3
import map_plane.dmap.mapsmanager as mman
import map_plane.dmap.mapfunctions as mfun
import map_plane.dmap.mapplothelp as mph
from map_plane import MPDATA_DIR

# PDB query performed manually 2026-03-22
# Criteria: X-ray diffraction, resolution < 0.8 Å, has EDS map
# 62 structures returned

####### CONFIGURATION ####################
width = 6
samples = 100
interpolation = "bspline"
#############################################

SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

with open(f"{SCRIPT_DIR}/pdb_query_2026-03-22.txt") as f:
    pdb_codes = [code.strip().lower() for code in f.read().split(',')]

#pdb_codes = ["1ejg"]


mman.MapsManager().set_dir(MPDATA_DIR)
print("Data directory set to: ", MPDATA_DIR)


for pdb_code in pdb_codes:
    print("------", pdb_code, "------")
    ml = mman.MapsManager().get_or_create(pdb_code,file=1,header=1,values=1)
    if ml is None:
        print(f"Failed to load map for {pdb_code}, skipping.")
        continue
    resolution = ""
    if pdb_code in ml.map_info:
        for val in ml.map_info[pdb_code]:
            if "author_provided" in val:
                if "resolution_high" in val["author_provided"]:
                    resolution = val["author_provided"]["resolution_high"]
                    print(f"  Resolution: {resolution}")

    mf = mfun.MapFunctions(pdb_code,ml.mobj,ml.pobj,interpolation)
    pobj = mf.pobj

    a1,a2,a3 = pobj.get_first_three()
    key1=pobj.get_key(a1)
    print(f"First key: {key1}")

    k2 = pobj.get_next_key(key1, offset=5)
    a2 = pobj.get_atm_key(k2)
    print(k2)
    k3 = pobj.get_next_key(k2, offset=5)
    a3 = pobj.get_atm_key(k3)
    print(k3)

    residues = [a1, a2, a3]

    for residuemap in residues:
        print(residuemap)
        aa = residuemap["aa"]
        residue = int(residuemap["rid"])
        print(f"Atoms: {residue} {aa}")
        central_atoms = [f"A:{residue}@C.A"]
        linear_atoms = [f"A:{residue}@CA.A"]
        planar_atoms = [f"A:{residue}@O.A"]

        slice_vectors = []
        for i in range(len(central_atoms)):
            central_atom = central_atoms[i]
            linear_atom = linear_atoms[i]
            planar_atom = planar_atoms[i]
            # get the vectors
            cc = v3.VectorThree().from_coords(ml.pobj.get_coords_key(central_atom))
            ll = v3.VectorThree().from_coords(ml.pobj.get_coords_key(linear_atom))
            pp = v3.VectorThree().from_coords(ml.pobj.get_coords_key(planar_atom))
            slice_vectors.append((cc,ll,pp))

        filename = f"{RESULTS_DIR}/{resolution}_{pdb_code}_peptide_{residue}.png"
        for cc,ll,pp in slice_vectors:
            vals2d = mf.get_slice(cc,ll,pp,width,samples,interpolation,deriv=0,ret_type="2d")
            mplot = mph.MapPlotHelp(filename)
            mplot.make_plot_slice_2d(vals2d,
                                    min_percent=1,
                                    max_percent=0.15,
                                    samples=samples,
                                    width=width,
                                    #points=[cc,ll,pp],
                                    title=f"{pdb_code}-{resolution}-{residue}-{aa}",
                                    plot_type="heatmap",
                                    hue="WB")


