from app.models import SignalTiming

# ------------------------------------------------------------
#        | N_S| N_L| N_R|S_S|S_L |S_R |E_S| E_L| E_R| W_S|W_L|W_R
# -------|----|----|--- |---|----|----|---|----|----|----|---|----
# N_S    |  - | ✔️ | ✔️ | ✔️ | ❌ | ✔️ | ❌ | ❌ | ✔️ | ❌ | ❌ | ✔️
# N_L    | ✔️ |  - | ✔️ | ❌ | ❌ | ✔️ | ❌ | ❌ | ✔️ | ❌ | ❌ | ✔️
# N_R    | ✔️ | ✔️ |  - | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️
# S_S    | ✔️ | ❌ | ✔️ |  - | ✔️ | ✔️ | ❌ | ❌ | ✔️ | ❌ | ❌ | ✔️
# S_L    | ❌ | ❌ | ✔️ | ✔️ |  - | ✔️ | ❌ | ❌ | ✔️ | ❌ | ❌ | ✔️
# S_R    | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ |  - | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️
# E_S    | ❌ | ❌ | ✔️ | ❌ | ❌ | ✔️ |  - | ✔️ | ✔️ | ✔️ | ❌ | ✔️
# E_L    | ❌ | ❌ | ✔️ | ❌ | ❌ | ✔️ | ✔️ |  - | ✔️ | ❌ | ❌ | ✔️
# E_R    | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ |  - | ✔️ | ✔️ | ✔️
# W_S    | ❌ | ❌ | ✔️ | ❌ | ❌ | ✔️ | ✔️ | ❌ | ✔️ |  - | ✔️ | ✔️
# W_L    | ❌ | ❌ | ✔️ | ❌ | ❌ | ✔️ | ❌ | ❌ | ✔️ | ✔️ |  - | ✔️
# W_R    | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ |  -

CONFLICT_PAIRS = [
   
    # rovno vs kolmé rovno
    ("N_S", "E_S"),
    ("N_S", "W_S"),
    ("S_S", "E_S"),
    ("S_S", "W_S"),

    # left vs protiidúce rovno
    ("N_L", "S_S"),
    ("S_L", "N_S"),
    ("E_L", "W_S"),
    ("W_L", "E_S"),

    # left vs kolmé rovno
    ("N_L", "E_S"),
    ("N_L", "W_S"),
    ("S_L", "E_S"),
    ("S_L", "W_S"),
    ("E_L", "N_S"),
    ("E_L", "S_S"),
    ("W_L", "N_S"),
    ("W_L", "S_S"),

    # left vs left (všetky relevantné kombinácie)
    ("N_L", "S_L"),
    ("N_L", "E_L"),
    ("N_L", "W_L"),
    ("S_L", "E_L"),
    ("S_L", "W_L"),
    ("E_L", "W_L"),
]


def _overlaps(a: SignalTiming, b: SignalTiming, cycle: int) -> tuple[int, int] | None:
    if a.duration == 0 or b.duration == 0:
        return None

    def segs(s, d):
        e = s + d
        return [(s, cycle), (0, e % cycle)] if e > cycle else [(s, e)]

    for as_, ae in segs(a.start, a.duration):
        for bs, be in segs(b.start, b.duration):
            if (ol := (max(as_, bs), min(ae, be)))[0] < ol[1]:
                return ol
    return None


def find_conflicts(timings: dict[str, SignalTiming], cycle: int) -> list[dict]:
    result = []
    for a, b in CONFLICT_PAIRS:
        if a not in timings or b not in timings:
            continue
        if ol := _overlaps(timings[a], timings[b], cycle):
            result.append({"signal_a": a, "signal_b": b, "overlap_start": ol[0], "overlap_end": ol[1]})
    return result