from map_plane.vxyz import vectorthree as v3
import map_plane.dmap.mapsmanager as mman
import map_plane.dmap.mapfunctions as mfun
import map_plane.dmap.mapplothelp as mph
from map_plane import MPDATA_DIR

# test_dmap.py
def test_import():
    from map_plane import dmap
    assert dmap is not None

# one meaningful test that the core function returns something sensible
def test_basic_functionality():
    # Set the variables
    pdb_code = "1ejg"
    central_atoms = ["A:5@C.A","A:6@C.A","A:7@C.A","A:8@C.A"]
    linear_atoms = ["A:5@CA.A","A:6@CA.A","A:7@CA.A","A:8@CA.A"]
    planar_atoms = ["A:5@O.A","A:6@O.A","A:7@O.A","A:8@O.A"]
    interpolation = "bspline"
    width = 4.5 #Angstrom
    samples = 50
    depth_samples = 10
    # find relative path for data
    print("Data directory set to: ", MPDATA_DIR)
    # downloand/upload into memory the pdb and ccp4 data (0 means skip if not there, 1 means in this thread, 2 means in another thread and don't wait)
    ml = mman.MapsManager().get_or_create(pdb_code,file=1,header=1,values=1)
    mf = mfun.MapFunctions(pdb_code,ml.mobj,ml.pobj,interpolation)
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

        # CELL 4
    # 2d plot (s)

    filename = "tests/tmp/test_output.png"
    for cc,ll,pp in slice_vectors:
        vals2d = mf.get_slice(cc,ll,pp,width,samples,interpolation,deriv=0,ret_type="2d")
        mplot = mph.MapPlotHelp(filename)
        mplot.make_plot_slice_2d(vals2d,min_percent=0.9,max_percent=0.3,samples=samples,width=width,points=[cc,ll,pp],title=pdb_code)

if __name__ == "__main__":
    test_import()
    test_basic_functionality()