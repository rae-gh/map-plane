import os
import urllib.request
import gemmi


class Density:
    def __init__(self, path):
        self.path = path
        self.ed = self.load_density(path)
    def load_density(self,path):
        ed = gemmi.read_ccp4_map(path)
        return ed
    def make_roundtrip(self, resolution):
        # 1. Read a ccp4 file from disk
        m = gemmi.read_ccp4_map(self.path, setup=False)
        # 2. Get the grid and the unit cell
        grid = m.grid    
        # 3. Map → Structure factors (real-space FFT to reciprocal space)
        d_min = resolution   # adjust to match your map's resolution
        sf = gemmi.transform_map_to_f_phi(grid, half_l=True)  # returns RecgridComplexFloat
        # Convert to a Miller array you can inspect / manipulate
        mtz_data = sf.prepare_asu_data(dmin=d_min, with_sys_abs=False)    
        mtz = gemmi.Mtz()
        mtz.cell = grid.unit_cell
        mtz.spacegroup = grid.spacegroup
        mtz.add_dataset("from_map")
        mtz.add_column("H",   "H")
        mtz.add_column("K",   "H")
        mtz.add_column("L",   "H")
        mtz.add_column("F",   "F")
        mtz.add_column("PHI", "P")
        mtz.set_data(mtz_data) 
        #mtz.write_to_file("../data/mtz/1ejg-calc.mtz")    
        # 4. Structure factors → Electron density (reciprocal → real space) ─────────    
        new_grid = mtz.transform_f_phi_to_map("F", "PHI", sample_rate=3.0)
        # Write the reconstructed density back to CCP4
        new_ccp4 = gemmi.Ccp4Map()
        new_ccp4.grid = new_grid
        new_ccp4.update_ccp4_header()
        new_ccp4.write_ccp4_map(f"{self.path}_reconstructed.ccp4")
        return f"{self.path}_reconstructed.ccp4"


    
class DensityRspb:
    def __init__(self, pdb_code, data_path):
        self.pdb_code = pdb_code
        mid = pdb_code[1:3]
        self.resolution = None
        self.path_data = os.path.expanduser(data_path)
        self.url_cif = f"https://files.rcsb.org/download/{self.pdb_code}.cif"
        self.url_pdb = f"https://files.rcsb.org/download/{self.pdb_code}.pdb"
        self.url_raw_sf = f"https://files.rcsb.org/download/{self.pdb_code}-sf.cif"
        self.url_fofc2_sf = f"https://files.wwpdb.org/pub/pdb/validation_reports/{mid}/{self.pdb_code}/{self.pdb_code}_validation_2fo-fc_map_coef.cif.gz"
        self.url_fofc_sf = f"https://files.wwpdb.org/pub/pdb/validation_reports/{mid}/{self.pdb_code}/{self.pdb_code}_validation_fo-fc_map_coef.cif.gz"
        self.url_xml = f"https://files.wwpdb.org/pub/pdb/validation_reports/{mid}/{self.pdb_code}/{self.pdb_code}_validation.xml.gz"
        
        self.path_cif = f"{self.path_data}/{self.pdb_code}.rspb.cif"
        self.path_pdb = f"{self.path_data}/{self.pdb_code}.rspb.pdb"
        self.path_raw_sf = f"{self.path_data}/{self.pdb_code}-sf.rspb.cif"
        self.path_fofc2_sf = f"{self.path_data}/{self.pdb_code}_validation_2fo-fc_map_coef.rspb.cif.gz"
        self.path_fofc_sf = f"{self.path_data}/{self.pdb_code}_validation_fo-fc_map_coef.rspb.cif.gz"
        self.path_xml = f"{self.path_data}/{self.pdb_code}_validation.rspb.xml.gz"
        self.path_fofc2_ccp4 = f"{self.path_data}/{self.pdb_code}_2fofc.rspb.ccp4"
        self.path_fofc_ccp4 = f"{self.path_data}/{self.pdb_code}_fofc.rspb.ccp4"
        self.download()
        st = gemmi.read_structure(self.path_cif)
        self.resolution = st.resolution
        
    def download(self):
        if not os.path.exists(self.path_data):
            os.makedirs(self.path_data)
        if not os.path.exists(self.path_cif):
            urllib.request.urlretrieve(self.url_cif, self.path_cif)
        if not os.path.exists(self.path_pdb):
            urllib.request.urlretrieve(self.url_pdb, self.path_pdb)
        if not os.path.exists(self.path_raw_sf):
            urllib.request.urlretrieve(self.url_raw_sf, self.path_raw_sf)
        if not os.path.exists(self.path_fofc2_sf):
            urllib.request.urlretrieve(self.url_fofc2_sf, self.path_fofc2_sf)
        if not os.path.exists(self.path_fofc_sf):
            urllib.request.urlretrieve(self.url_fofc_sf, self.path_fofc_sf)
        if not os.path.exists(self.path_xml):
            urllib.request.urlretrieve(self.url_xml, self.path_xml)

        if not os.path.exists(self.path_fofc2_ccp4):
            doc_2fofc = gemmi.cif.read(self.path_fofc2_sf)
            rblock_2fofc = gemmi.as_refln_blocks(doc_2fofc)[0]
            grid_2fofc = rblock_2fofc.transform_f_phi_to_map('pdbx_FWT', 'pdbx_PHWT', sample_rate=3)
            ccp_2fofc = gemmi.Ccp4Map()
            ccp_2fofc.grid = grid_2fofc
            ccp_2fofc.update_ccp4_header()
            ccp_2fofc.write_ccp4_map(self.path_fofc2_ccp4)

        if not os.path.exists(self.path_fofc_ccp4):
            doc_fofc = gemmi.cif.read(self.path_fofc_sf)
            rblock_fofc = gemmi.as_refln_blocks(doc_fofc)[0]
            grid_fofc = rblock_fofc.transform_f_phi_to_map('pdbx_DELFWT', 'pdbx_DELPHWT', sample_rate=3)
            ccp_fofc = gemmi.Ccp4Map()
            ccp_fofc.grid = grid_fofc
            ccp_fofc.update_ccp4_header()
            ccp_fofc.write_ccp4_map(self.path_fofc_ccp4)

    def create_ccp4_from_sf(self, sf_path, ccp4_path):
        doc = gemmi.cif.read(sf_path)
        rblock = gemmi.as_refln_blocks(doc)[0]
        grid = rblock.transform_f_phi_to_map(
            'pdbx_FWT', 'pdbx_PHWT', sample_rate=3)
        ccp4 = gemmi.Ccp4Map()
        ccp4.grid = grid
        ccp4.update_ccp4_header()
        ccp4.write_ccp4_map(ccp4_path)


class DensityEbi:
    def __init__(self, pdb_code, data_path):
        self.pdb_code = pdb_code
        self.resolution = None
        self.path_data = os.path.expanduser(data_path)
        self.url_cif = f"https://www.ebi.ac.uk/pdbe/entry-files/download/{self.pdb_code}_updated.cif"
        self.url_raw_sf = f"https://www.ebi.ac.uk/pdbe/entry-files/r{self.pdb_code}sf.ent"
        self.url_fofc2_ccp4 = f"https://www.ebi.ac.uk/pdbe/entry-files/{self.pdb_code}.ccp4"
        self.url_fofc_ccp4 = f"https://www.ebi.ac.uk/pdbe/entry-files/{self.pdb_code}_diff.ccp4"

        self.path_cif = f"{self.path_data}/{self.pdb_code}.ebi.cif"
        self.path_raw_sf = f"{self.path_data}/{self.pdb_code}-sf.ebi.ent"
        self.path_fofc2_ccp4 = f"{self.path_data}/{self.pdb_code}_2fofc.ebi.ccp4"
        self.path_fofc_ccp4 = f"{self.path_data}/{self.pdb_code}_fofc.ebi.ccp4"
        self.download()
        st = gemmi.read_structure(self.path_cif)
        self.resolution = st.resolution

    def download(self):
        if not os.path.exists(self.path_data):
            os.makedirs(self.path_data)
        if not os.path.exists(self.path_cif):
            urllib.request.urlretrieve(self.url_cif, self.path_cif)
        if not os.path.exists(self.path_raw_sf):
            urllib.request.urlretrieve(self.url_raw_sf, self.path_raw_sf)
        if not os.path.exists(self.path_fofc2_ccp4):
            urllib.request.urlretrieve(self.url_fofc2_ccp4, self.path_fofc2_ccp4)
        if not os.path.exists(self.path_fofc_ccp4):
            urllib.request.urlretrieve(self.url_fofc_ccp4, self.path_fofc_ccp4)




