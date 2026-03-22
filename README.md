# map-plane
Plane views of density maps

# Repository Structure and README Template

## Repository Structure

```
your-tool/
├── README.md
├── requirements.txt
├── LICENSE
├── src/
│   └── # your tool code as it is now — do not modify
├── notebooks/
│   ├── figure2_1egj_rings.ipynb
│   ├── figure3_example2.ipynb
│   └── thesis_chapter2_refitting.ipynb
└── examples/
    └── quick_start.ipynb
```

---

## README Template

```markdown
# Your Tool Name

One paragraph description of what the tool does in plain English. No jargon.
This is what Google indexes and what a reviewer reads first.

## Citation

If you use this tool please cite:

> Your Name (2026). Title of Short Communication. 
> Acta Crystallographica Section A. doi:XXXXXXXX

## Quick Start

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yourusername/yourrepo/blob/main/examples/quick_start.ipynb)

One example, five lines of code maximum, showing the most important thing 
the tool does.

## Reproducing the Paper Figures

### Figure 2 — Fourier truncation rings in 1EGJ (0.54 Å)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yourusername/yourrepo/blob/main/notebooks/figure2_1egj_rings.ipynb)

Input data: fetched automatically from EBI Electron Density Server  
PDB accession: 1EGJ  
Expected output: Fourier truncation rings visible at bond electron distances

### Figure 3 — [Next example]
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yourusername/yourrepo/blob/main/notebooks/figure3_example2.ipynb)

Input data: fetched automatically from EBI Electron Density Server  
PDB accession: XXXX  
Expected output: [description]

### Figure 4 — Bump on ring artefact in 4UA6 (0.79 Å)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yourusername/yourrepo/blob/main/notebooks/figure4_4ua6.ipynb)

Input data: fetched automatically from EBI Electron Density Server  
PDB accession: 4UA6  
Expected output: [description]

## Reproducing the Thesis Examples

### Chapter 2 — Coordinate refitting experiment
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yourusername/yourrepo/blob/main/notebooks/thesis_chapter2_refitting.ipynb)

Input data: fetched automatically from EBI Electron Density Server  
Expected output: [description]

## Data

All electron density data is fetched automatically from the 
EBI Electron Density Server (https://www.ebi.ac.uk/pdbe/eds). 
No data is bundled with this repository.

Please cite the EBI if you use this tool:
> Wojdyr et al. (2022). The Protein Data Bank at 50. 
> Nucleic Acids Research.

## Dependencies

Python 3.x  
See requirements.txt for full list.

Install with:
pip install -r requirements.txt

## Licence

MIT Licence — see LICENSE file.

## Acknowledgements

Mark Williams, Birkbeck College, University of London.  
[Second supervisor name], Birkbeck College.  
[Pearl's lab reader name], Institute of Cancer Research.
```

---

## Five Point Notebook Checklist

Before marking any notebook as done, verify:

1. Can you open it in a fresh Colab session and run all cells without errors?
2. Does it fetch its own input data from a public source rather than relying on local files?
3. Does the key output figure match what is in the paper or thesis chapter?
4. Is there a cell at the top that installs all dependencies?
5. Is there a brief text cell explaining what the notebook does?

Only fix what answers no. Nothing else.

---

## Colab Badge Template

Replace `yourusername`, `yourrepo`, and `path/to/notebook.ipynb` with your details:

```markdown
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yourusername/yourrepo/blob/main/path/to/notebook.ipynb)
```

---

## Zenodo DOI Instructions

1. Go to https://zenodo.org
2. Log in with GitHub
3. Go to GitHub settings in Zenodo
4. Enable your repository
5. Create a release in GitHub
6. Zenodo automatically mints a DOI
7. Add the DOI badge to your README

```markdown
[![DOI](https://zenodo.org/badge/XXXXXXX.svg)](https://zenodo.org/badge/latestdoi/XXXXXXX)
```

---

## What This Repository Is Not

- Not a pip installable package
- Not production software
- Not fully documented beyond the README and notebook comments
- Not containerised
- Not continuously integrated

It is reproducible evidence that the results in the paper and thesis are real.
That is all it needs to be.
