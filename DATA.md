# PDB Data Sources and URLs

## Overview

For crystallographic electron density work you need two things: a **structure file** (atomic coordinates) and **electron density data**. 

The two main sources are **RCSB (US)** and **PDBe/EBI (UK)**. For all URLs below, `{pdb_id}` is the 4-character PDB code (e.g. `1ejg`) and `{mid}` is `pdb_id[1:3]` (e.g. `ej` from `1ejg`).

---

## RCSB

### Structure

| File | URL | Notes |
|------|-----|-------|
| Structure mmCIF | `https://files.rcsb.org/download/{pdb_id}.cif` | Original deposited coordinates |
| Structure PDB format | `https://files.rcsb.org/download/{pdb_id}.pdb` | Legacy format, avoid for new work |

### Raw Structure Factors

| File | URL | Notes |
|------|-----|-------|
| Raw structure factors | `https://files.rcsb.org/download/{pdb_id}-sf.cif` | Fo and σFo only, **no phases** |

Raw structure factors are the primary experimental observations. They contain observed amplitudes (Fo) and their errors (σFo) but **no phases** — phases cannot be measured directly in X-ray crystallography. You cannot make a map from this file alone without re-running crystallographic refinement.

### Map Coefficients

Computed by the wwPDB validation pipeline from the deposited structure and structure factors. Consistent with the RCSB structure file.

| File | URL | Notes |
|------|-----|-------|
| 2Fo-Fc coefficients | `https://files.wwpdb.org/pub/pdb/validation_reports/{mid}/{pdb_id}/{pdb_id}_validation_2fo-fc_map_coef.cif.gz` | Weighted amplitudes and phases, gzipped |
| Fo-Fc coefficients | `https://files.wwpdb.org/pub/pdb/validation_reports/{mid}/{pdb_id}/{pdb_id}_validation_fo-fc_map_coef.cif.gz` | Difference map coefficients, gzipped |

Column names in these files (for 1ejg in testing):

| File | Amplitude column | Phase column |
|------|-----------------|--------------|
| 2Fo-Fc | `pdbx_FWT` | `pdbx_PHWT` |
| Fo-Fc | `pdbx_DELFWT` | `pdbx_DELPHWT` |

### Validation Reports

| File | URL |
|------|-----|
| Validation XML | `https://files.wwpdb.org/pub/pdb/validation_reports/{mid}/{pdb_id}/{pdb_id}_validation.xml.gz` |
| Validation PDF | `https://files.wwpdb.org/pub/pdb/validation_reports/{mid}/{pdb_id}/{pdb_id}_full_validation.pdf.gz` |

---

## PDBe / EBI (pre-computed CCP4 maps)

### Structure

| File | URL | Notes |
|------|-----|-------|
| Updated structure mmCIF | `https://www.ebi.ac.uk/pdbe/entry-files/download/{pdb_id}_updated.cif` | PDBe-enriched with additional annotations |

The `_updated.cif` from PDBe contains the same coordinates as the RCSB file but with additional annotations (UniProt mappings, corrected residue numbering etc). For purely crystallographic work either is fine, but **do not mix** the PDBe updated structure with RCSB map coefficients as they may be inconsistent.

### Raw Structure Factors

| File | URL | Notes |
|------|-----|-------|
| Raw structure factors | `https://www.ebi.ac.uk/pdbe/entry-files/r{pdb_id}sf.ent` | Same content as RCSB `-sf.cif`, older naming convention |

### Pre-computed CCP4 Maps

| File | URL | Notes |
|------|-----|-------|
| 2Fo-Fc map | `https://www.ebi.ac.uk/pdbe/entry-files/{pdb_id}.ccp4` | Pre-computed, fixed grid spacing |
| Fo-Fc map | `https://www.ebi.ac.uk/pdbe/entry-files/{pdb_id}_diff.ccp4` | Pre-computed, fixed grid spacing |

PDBe maps can be loaded directly into gemmi without FFT. The disadvantage is that the grid spacing is fixed — you cannot control it via `sample_rate` as you can with structure factors.

---

## Derived Maps from Reciprocal Space Arithmetic

From the two map coefficient files you can derive pure Fo and Fc maps by arithmetic on the complex structure factor arrays before FFT:

```
2Fo-Fc = 2Fo - Fc
Fo-Fc  = Fo  - Fc

Therefore:
Fo = (2Fo-Fc) - (Fo-Fc)
Fc = Fo - (Fo-Fc)
```

This arithmetic should always be done in **reciprocal space** (on the complex structure factor arrays) rather than on the real-space maps, to avoid compounding numerical errors on top of the unavoidable experimental truncation artefacts.

---

