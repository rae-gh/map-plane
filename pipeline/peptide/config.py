# Config for the peptide bond pipeline
GEOM_LENGTHS = [
    "N:N+1",
    "C:N+1",
    "C:O",
    "N:O",
    "O-1:N",
    "CA:CA+1",
    "CA-1:CA",
    "O:N+1",
]

GEOM_ANGLES = [
    "N:CA:C",
    "CA:C:N+1",
    "C-1:N:CA",
    "N:CA:O",
    "CA-1:CA:CA+1",
    "N-1:O-1:N",
    "CA:C:O",
    "O:C:N+1",
]

GEOM_DIHEDRALS = [
    "N:CA:C:N+1",
    "C-1:N:CA:C",
    "N:CA:C:O",
    "CA-1:C-1:N:CA",
    "CA:C:N+1:CA+1",
]

GEOM_PARAMS = GEOM_LENGTHS + GEOM_ANGLES + GEOM_DIHEDRALS

ADD_PARAMS = [
    "dssp",
    "motif_CA-1:CA:CA+1",
    "bf_N:CA:C",
    "bf_C:O",
]

DSSP_MAP = {
    "H": "α-helix",
    "B": "isolated β-bridge",
    "E": "extended strand",
    "G": "310-helix",
    "I": "π-helix",
    "P": "poly-proline II helix",
    "T": "hydrogen-bonded turn",
    "S": "bend"
}
