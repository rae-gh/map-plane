
from os.path import exists
import gemmi



from map_plane.gemi import cifobject as po
from map_plane import MPDATA_DIR

"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
class CifFile(object):
    def __init__(self, pdb_code, path):
        self.pdb_code = pdb_code        
        self.cif_filepath = path
        self.pobj = po.CifObject(pdb_code)
    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
    def exists_pdb(self):
        return exists(self.cif_filepath)                    
    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
    def load_pdb(self):      
        structure = gemmi.read_structure(self.cif_filepath)        
        self.pobj.add_atoms(structure)        
        return self.pobj
    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""