import os
import urllib.request
import gemmi


class Density:
    def load_density(path):
        ed = gemmi.read_ccp4_map(path)
        return ed
    
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

    def create_ccp4_from_sf(self, sf_path, ccp4_path, resolution):
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

class DensityLocal:
    def __init__(self, pdb_code, ed_path, pdb_path, sf_path, data_path):
        self.pdb_code = pdb_code
        self.resolution = None
        self.path_data = data_path
        self.path_ed = ed_path
        self.path_pdb = pdb_path
        self.path_sf = sf_path


