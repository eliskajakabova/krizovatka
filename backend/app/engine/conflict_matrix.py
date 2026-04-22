CONFLICT_MATRIX: dict[str, list[str]] = {
    "N_S": ["W_L", "W_S", "E_S", "S_L"],
    "N_L": ["E_S", "S_S", "E_L", "W_L"],
    "N_R": [],
    "S_S": ["E_S", "W_S", "N_L", "E_L"],
    "S_L": ["W_S", "N_S", "W_L", "E_L"],
    "S_R": [],
    "E_S": ["N_S", "S_S", "W_L", "N_L"],
    "E_L": ["S_S", "S_L", "W_S", "N_L"],
    "E_R": [],
    "W_S": ["N_S", "S_S", "E_L", "S_L"],
    "W_L": ["E_S", "N_L", "N_S", "S_S"],
    "W_R": [],
}

ALL_SIGNALS = [
    "N_S", "N_L", "N_R",
    "S_S", "S_L", "S_R",
    "E_S", "E_L", "E_R",
    "W_S", "W_L", "W_R",
]
