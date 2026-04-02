from rcsbapi.search import AttributeQuery
from rcsbapi.search import search_attributes as attrs
import json
from datetime import date

from map_plane import MPDATA_DIR
from map_plane.vxyz import vectorthree as v3
import map_plane.dmap.mapsmanager as mman
import map_plane.dmap.mapfunctions as mfun
import map_plane.dmap.mapplothelp as mph


# Query: X-ray structures with resolution better than 0.8Å
query = (
    attrs.rcsb_entry_info.resolution_combined <= 0.8
) & (
    attrs.rcsb_entry_info.experimental_method == "X-ray"
)

results = list(query())

# Save results
with open("data/query_results/pdb_query_results.tsv", "w") as f:
    f.write("pdb_code\tresolution\n")

mman.MapsManager().set_dir(MPDATA_DIR)
print("Data directory set to: ", MPDATA_DIR)
structures_with_maps = 0

for pdb_code in results:
    pdb_code = pdb_code.lower()
    print("------", pdb_code, "------")
    try:
        ml = mman.MapsManager().get_or_create(pdb_code,file=1,header=1,values=1)
        if ml is None:
            print(f"Failed to load map for {pdb_code}, skipping.")
            continue
        if ml.valid:
            structures_with_maps += 1
            resolution = ""
            if pdb_code in ml.map_info:
                for val in ml.map_info[pdb_code]:
                    if "author_provided" in val:
                        if "resolution_high" in val["author_provided"]:
                            resolution = val["author_provided"]["resolution_high"]
                            print(f"  Resolution: {resolution}")
            with open("data/query_results/pdb_query_results.tsv", "a") as f:
                f.write(f"{pdb_code}\t{resolution}\n")
    except Exception as e:
        print(f"Error processing {pdb_code}: {e}")
# Save provenance
metadata = {
    "query_date": str(date.today()),
    "resolution_cutoff_angstrom": 0.8,
    "experimental_method": "X-ray",
    "n_structures": len(results),
    "n_structures_with_maps": structures_with_maps,
    "package": "rcsbapi"
}

with open("data/query_results/query_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print(f"Found {len(results)} structures")