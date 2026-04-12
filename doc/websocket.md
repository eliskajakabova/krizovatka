##  WebSocket analýza

Klient sa pripája na adresu:

ws://localhost:8000/ws/{simulation_id}

kde simulation_id predstavuje identifikátor konkrétnej spustenej simulácie.

Charakter komunikácie
komunikácia prebieha iba v smere server → klient,
klient neposiela riadiace správy cez WebSocket,
všetko riadenie simulácie prebieha cez REST API,
WebSocket sa používa iba na streamovanie priebežného stavu simulácie.

### Charakter komunikácie
- iba server → klient,
- klient neposiela riadiace správy cez WebSocket,
- všetko riadenie ide cez REST API.

---

## 2. Typy správ

### Setup správa
Posiela sa po vytvorení spojenia.

```json
{ "type": "setup",
 "simulation_id": "sim_xyz789",
 "config_id": "conf_abc123",
 "cycle_duration": 120,
 "signal_timings": { "N_S": {"start": 0,
 "duration": 50}, "N_L": {"start": 50, "duration": 10},
 "N_R": {"start": 0, "duration": 50}
  }
}
```

### State správa
Posiela sa pravidelne počas simulácie.

```json
{ "type": "state",
 "time": 45.3,
 "cycle_time": 45.3,
 "signals": { "N_S": "green", "N_L": "red", "N_R": "green", "S_S": "green", "S_L": "red", "S_R": "green" },
 "vehicles": [ { "id": "v_001", "from": "north", "state": "waiting", "wait_time": 12.3 },
 { "id": "v_002", "from": "east", "state": "crossing", "wait_time": 3.1
 }
 ],
 "queue_lengths": { "north": 2, "south": 1, "east": 0, "west": 3 },
 "statistics": {
 "total_vehicles_generated": 45,
 "total_vehicles_passed": 35,
 "total_vehicles_waiting": 10,
 "average_wait_time": 12.3,
 "max_wait_time": 31.1,
 "average_queue_length": 2.1,
 "max_queue_length": 7,
 "intersection_utilization": 0.75
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
    "total_vehicles_waiting": 5,
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
