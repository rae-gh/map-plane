from map_plane.geom import pdbloader as pl
from map_plane.geom import pdbgeometry as pg
from map_plane import MPDATA_DIR

# Testing only geometry, nothing from dmap that sits at a higher level

def test_basic_functionality():
    # one meaningful test that the core function returns something sensible
    pass

def test_1ejg():
    po = pl.PdbLoader("1ejg",MPDATA_DIR,cif=False,source="ebi").load_pdb()
    geomm = pg.GeometryMaker([po])
    df_geos = geomm.calculateGeometry(["N:N+1", "C:N+1", "C:O"])
    df_info = geomm.calculateData(hues=["aa","bfactor","occupancy"])
    df_dssp = geomm.calculateDssp()
    print("Test 1ejg geometry")
    print(df_geos.head())
    print("Test 1ejg data")
    print(df_info.head())
    print("Test 1ejg dssp")
    print(df_dssp.head())



if __name__ == "__main__":
    test_basic_functionality()
    test_1ejg()