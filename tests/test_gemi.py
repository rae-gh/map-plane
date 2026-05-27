from map_plane.gemi import density as gemi_density

data_path = "~/.map_plane/data"
pdb_id = "1ejg"
resolution = 0.54  # match the resolution of 1ejg
sample_rate = 3      # same sample rate as your experimental maps

rsbp_density = gemi_density.DensityRspb(pdb_id, data_path)
rsbp_density.download()

ebi_density = gemi_density.DensityEbi(pdb_id, data_path)
ebi_density.download()
