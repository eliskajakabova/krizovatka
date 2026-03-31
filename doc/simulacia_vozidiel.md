# Simulácia vozidiel

## 1. Účel dokumentu

Tento dokument popisuje návrh simulácie vozidiel pre projekt **Simulátor križovatky so semaformi**. Cieľom je definovať:

* spôsob generovania vozidiel,
* model vozidla,
* správanie vozidiel v čase,
* tvorbu radov (queue),
* výpočet štatistík simulácie.

Simulácia vozidiel dopĺňa stavový automat semaforov a predstavuje základ pre realistické vyhodnocovanie premávky.

---

## 2. Rozsah simulácie

Simulácia rieši:

* príchod vozidiel na križovatku,
* pohyb vozidiel smerom ku križovatke,
* čakanie na červenú,
* prejazd križovatkou,
* odchod vozidiel zo systému.

Model je **zjednodušený** a neobsahuje fyzikálne kolízie ani detailnú dynamiku pohybu.

---

## 3. Generovanie vozidiel

### 3.1 Princíp

Vozidlá sa generujú pomocou **Poisson procesu**, ktorý simuluje náhodné príchody vozidiel.

### 3.2 Vstup

* intenzita dopravy (`traffic_intensity`) v jednotkách:

  * vozidlá za minútu,
  * pre každý smer zvlášť:

    * north
    * south
    * east
    * west

### 3.3 Vlastnosti

* príchody sú náhodné, ale štatisticky stabilné,
* vyššia intenzita → viac vozidiel,
* simulácia je realistickejšia než pevné intervaly.

---

## 4. Model vozidla

Každé vozidlo je reprezentované objektom s nasledujúcimi atribútmi:

| Pole      | Typ    | Popis                  |
| --------- | ------ | ---------------------- |
| id        | string | unikátny identifikátor |
| from      | string | vstupný smer           |
| to        | string | výstupný smer          |
| position  | object | aktuálna pozícia       |
| state     | string | aktuálny stav          |
| wait_time | float  | čas čakania            |

### 4.1 Pozícia

```json id="veh_pos_example"
{
  "x": 0,
  "y": -5
}
```

Štruktúra je kompatibilná s modelom `VehicleState` v API.

---

## 5. Stavy vozidla

Vozidlo môže byť v jednom z nasledujúcich stavov:

* `approaching` – približuje sa ku križovatke,
* `waiting` – čaká na zelený signál,
* `crossing` – prechádza križovatkou,
* `leaving` – opúšťa križovatku.

### 5.1 Prechod stavov

```text id="vehicle_flow"
approaching → waiting → crossing → leaving
```

Prechod závisí od:

* stavu semaforu,
* pozície vozidla,
* voľnosti križovatky.

---

## 6. Rady vozidiel (queue)

### 6.1 Princíp

Pre každý smer existuje samostatný rad vozidiel:

* north
* south
* east
* west

### 6.2 Vlastnosti

* implementácia typu **FIFO (First-In First-Out)**,
* vozidlá čakajú v poradí príchodu,
* vozidlo môže prejsť iba ak:

  * má zelenú,
  * cesta je voľná.

---

## 7. Interakcia so semaformi

Správanie vozidiel závisí od stavového automatu semaforov:

* zelená → vozidlo môže prejsť,
* červená → vozidlo čaká.

Frontend nevykonáva rozhodovanie – všetka logika je na backende.

---

## 8. Štatistiky simulácie

Počas simulácie sa zbierajú tieto metriky:

| Metrika                  | Popis                         |
| ------------------------ | ----------------------------- |
| total_vehicles_generated | počet vygenerovaných vozidiel |
| total_vehicles_passed    | počet prejdených vozidiel     |
| total_vehicles_waiting   | aktuálny počet čakajúcich     |
| average_wait_time        | priemerný čas čakania         |
| max_wait_time            | maximálny čas čakania         |
| queue_length             | dĺžka radu                    |
| intersection_utilization | využitie križovatky           |

### 8.1 Použitie

Tieto štatistiky sa:

* zobrazujú vo UI,
* posielajú cez WebSocket,
* ukladajú do databázy (simulations).

---

## 9. Prepojenie na ostatné časti systému

Simulácia vozidiel je úzko prepojená s:

* **stavovým automatom** – riadi, kedy vozidlá môžu prejsť,
* **API** – definuje štruktúru `VehicleState`,
* **UI** – vizualizuje vozidlá a ich pohyb,
* **dátovým modelom** – ukladá výsledné štatistiky.

---

## 10. Záver

Simulácia vozidiel dopĺňa systém o dynamické správanie premávky. Umožňuje:

* realistické vyhodnocovanie konfigurácií,
* generovanie štatistík,
* vizualizáciu premávky v reálnom čase.

Model je zámerne zjednodušený, aby bol implementovateľný v rámci projektu, no zároveň dostatočný na demonštráciu fungovania dopravného systému.
