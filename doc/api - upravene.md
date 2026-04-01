# API analýza

## 1. Účel dokumentu

Tento dokument definuje návrh API pre projekt **Simulátor križovatky so semaformi**. Cieľom je:
- presne určiť endpointy,
- uzamknúť formát request/response JSON,
- oddeliť správu konfigurácií od správy simulácií,

---

## 2. API princípy

- REST API sa používa na správu konfigurácií a simulácií.
- WebSocket sa používa iba na priebežné streamovanie stavov simulácie.
- Frontend je klient API a nesmie obchádzať validáciu backendu.
- Všetky odpovede musia byť vo formáte JSON.
- Chybové odpovede musia byť čitateľné a konzistentné.

---

## 3. Základné URL

### REST API
```text
/api/intersection/...
```

### WebSocket
```text
/ws/{simulation_id}
```

---

## 4. Identifikátory

| Typ | Formát | Príklad |
|---|---|---|
| Configuration ID | string | `conf_abc123` |
| Simulation ID | string | `sim_xyz789` |

---

## 5. Modely dát

## 5.1 SignalTiming
```json
{
  "start": 0,
  "duration": 50
}
```

## 5.2 TrafficIntensity
```json
{
  "north": 20,
  "south": 20,
  "east": 15,
  "west": 15
}
```

## 5.3 VehicleState
```json
{ "id": "v_001",
 "from": "north",
 "state": "waiting",
 "wait_time": 12.3 }
```

---

## 6. Endpointy – konfigurácie

## 6.1 POST /api/intersection/configurations

### Účel
Vytvorí a uloží novú konfiguráciu časovania semaforov.

### Request
```json
{
  "name": "Vyvážená konfigurácia",
  "description": "Rovnaký čas pre Sever-Juh a Východ-Západ",
  "cycle_duration": 120,
  "signal_timings": {
    "N_S": {"start": 0, "duration": 50},
    "N_L": {"start": 50, "duration": 10},
    "N_R": {"start": 0, "duration": 50},
    "S_S": {"start": 0, "duration": 50},
    "S_L": {"start": 0, "duration": 0},
    "S_R": {"start": 0, "duration": 50},
    "E_S": {"start": 60, "duration": 50},
    "E_L": {"start": 110, "duration": 10},
    "E_R": {"start": 60, "duration": 50},
    "W_S": {"start": 60, "duration": 50},
    "W_L": {"start": 60, "duration": 0},
    "W_R": {"start": 60, "duration": 50}
  }
}
```

### Validácia
- `name` je povinný,
- `cycle_duration` je v rozsahu 30 až 300,
- všetky semafory musia byť prítomné,
- `start` a `duration` musia byť v rozsahu cyklu,
- konfliktné intervaly sa nesmú prekrývať.

### Success response
```json
{
  "config_id": "conf_abc123",
  "name": "Vyvážená konfigurácia",
  "description": "Rovnaký čas pre Sever-Juh a Východ-Západ",
  "cycle_duration": 120,
  "signal_timings": {
    "N_S": {"start": 0, "duration": 50}
  },
  "total_phases": 4,
  "conflicts_detected": [],
  "warnings": [
    "Semafor S_L má nulovú dĺžku zelenej fázy"
  ],
  "cycle_utilization": 0.916,
  "created_at": "2025-11-08T10:30:00Z"
}
```

### Error response
```json
{
  "error": "validation_error",
  "message": "Konfigurácia obsahuje konfliktné zelené fázy",
  "details": [
    {
      "signal_a": "N_L",
      "signal_b": "S_S",
      "overlap_start": 40,
      "overlap_end": 50
    }
  ]
}
```

---

## 6.2 GET /api/intersection/configurations

### Účel
Vráti zoznam všetkých konfigurácií.

### Query parametre
- `include_presets=true|false`

### Response
```json
{
  "configurations": [
    {
      "config_id": "conf_abc123",
      "name": "Vyvážená konfigurácia",
      "description": "Rovnaký čas pre Sever-Juh a Východ-Západ",
      "cycle_duration": 120,
      "is_preset": false,
      "times_simulated": 8,
      "created_at": "2025-11-08T10:30:00Z"
    }
  ]
}
```

---

## 6.3 GET /api/intersection/configurations/{config_id}

### Účel
Vráti detail konkrétnej konfigurácie.

### Response
```json
{
  "config_id": "conf_abc123",
  "name": "Vyvážená konfigurácia",
  "description": "Rovnaký čas pre Sever-Juh a Východ-Západ",
  "cycle_duration": 120,
  "signal_timings": {
    "N_S": {"start": 0, "duration": 50},
    "N_L": {"start": 50, "duration": 10}
  },
  "is_preset": false,
  "created_at": "2025-11-08T10:30:00Z",
  "updated_at": "2025-11-08T10:30:00Z"
}
```

---

## 6.4 PUT /api/intersection/configurations/{config_id}

### Účel
Aktualizuje existujúcu používateľskú konfiguráciu.

### Pravidlá
- preset konfigurácie sa nesmú meniť,
- validácia je rovnaká ako pri vytvorení.

### Response
```json
{
  "config_id": "conf_abc123",
  "status": "updated",
  "updated_at": "2025-11-08T11:00:00Z"
}
```

---

## 6.5 DELETE /api/intersection/configurations/{config_id}

### Účel
Zmaže používateľskú konfiguráciu.

### Response
```json
{
  "config_id": "conf_abc123",
  "status": "deleted"
}
```

---

## 6.6 POST /api/intersection/configurations/validate

### Účel
Overí konfiguráciu bez uloženia.

### Request
```json
{
  "cycle_duration": 120,
  "signal_timings": {
    "N_S": {"start": 0, "duration": 50},
    "N_L": {"start": 50, "duration": 10}
  }
}
```

### Response
```json
{
  "valid": true,
  "conflicts_detected": [],
  "warnings": [
    "Semafor W_L má nulovú dĺžku zelenej fázy"
  ],
  "cycle_utilization": 0.89
}
```

---

## 7. Endpointy – simulácie

## 7.1 POST /api/intersection/simulations/start

### Účel
Spustí simuláciu na základe existujúcej konfigurácie.

### Request
```json
{
  "config_id": "conf_abc123",
  "simulation_duration": 300,
  "traffic_intensity": {
    "north": 20,
    "south": 20,
    "east": 15,
    "west": 15
  },
  "vehicle_speed": 10
}
```

### Validácia
- `config_id` musí existovať,
- `simulation_duration > 0` a maximálne 3600,
- `traffic_intensity` v rozsahu 0 až 100,
- `vehicle_speed` v rozsahu 5 až 20.

### Response
```json
{
  "simulation_id": "sim_xyz789",
  "config_id": "conf_abc123",
  "config_name": "Vyvážená konfigurácia",
  "websocket_url": "ws://localhost:8000/ws/sim_xyz789",
  "status": "running",
  "parameters": {
    "cycle_duration": 120,
    "simulation_duration": 300,
    "traffic_intensity": {
      "north": 20,
      "south": 20,
      "east": 15,
      "west": 15
    },
    "vehicle_speed": 10
  },
  "started_at": "2025-11-08T10:35:00Z"
}
```

---

## 7.2 GET /api/intersection/simulations

### Účel
Vráti zoznam simulácií.

### Query parametre
- `status`
- `config_id`
- `limit`

### Response
```json
{
  "simulations": [
    {
      "simulation_id": "sim_xyz789",
      "config_id": "conf_abc123",
      "config_name": "Vyvážená konfigurácia",
      "status": "running",
      "started_at": "2025-11-08T10:35:00Z",
      "elapsed_time": 45.2,
      "current_statistics": {
        "total_vehicles_passed": 35,
        "average_wait_time": 12.5
      }
    }
  ]
}
```

---

## 7.3 GET /api/intersection/simulations/{simulation_id}

### Účel
Vráti detail simulácie.

### Response
```json
{
  "simulation_id": "sim_xyz789",
  "config_id": "conf_abc123",
  "status": "running",
  "simulation_duration": 300,
  "traffic_intensity": {
    "north": 20,
    "south": 20,
    "east": 15,
    "west": 15
  },
  "vehicle_speed": 10,
  "started_at": "2025-11-08T10:35:00Z"
}
```

---

## 7.4 GET /api/intersection/simulations/{simulation_id}/stats

### Účel
Vráti aktuálne alebo finálne štatistiky simulácie.

### Response
```json
{
  "simulation_id": "sim_xyz789",
  "status": "running",
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

---

## 7.5 DELETE /api/intersection/simulations/{simulation_id}

### Účel
Zastaví bežiacu simuláciu.

### Response
```json
{
  "status": "stopped",
  "simulation_id": "sim_xyz789",
  "elapsed_time": 150.5,
  "final_statistics": {
    "total_vehicles_generated": 88,
    "total_vehicles_passed": 80,
    "average_wait_time": 13.4
  }
}
```

---

## 8. Ďalšie endpointy

## 8.1 GET /api/intersection/configurations/{config_id}/history
Vráti históriu simulácií pre konkrétnu konfiguráciu.

## 8.2 GET /api/intersection/presets
Vráti zoznam prednastavených konfigurácií.

## 8.3 GET /api/info
Vráti základné informácie o serveri a verzii API.

---

## 9. Chybové kódy REST API

| HTTP kód | Význam |
|---|---|
| 200 | Úspech |
| 201 | Vytvorené |
| 400 | Chybný vstup |
| 404 | Zdroj neexistuje |
| 409 | Konflikt, napr. neplatná konfigurácia |
| 422 | Nevalidný formát dát |
| 500 | Interná chyba servera |

### Odporúčaný error formát
```json
{
  "error": "validation_error",
  "message": "Invalid cycle duration",
  "details": []
}
```

---

## 10. Záver

Tento dokument fixuje:
- endpointy,
- chybové odpovede
