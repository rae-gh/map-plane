from map_plane.vxyz import vectorthree as v3
import map_plane.dmap.mapsmanager as mman
import map_plane.dmap.mapfunctions as mfun
import map_plane.dmap.mapplothelp as mph
from map_plane import MPDATA_DIR

pdb_code = "1ejg"
interpolation = "bspline"
map_path = f"{MPDATA_DIR}/{pdb_code}.ccp4_reconstructed.ccp4"
width = 6
samples = 100
slice_vectors = [
        (v3.VectorThree(4.91, 11.35, -3.00), 
         v3.VectorThree(3.66, 10.58, -3.46), 
         v3.VectorThree(5.84, 10.73, -2.48)),
    ]


def test_pdbmap():         
    ml = mman.MapsManager().get_or_create(pdb_code, file=1, header=1, values=1)        
    mf = mfun.MapFunctions(pdb_code, ml.mobj, ml.pobj, interpolation)

    filename = "tests/tmp/test_pdbmap.png"

    for cc,ll,pp in slice_vectors:
        vals2d = mf.get_slice(cc,ll,pp,width,samples,interpolation,deriv=0,ret_type="2d")
        mplot = mph.MapPlotHelp(filename)
        mplot.make_plot_slice_2d(
            vals2d,            
            max_percent=95,
            samples=samples,
            width=width,
            points=[cc,ll,pp],
            title=pdb_code)


def test_recmap():         
    ml = mman.MapsManager().get_or_create(pdb_code, file=1, header=1, values=1)    
    ml.load_map_from_path(map_path, diff=False)        
    mf = mfun.MapFunctions(pdb_code, ml.mobj, ml.pobj, interpolation)
            
    filename = "tests/tmp/test_recmap.png"
    
    for cc,ll,pp in slice_vectors:
        vals2d = mf.get_slice(cc,ll,pp,width,samples,interpolation,deriv=0,ret_type="2d")
        mplot = mph.MapPlotHelp(filename)
        mplot.make_plot_slice_2d(
            vals2d,            
            max_percent=95,
            samples=samples,
            width=width,
            points=[cc,ll,pp],
            title=pdb_code)

if __name__ == "__main__":    
    test_pdbmap()
    test_recmap()