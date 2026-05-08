from __future__ import annotations
import json
from db.db_config import get_connection

_SELECT = """
    SELECT id, name, description, cycle_duration, signal_timings,
           is_preset, cycle_utilization, created_at, updated_at
    FROM configurations
"""

def _row_to_dict(row) -> dict:
    d = dict(row)
    if d.get("signal_timings"):
        d["signal_timings"] = json.loads(d["signal_timings"])
    return d

def save_configuration(record: dict) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO configurations
            (id, name, description, cycle_duration, signal_timings)
        VALUES
            (:id, :name, :description, :cycle_duration, :signal_timings)
    """, {
        "id":             record["id"],
        "name":           record["name"],
        "description":    record["description"],
        "cycle_duration": record["cycle_duration"],
        "signal_timings": json.dumps(record["signal_timings"]),
    })
    conn.commit()
    conn.close()

def update_configuration(cfg_id: str, data: dict) -> dict | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE configurations
        SET name           = :name,
            description    = :description,
            cycle_duration = :cycle_duration,
            signal_timings = :signal_timings,
            updated_at     = CURRENT_TIMESTAMP
        WHERE id = :id
    """, {
        "id":             cfg_id,
        "name":           data["name"],
        "description":    data["description"],
        "cycle_duration": data["cycle_duration"],
        "signal_timings": json.dumps(data["signal_timings"]),
    })
    conn.commit()
    cur.execute(_SELECT + "WHERE id = :id", {"id": cfg_id})
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return _row_to_dict(row)

def delete_configuration(cfg_id: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM simulations WHERE config_id = ?", (cfg_id,))
    cur.execute("DELETE FROM configurations WHERE id = ?", (cfg_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def fetch_all() -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + "ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [_row_to_dict(row) for row in rows]

def fetch_one(cfg_id: str) -> dict | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + "WHERE id = ?", (cfg_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return _row_to_dict(row)
