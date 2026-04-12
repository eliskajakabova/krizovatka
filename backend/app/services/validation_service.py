from app.engine.conflict_matrix import ALL_SIGNALS, CONFLICT_MATRIX


class ValidationService:
    def validate(self, cycle_duration: int, signal_timings: dict) -> dict:
        conflicts = []
        warnings = []

        missing = [
            signal for signal in ALL_SIGNALS if signal not in signal_timings]
        if missing:
            for signal in missing:
                conflicts.append({
                    "signal_a": signal,
                    "signal_b": signal,
                    "error": "missing_signal",
                })

            return {
                "valid": False,
                "conflicts_detected": conflicts,
                "warnings": warnings,
                "cycle_utilization": 0.0,
            }

        for signal, timing in signal_timings.items():
            start = timing["start"]
            duration = timing["duration"]

            if start < 0 or start >= cycle_duration:
                conflicts.append({
                    "signal_a": signal,
                    "signal_b": signal,
                    "error": "invalid_start",
                })

            if duration < 0 or duration > cycle_duration:
                conflicts.append({
                    "signal_a": signal,
                    "signal_b": signal,
                    "error": "invalid_duration",
                })

            if duration == 0:
                warnings.append(
                    f"Semafor {signal} má nulovú dĺžku zelenej fázy")

        for signal_a, conflicting_signals in CONFLICT_MATRIX.items():
            for signal_b in conflicting_signals:
                if signal_a >= signal_b:
                    continue

                if self._intervals_overlap(
                    signal_timings[signal_a],
                    signal_timings[signal_b],
                    cycle_duration,
                ):
                    conflicts.append({
                        "signal_a": signal_a,
                        "signal_b": signal_b,
                        "error": "overlap",
                    })

        valid = len(conflicts) == 0
        utilization = self._calculate_cycle_utilization(
            signal_timings, cycle_duration)

        return {
            "valid": valid,
            "conflicts_detected": conflicts,
            "warnings": warnings,
            "cycle_utilization": utilization,
        }

    def _normalize_intervals(
            self, timing: dict, cycle_duration: int) -> list[tuple[int, int]]:
        start = timing["start"]
        duration = timing["duration"]
        end = start + duration

        if duration <= 0:
            return []

        if end <= cycle_duration:
            return [(start, end)]

        overflow = end - cycle_duration
        return [(start, cycle_duration), (0, overflow)]

    def _intervals_overlap(
            self, timing_a: dict, timing_b: dict, cycle_duration: int) -> bool:
        intervals_a = self._normalize_intervals(timing_a, cycle_duration)
        intervals_b = self._normalize_intervals(timing_b, cycle_duration)

        for a_start, a_end in intervals_a:
            for b_start, b_end in intervals_b:
                if max(a_start, b_start) < min(a_end, b_end):
                    return True

        return False

    def _calculate_cycle_utilization(
            self, signal_timings: dict, cycle_duration: int) -> float:
        total = sum(t["duration"] for t in signal_timings.values())

        if cycle_duration <= 0 or not signal_timings:
            return 0.0

        return round(total / (cycle_duration * len(signal_timings)), 3)
