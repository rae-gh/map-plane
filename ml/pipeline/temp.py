import pandas as pd

df = pd.read_csv("ml/data/peptide_bonds_data.tsv", sep="\t", dtype=str)
df["has_rings"]         = None
df["classified_by"]     = None
df["manually_verified"] = None
df["confidence"]        = None
df.to_csv("ml/data/peptide_bonds_data.tsv", sep="\t", index=False)
print(f"Cleared {len(df)} rows")