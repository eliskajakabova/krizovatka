import json
from db.db_config import get_connection

_SELECT = """
    SELECT id, name, description, cycle_duration, signal_timings,
           is_preset, cycle_utilization, created_at, updated_at
    FROM configurations
"""

def _row_to_dict(cur, row) -> dict:
    return dict(zip([d[0] for d in cur.description], row))


def save_configuration(record: dict) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO configurations
                    (id, name, description, cycle_duration, signal_timings)
                VALUES
                    (%(id)s, %(name)s, %(description)s, %(cycle_duration)s, %(signal_timings)s)
            """, {
                "id":             record["id"],
                "name":           record["name"],
                "description":    record["description"],
                "cycle_duration": record["cycle_duration"],
                "signal_timings": json.dumps(record["signal_timings"]),
            })
        conn.commit()


def update_configuration(cfg_id: str, data: dict) -> dict | None:
    """Update name/description/cycle_duration/signal_timings. Returns updated row or None if not found."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE configurations
                SET name           = %(name)s,
                    description    = %(description)s,
                    cycle_duration = %(cycle_duration)s,
                    signal_timings = %(signal_timings)s,
                    updated_at     = NOW()
                WHERE id = %(id)s
                RETURNING id, name, description, cycle_duration, signal_timings,
                          is_preset, cycle_utilization, created_at, updated_at
            """, {
                "id":             cfg_id,
                "name":           data["name"],
                "description":    data["description"],
                "cycle_duration": data["cycle_duration"],
                "signal_timings": json.dumps(data["signal_timings"]),
            })
            row = cur.fetchone()
        conn.commit()
    if not row:
        return None
    return dict(zip([d[0] for d in cur.description], row))


def delete_configuration(cfg_id: str) -> bool:
    """Delete configuration and all its simulations. Returns True if a row was deleted."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Najprv zmaž všetky simulácie ktoré používajú túto konfiguráciu
            cur.execute(
                "DELETE FROM simulations WHERE config_id = %s",
                (cfg_id,)
            )
            # Potom zmaž konfiguráciu
            cur.execute(
                "DELETE FROM configurations WHERE id = %s",
                (cfg_id,)
            )
            deleted = cur.rowcount > 0
        conn.commit()
    return deleted


def fetch_all() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(_SELECT + "ORDER BY created_at DESC")
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]


def fetch_one(cfg_id: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(_SELECT + "WHERE id = %s", (cfg_id,))
            row = cur.fetchone()
            if not row:
                return None
            return _row_to_dict(cur, row)