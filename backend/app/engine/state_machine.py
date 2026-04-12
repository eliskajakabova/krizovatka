def is_signal_green(
        start: int, duration: int, cycle_time: float,
        cycle_duration: int) -> bool:
    if duration <= 0:
        return False

    end = start + duration

    if end <= cycle_duration:
        return start <= cycle_time < end

    overflow = end - cycle_duration
    return cycle_time >= start or cycle_time < overflow


def get_signal_states(
        signal_timings: dict, cycle_time:
        float, cycle_duration: int) -> dict[str, str]:
    result: dict[str, str] = {}

    for signal_id, timing in signal_timings.items():
        green = is_signal_green(
            timing["start"],
            timing["duration"],
            cycle_time,
            cycle_duration,
        )
        result[signal_id] = "green" if green else "red"

    return result
