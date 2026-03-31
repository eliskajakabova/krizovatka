##  WebSocket analýza

## 1. Pripojenie
Klient sa pripája na:
```text
ws://localhost:8000/ws/{simulation_id}
```

### Charakter komunikácie
- iba server → klient,
- klient neposiela riadiace správy cez WebSocket,
- všetko riadenie ide cez REST API.

---

## 2. Typy správ

### Setup správa
Posiela sa po vytvorení spojenia.

```json
{
  "type": "setup",
  "simulation_id": "sim_xyz789",
  "config_id": "conf_abc123",
  "cycle_duration": 120,
  "signal_timings": {
    "N_S": {"start": 0, "duration": 50}
  },
  "intersection_layout": {
    "width": 20,
    "height": 20,
    "lane_width": 3
  }
}
```

### State správa
Posiela sa pravidelne počas simulácie.

```json
{
  "type": "state",
  "time": 45.3,
  "cycle_time": 45.3,
  "signals": {
    "N_S": "green",
    "N_L": "red",
    "N_R": "green"
  },
  "vehicles": [
    {
      "id": "v_001",
      "from": "north",
      "to": "south",
      "position": {"x": 0, "y": -5},
      "state": "approaching"
    }
  ],
  "queue_lengths": {
    "north": 2,
    "south": 1,
    "east": 0,
    "west": 3
  },
  "statistics": {
    "total_vehicles_generated": 45,
    "total_vehicles_passed": 35,
    "total_vehicles_waiting": 10,
    "average_wait_time": 12.3
  }
}
```

### Completed správa
Posiela sa po ukončení simulácie.

```json
{
  "type": "completed",
  "total_time": 300.0,
  "final_statistics": {
    "total_vehicles_generated": 125,
    "total_vehicles_passed": 120,
    "average_wait_time": 14.2,
    "max_wait_time": 58.3,
    "average_queue_length": 2.1,
    "max_queue_length": 7,
    "intersection_utilization": 0.75
  }
}
```

### Error správa
Odporúčaná doplnková správa pri chybe.

```json
{
  "type": "error",
  "message": "Simulation not found"
}
```
