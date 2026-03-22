# Installation

## User as a package
```
pip install git+https://github.com/rae-gh/map-plane.git
```

## Dev

conda env is called phd and created with python 3,14
```
conda activate phd
pip install -e ".[dev]"   # installs test packages and jupyter extensions
pip install -e ".[test]"  # installs package plus pytest
pip install -e "."        # installs package only
```