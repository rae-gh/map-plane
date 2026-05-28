from map_plane.gemi import density as gd
from map_plane.gemi import ciffile as cf
from map_plane.dmap import mapfile as mf

data_path = "~/.map_plane/data"
pdb_code = "1ejg"
resolution = 0.54  # match the resolution of 1ejg
sample_rate = 3      # same sample rate as your experimental maps

rsbp_density = gd.DensityRspb(pdb_code, data_path)
rsbp_density.download()

ebi_density = gd.DensityEbi(pdb_code, data_path)
ebi_density.download()


rspb_cif = cf.CifFile(pdb_code, rsbp_density.path_cif)
den_path = rspb_cif.create_synthetic_ed()
syn_fc = mf.MapFile(pdb_code, den_path)

file_density = gd.Density(den_path)
reconstructed_path = file_density.make_roundtrip(resolution)


