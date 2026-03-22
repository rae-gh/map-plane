# Publication Scripts

These scripts reproduce the systematic analysis in Alcraft (2026).

Run in order:

## results01_pdb_query.py
Queries the PDB REST API for all X-ray structures at resolution < 0.8 Å 
with available EDS maps. Records query date. Outputs: `data/pdb_query_results.csv`

## results02_catalog_generation.py
Generates heatmap for residue 5 chain A for all structures returned by results01.
Outputs: `data/catalog/` — one PNG and one JSON per structure.

## results03_summary_table.py
Generates summary table from catalog metadata.
Outputs: `data/summary_table.csv`