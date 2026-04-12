CONFLICT_MATRIX: dict[str, list[str]] = {
    "N_S": ["E_S", "W_S", "S_L"],
    "N_L": ["S_S", "S_R", "E_L", "W_R"],
    "N_R": [],
    "S_S": ["E_S", "W_S", "N_L"],
    "S_L": ["N_S", "N_R", "W_L", "E_R"],
    "S_R": [],
    "E_S": ["N_S", "S_S", "W_L"],
    "E_L": ["W_S", "W_R", "S_L", "N_R"],
    "E_R": [],
    "W_S": ["N_S", "S_S", "E_L"],
    "W_L": ["E_S", "E_R", "N_L", "S_R"],
    "W_R": [],
}

ALL_SIGNALS = [
    "N_S", "N_L", "N_R",
    "S_S", "S_L", "S_R",
    "E_S", "E_L", "E_R",
    "W_S", "W_L", "W_R",
]
