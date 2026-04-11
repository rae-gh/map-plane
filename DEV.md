# Installation

## User as a package
```
pip install git+https://github.com/rae-gh/map-plane.git
```

python -m streamlit run streamlit/app_peptide.py

## Dev

conda env is called phd and created with python 3,14
```
conda activate phd
conda install -c conda-forge dssp

# Dev - all of it
python -m pip install -e ".[test,dev,ml,analysis,app]"

pre-commit install

# ML training
python -m pip install -e ".[ml]"

# other
python -m pip install -e ".[test]"  # installs package plus pytest
python -m pip install -e "."        # installs package only


```