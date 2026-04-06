from rcsbapi.search import AttributeQuery
from rcsbapi.search import search_attributes as attrs
import json
from datetime import date

import urllib

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
    f.write("pdb_code\tresolution\tsoftware\trefinement\tr_work\tr_free\tstereo_target\tis_multipole\n")

mman.MapsManager().set_dir(MPDATA_DIR)
print("Data directory set to: ", MPDATA_DIR)
structures_with_maps = 0
count = 0
for pdb_code in results:
    count +=1
    pdb_code = pdb_code.lower()
    print(f"{count}/{len(results)}------{pdb_code}------")
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
            # now get structure info from rest api
            url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_code.lower()}"
            refine, software = None, None
            r_work, r_free, refine_method, is_multipole, stereo_target = None, None, None, None, None
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                if "software" in data:
                    software = data["software"]
                if "refine" in data:
                    refine = data["refine"]

                #for s in software:
                #    print(s)
                refinement_software = [s.get('name', 'unknown') for s in software if isinstance(s, dict) and s.get('classification') == 'refinement']
                refinement_software = ", ".join(refinement_software[:1]) if refinement_software else "unknown"

                for r in refine:
                    for key, value in r.items():
                        print(f"{key}: {value}")
                        if key == "pdbx_method_to_determine_struct":
                            refine_method = value
                        elif key == "pdbx_stereochemistry_target_values":
                            stereo_target = value
                            if "engh" in stereo_target.lower() and "huber" in stereo_target.lower():
                                stereo_target = "Engh&Huber"
                        elif key == "ls_rfactor_rwork":
                            r_work = value
                        elif key == "ls_rfactor_rfree":
                            r_free = value

            #MOLLY — Hansen-Coppens, the original
            #MOPRO — Nancy group, Jelsch's software
            #CRYSTALS — Oxford, has multipole capability
            #JANA2006 / JANA2008 / JANA2020 — Prague group
            #INVARIOM — invariom database approach
            #XD / XD2006 / XD2016 — most widely used multipole program
            #VALRAY — older, less common`
            MULTIPOLE_PROGRAMS = ['MOLLY','MOPRO','CRYSTALS','JANA','INVARIOM','XD','VALRAY']
            #if any of the above are in the string refinement_software
            is_multipole = any(m in refinement_software.upper() for m in MULTIPOLE_PROGRAMS)


            with open("data/query_results/pdb_query_results.tsv", "a") as f:
                f.write(f"{pdb_code}\t{resolution}\t{refinement_software}\t{refine_method}\t{r_work}\t{r_free}\t{stereo_target}\t{is_multipole}\n")
                f.flush()
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