
from os.path import exists
import gemmi



from map_plane.gemi import cifobject as co
from map_plane import MPDATA_DIR

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CifFile(object):
    def __init__(self, pdb_code, path):
        self.pdb_code = pdb_code        
        self.cif_filepath = path
        self.pobj = co.CifObject(pdb_code)
        self.struc = None
        self.load_pdb()
        self.eds = []
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def exists_pdb(self):
        return exists(self.cif_filepath)                    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def load_pdb(self):      
        self.struc = gemmi.read_structure(self.cif_filepath)        
        self.pobj.add_atoms(self.struc)        
        return self.pobj
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def create_synthetic_ed(self, resolution=-1):
        dc = gemmi.DensityCalculatorX()        
        if resolution > 0:
            dc.d_min = resolution
            path_name = f"{self.cif_filepath}.calc.{round(resolution,2)}.ccp4"
        else:
            dc.d_min = self.struc.resolution
            path_name = f"{self.cif_filepath}.calc.ccp4"
        if not exists(path_name):            
            dc.rate = 3
            dc.grid.setup_from(self.struc)
            dc.set_refmac_compatible_blur(self.struc[0])
            dc.put_model_density_on_grid(self.struc[0])
            grid_calc = dc.grid
            ccp4 = gemmi.Ccp4Map()
            ccp4.grid = grid_calc
            ccp4.update_ccp4_header()
            ccp4.write_ccp4_map(path_name)
        if path_name not in self.eds:
            self.eds.append(path_name)
        return path_name