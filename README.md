# map-plane
Plane views of density maps

This is a libary to visualise planes through electron density maps.

## Citation

If you use this tool please cite:

> Rachel Alcraft (2026). Publication details forthcoming.

## Data Storage

Downloaded data (pdb and electron desntiy) is stored in ~/.map_plane/data/ by default.  
To use a custom location:  
`export MAP_PLANE_DATA=/your/preferred/path`  

## Reproducing the Paper Figures

### Figure 1 — Fourier truncation rings in 1EGJ (0.54 Å)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rae-gh/map-plane/blob/main/notebooks/Figure01_1ejg.ipynb)

Input data: fetched automatically from EBI Electron Density Server  
PDB accession: 1EGJ  
Expected output: Fourier truncation rings visible at bond electron distances

## Data

All electron density data is fetched automatically from the 
EBI Electron Density Server (https://www.ebi.ac.uk/pdbe/eds). 
No data is bundled with this repository.

Please cite the EBI if you use this tool:
> Wojdyr et al. (2022). The Protein Data Bank at 50. 
> Nucleic Acids Research.

## Dependencies

Python 3.9+
See pyproject.toml for full details

Install with:
pip install git+https://github.com/rae-gh/map-plane.git

## Licence

MIT Licence — see LICENSE file.

## Acknowledgements

Mark Williams, Birkbeck College, University of London.  
Tracey Barrett, Birkbeck College, University of London.  

---

## What This Repository Is Not

- Not production software
- Not fully documented beyond the README and notebook comments
- Not containerised
- Not continuously integrated

It is reproducible evidence of the results in the paper and thesis.
