# This file takes a pdb file and creates the ED synthetically for 
# both the atomic coordinates and the density maxima
import urllib.request
import gemmi

pdb_id = "1ejg"
resolution = 0.54  # match the resolution of 1ejg
sample_rate = 3      # same sample rate as your experimental maps

mid = pdb_id[1:3]

# Download structure
urllib.request.urlretrieve(
    f"https://files.rcsb.org/download/{pdb_id}.cif",
    f"{pdb_id}.cif"
)

# Download map coefficients
base = f"https://files.wwpdb.org/pub/pdb/validation_reports/{mid}/{pdb_id}"
urllib.request.urlretrieve(
    f"{base}/{pdb_id}_validation_2fo-fc_map_coef.cif.gz",
    f"{pdb_id}_2fofc_coef.cif.gz"
)
urllib.request.urlretrieve(
    f"{base}/{pdb_id}_validation_fo-fc_map_coef.cif.gz",
    f"{pdb_id}_fofc_coef.cif.gz"
)

# Load structure
st = gemmi.read_structure(f"{pdb_id}.cif")
st.setup_entities()

# Load 2fo-fc
doc_2fofc = gemmi.cif.read(f"{pdb_id}_2fofc_coef.cif.gz")
rblock_2fofc = gemmi.as_refln_blocks(doc_2fofc)[0]
print("2fofc columns:", rblock_2fofc.column_labels())
grid_2fofc = rblock_2fofc.transform_f_phi_to_map(
    'pdbx_FWT', 'pdbx_PHWT', sample_rate=sample_rate)

# Load fo-fc
doc_fofc = gemmi.cif.read(f"{pdb_id}_fofc_coef.cif.gz")
rblock_fofc = gemmi.as_refln_blocks(doc_fofc)[0]
print("fofc columns:", rblock_fofc.column_labels())
grid_fofc = rblock_fofc.transform_f_phi_to_map(
    'pdbx_DELFWT', 'pdbx_DELPHWT', sample_rate=sample_rate)

# Save 2fo-fc
ccp4_2fofc = gemmi.Ccp4Map()
ccp4_2fofc.grid = grid_2fofc
ccp4_2fofc.update_ccp4_header()
ccp4_2fofc.write_ccp4_map(f"{pdb_id}_2fofc.ccp4")

# Save fo-fc
ccp4_fofc = gemmi.Ccp4Map()
ccp4_fofc.grid = grid_fofc
ccp4_fofc.update_ccp4_header()
ccp4_fofc.write_ccp4_map(f"{pdb_id}_fofc.ccp4")
########################################################
dc = gemmi.DensityCalculatorX()
dc.d_min = resolution 
dc.rate = sample_rate 
dc.grid.setup_from(st)
dc.set_refmac_compatible_blur(st[0])
dc.put_model_density_on_grid(st[0])
grid_calc = dc.grid

# save theoretical map
ccp4_calc = gemmi.Ccp4Map()
ccp4_calc.grid = grid_calc
ccp4_calc.update_ccp4_header()
ccp4_calc.write_ccp4_map(f"{pdb_id}_calc.ccp4")

