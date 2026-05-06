# Krizovatka


## Project Structure

```
krizovatka/
├── app/
│   ├── conflict.py
│   ├── models.py
│   ├── repository.py
│   ├── simulation_engine.py
│   └── simulation_service.py
├── db/
│   └── db_config.py
├── frontend/
│   ├── index.html
│   ├── css/
│       └── style.css
│   └── js/
│       ├── canvas.js           
│       ├── websocket.js        
│       ├── api.js              
│       └── main.js  
├── init.sql    
├── docker-compose.yaml
├── Dockerfile
├── main.py
├── requirments.txt

```
---

## app/conflict.py
- `CONFLICT_PAIRS` - matica semaforov ktore sa navzajom vylucuju
- `def _overlaps(a, b, cycle)` :
    - zisti ci sa dva casove intervaly prekryvaju v ramci cyklu
    - kazdy semafor ma start a duration
---
## app/models.py
- definuje datove struktury ktore API pouziva na vstup a vystup
- rozdeleny na dve casti - Simulationa & Configuration
- Configuration
    - `SignalTiming` - semafor ma `start`(kedy sa rozsvieti) a `duration`(ako dlho svieti zelena)
    - `ConfigurationRequest` - je to co pride v tele POST/PUT requestu. 
        - `check_cycle` - validator na overenie cyklu 30 - 300s
        - `check_timings` - overi kazdy semafor ze `start` a `duration` davaju zmysel v ramci cyklu
    - `ConfigurationResponse` - je to co api vrati po GET/POST/PUT
        - obsahuje polia z db (id, is_preset, cycle_utilization, ...)
- Simulation
    - `TrafficIntensity` - drzi intenzitu premavky pre kazdy smer s validaciou hodnot <0, 100>
    - `SimulationRequest` - vstup pre spustenie simulacie `config_id` - trvanie (1 - 3600s) a intenzita vozidiel (5-20m/s)
    - `SimulationResponse` - odpoved na spustenie - obsahuje `simulation_id`, WebSocket URL, ocakavanu priepustnost a cas startu
    - `SimulationListItem` - jeden riadok v zozname simulacii navrhnuty tak aby pokryl obsa stavi 
        - pre `running` - simulacia ma `elapsed_time` a `current_statistics`
        - pre `completed` simulacia ma `completed_at` a `final_statistics`
    - `SimulationStopResponse` - odpoved na DELETE - vrati finalne statistiky a casy behu
    - `FinalStatistics` a `CurrentStatistics`
---

## app/repository.py
- databazaova vrstva pre konfiguracie - kazda funkcia probu presne jednu SQL operaciu
- `_SELECT` - spolocny SELECT string ktory sa pouziva vo viacerych funkciach
- `_row_to_dict(cur, row)` - pomocna funkcia, ktora prevedie jeden riadok z DB na dict (slovnik) - JSON
    - `cur_description` - obsahuje metadat stlpcov(nazvy), `row` - obsahuje hodnot, `zip` - ich spojit do parov, `dict`- z nich spravi JSON
- `def save_configuration(record)` - INSERT zaznamu do db
- `delete_configuration(cfg_id)` - DELETE zaznamu z db, na vstupe je cfg_id, `cur.rowcount` - hovori kolko riadkov bolo zmazanych - ak 0 `cfg_id` neexistuje v db
- `fetch_all()` - SELECT vsetkych konfiguracii z db, vrati zoznam riadkov - JSON
- `fetch_one(cfg_id)` - SELECT konkretneho zaznamu z db podla `cfg_id`, ak neexistuje `cfg_if` vrati `None`
---

## app/simulation_engine.py
- fyzikalny engine simulacie - bezi kazdych 100ms - pocita kde su auta, ake su semafory a co sa deje na krizovatke
- krizovatka je modelovana v metroch so stredom v bode `(0, 0)`.
- kazdy smer ma tri pevne body:
 
| Bod | Popis |
|-----|-------|
| `_SPAWN` | kde auto vznikne — 15 m od stredu |
| `_EXIT` | kde auto zmizne po prejazde (opačná strana) |
| `_CROSS` | stred krizovatky — vsetky `(0, 0)`, auto mieri vždy do stredu |
- `class Vehicle`
    - reprezentacia auta
    - kazde auto ma `id`, `from_dir` - odkial; `to_dir` - kam; poziciu `x`, `y` a stavy: 
 
Každé auto má `id`, odkiaľ ide (`from_dir`), kam ide (`to_dir`), pozíciu `x, y` a stav:
 
| Stav | Popis |
|------|-------|
| `approaching` | ide smerom k semaforu |
| `waiting` | stoji pred cervenou |
| `crossing` | prechadza krizovatkou |
| `exited` | vyslo z krizovatky — coskoro zmazane |
 
- `IntersectionEngine.step()`
    - hlavna metoda
    - volana kazdych 100ms a robia sa nasledovne kroky
        - posunie cas
        - vypocita stav semaforov
        - spawne nove auta
        - pohne existujuce auta
    - potom sa zastavi a vrati `state` - ktory ide cez WebSocket na frontend
- `_compute_signals(cycle_time)`
    - pre kazdy semafor zisti ci je zelena alebo cervena
    - ide dokola - for loop
    - riesi case kedy interval presahuje koniec cyclu - napr. `start=110`, `duration=20` semafor svieti od 110 do 120 a potom od 0 10
- `_spawn_vehicles()` - pouziva akumulator namiesto nahodnosti
    - napr 20 aut/minuta
```
kazdy tick (0.1 s): akumulator += 20 / 60 * 0.1 ≈ 0.033
```
- ked akumulator dosiahne `1.0` - spawne sa auto a akumulator sa znizi o `1`
    - zarucuje spravnu spravnu priemernu frekvenciu bez skokov
    - cielovy smer `to_dir` je nahodny zo zostavajucich troch smerov
- `_move_vehicles(signals)` - kazde auto sa pohne o `speed * 0.1` metrov za tick smerom k svojmu cielu

---
### Logika stavov
 
**`approaching`**
- pohybuje sa k `(0, 0)`
- ked je blizsie ako **1,5 m**, skontroluje semafor:
  - zelena → prepne na `crossing`
  - cervena → prepne na `waiting`
**`waiting`**
- stoji, kazdy tick zvysuje `wait`
- pri zelenej prepne na `crossing`
**`crossing`**
- pohybuje sa k `_EXIT[to_dir]`
- ked dorazi, prepne na `exited` a zaznamena cakaciu dobu
---
- `final_stats()` - vypocita suhrne statistiky po skonceni simulacie
 

| Metrika | Popis |
|---------|-------|
| Priemerne cakanie | Priemerny `wait` cez vsetky auta |
| Maximalne cakanie | Najdlhsi jednotlivy `wait` |
| Priemerna dlzka fronty | Priemer cez vsetky ticky |
| Maximalna dlzka fronty | Najdlhsia zaznamenana fronta |
| `intersection_utilization` | Priemer zelenych frakcii vsetkych styroch smerov — kolko percent cyklu bola krizovatka aktivne vyuzivana | 
---
## app/simulation_service.py
- zivpotny cyklus simulacii
- tri fazy
    - ulozenie do db
    - beh ako asyncio task na pozadi
    - zapis vysledkov po skonceni
- WebSocket
    - `ws_connect`(sim_id, ws)
        - zaregistruje klienta a streamuje framy az kym simulacia bezi
        - prijme spojenie `ws.accept()`
        - posle `setup` spravu s konfiguraciou a layoultom krizovatky
        - drzi spojenie zive - framy su streamovane z `_broadcast()` - prichadzajuce spravy ignoruje
        - ` po odpojeni sa klient odstrani zo setu
    - `broadcast(sim_id, payload)` - posle JSON payload vsetkym pripojenym klientom danej simulacie - mrtve spojenia sa odstrania
    - `start_simulation(config, req)` - verejne API - vytvori novu simulaciu 
        - vygeneruje unique `sim_id` + UUID
        - vypocita priepustnost (`expected_throughput`) - intenzita x zelena frakcia
        - ulozi pociatocny stav do `_running` a do db
        - vyvori `IntersecrtionEngine` a spusti asyncio task `_run()`
        - vrarati metadata vratane `websockeet_url`
    - `get_simulation(sim_id)` - vrati stav simulacie z db - hlada v `_running` ak nenajde tak v db
    - `list_simulations(status, config_id, limit)` - vrati zoznam simulacii z DB s filtrom
    - `stop_simulations(sim_id)` - zastavi beziacu simulaciu
        - zrysu asyncio task `task_cancel()`
        - nastavi stav na `stopped`
        - zapisa statistiky do db
        -  odstrani simulaciu z `_running`
    - `get_stats(sim_id)` - vrati aktualne statistiky simulacie
    - `_run(sim_id, engine, duration)` - hlavny loop simulacie - bezi kazdych 100ms
        - po skonceni posle vsetkym clientom `completed` + finanle statistiky
        - vycisti `_running` aj `_ws_clients`
    - `_green_frac(direction, timings, cycle)` - vypocita zeleny stav pre dany smer - `duration`/`cycle`
    - `_sync_stats(state, final)` - prepisuje live statistiky v `state` s hodnotami z `engine.final_stats()` - vola sa po kazdom tick-u aj pri ukonceni
    - `_public(state)` - odfiltruje vnutorne kluce (zacinajuce na `_`) pre odoslanim na FE alebo do API response
    - `_save_to_db` - INSERT pri starte simulacie
    - `_update_int_db` - UPDATE po skonceni alebo zastavenie - zapise status, cas, statistiky
    - `_fet_one` - SELECT podla `id` - JOIN na `configuration`
    - `_fetch_many` - SELECT zo zoznamu s filtrom 

--- 
## db/db_config.py
 - pripojenie na databazu
 - db - postgresql
 - pouzivaju sa hodnoty z `.env`

---
## docker-compose.yaml 
- !!! musi byt nainstalovany docker a docker-compose
- databaza spusta lokalne 
- postgresql databaza
- stiahne sa image postgresql 
- na pripojenie sa pouzivaju hodnoty z .env
- dolezite prikazy
- !!!! - databaza bezi lokalne na `localhost:5432/<DB_NAME>`
    - cez PostgreSql - extension vo vscode si na nu viete dat `connect` a spustat SQL prikazy

```bash
# SPUSTENIE DATABAZY 
docker compose up 
// stopnutie cez ctrl+c

# SPUSTENIE DATABAZY NA POZADI
docker compose up -d

# ZASTAVENIE
docker compose down
```
---
## main.py
- zadefinovane vsetky endpointy, ktore volaju jednotlive funkcie z `app/`

---
## Dockerfile 
- sluzi na spustenie celej aplikacie v jednom kontajneri 
- docker si natiahne python image
- nainstaluje potrebne python kniznice z requirments.txt.
- spusti fastapi (uvicorn...)
- po spusteni - otvorit prehliadact `localhost:8000/docs#/`

---
## init.sql- automaticky vytvori databazove tabulky a vlozi prednastavene konfiguracie pri prvom spusteni kontajnera

## SPUSTENIE 
-v `krizovatka/` spustit `docker compose up --build `

