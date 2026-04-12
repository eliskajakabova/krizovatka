# Simulácia vozidiel

## 1. Účel dokumentu

Tento dokument popisuje zjednodušený návrh simulácie vozidiel pre projekt **Simulátor križovatky so semaformi**. Cieľom je definovať:

* spôsob generovania vozidiel,
* základný model vozidla,
* správanie vozidiel počas simulácie,
* tvorbu radov vozidiel,
* výpočet základných štatistík.

Simulácia vozidiel v tomto projekte slúži iba ako doplnok k simulácii križovatky a semaforov. Jej účelom nie je detailne modelovať dopravu, ale umožniť vyhodnotenie plynulosti premávky.

---

## 2. Rozsah simulácie

Simulácia rieši iba základné správanie vozidiel potrebné pre fungovanie križovatky:

* náhodný príchod vozidiel zo smerov (north, south, east, west),
* zaradenie vozidiel do radu pred križovatkou,
* čakanie na zelený signál,
* prejazd križovatkou,
* odstránenie vozidla po prejdení.

Model je zámerne zjednodušený:

* neobsahuje fyzikálny pohyb,
* nerieši kolízie,
* nesleduje presnú trajektóriu vozidla.

---

## 3. Generovanie vozidiel

### 3.1 Princíp

Vozidlá sú generované náhodne backendom počas simulácie. V každom kroku môže vzniknúť nové vozidlo pre niektorý zo smerov.

### 3.2 Vstup

Generovanie vychádza z parametra `traffic_intensity`, ktorý určuje intenzitu dopravy pre jednotlivé smery:

* north
* south
* east
* west

Vyššia hodnota znamená vyššiu pravdepodobnosť vzniku vozidla.

### 3.3 Vlastnosti

* príchody sú náhodné,
* nie je potrebné modelovať presný dopravný tok,
* cieľom je sledovať, či vozidlá prejdú alebo čakajú.

---

## 4. Model vozidla

Každé vozidlo je reprezentované jednoduchým objektom:

| Pole      | Typ    | Popis                  |
| --------- | ------ | ---------------------- |
| id        | string | unikátny identifikátor |
| from      | string | vstupný smer           |
| state     | string | aktuálny stav          |
| wait_time | float  | čas čakania            |

Model neobsahuje polohu ani cieľ cesty, pretože nie sú potrebné pre účely simulácie.

---

## 5. Stavy vozidla

Vozidlo môže byť iba v jednom z dvoch stavov:

* `waiting` – vozidlo stojí v rade a čaká na zelený signál,
* `crossing` – vozidlo prechádza križovatkou.

### 5.1 Prechod stavov

```text
waiting → crossing
```

Po prejdení križovatkou sa vozidlo zo simulácie odstráni.

### 5.2 Čas prejazdu

Každé vozidlo potrebuje pevne stanovený čas na prejazd križovatkou. Počas tohto času je v stave `crossing`.

---

## 6. Rady vozidiel

### 6.1 Princíp

Pre každý smer existuje samostatný rad:

* north
* south
* east
* west

### 6.2 Vlastnosti

* rady fungujú princípom **FIFO (First-In First-Out)**,
* vozidlá čakajú v poradí príchodu,
* na prejazd je vždy vybrané prvé vozidlo v rade.

---

## 7. Vzťah k semaforom

Správanie vozidiel závisí od stavového automatu semaforov:

* červená → vozidlo ostáva v stave `waiting`,
* zelená → vozidlo môže prejsť do stavu `crossing`.

Backend rozhoduje o tom, či vozidlo prejde. Frontend iba zobrazuje výsledok simulácie.

---

## 8. Štatistiky simulácie

Počas simulácie sa sledujú tieto metriky:

| Metrika                  | Popis                         |
| ------------------------ | ----------------------------- |
| total_vehicles_generated | počet vygenerovaných vozidiel |
| total_vehicles_passed    | počet vozidiel, ktoré prešli  |
| total_vehicles_waiting   | počet čakajúcich vozidiel     |
| average_wait_time        | priemerný čas čakania         |
| max_wait_time            | maximálny čas čakania         |
| average_queue_length     | priemerná dĺžka radu          |
| max_queue_length         | maximálna dĺžka radu          |
| intersection_utilization | využitie križovatky           |

Tieto hodnoty sa používajú na porovnanie rôznych konfigurácií semaforov.

---

## 9. Prepojenie na systém

Simulácia vozidiel je prepojená s:

* **stavovým automatom** – riadi, kedy vozidlá môžu prejsť,
* **API a WebSocket** – prenášajú stav simulácie,
* **UI** – zobrazuje vozidlá,
* **dátovým modelom** – ukladá výsledné štatistiky.

Simulácia vozidiel je podriadená logike križovatky.

---

## 10. Obmedzenia modelu

Pre projekt platí:

* vozidlá nemajú presnú polohu,
* neexistuje detailná fyzika pohybu,
* neriešia sa kolízie,
* vozidlo po prejdení zaniká,
* model je optimalizovaný na jednoduchosť.

---

## 11. Záver

Simulácia vozidiel predstavuje jednoduchý model správania premávky, ktorý slúži na podporu hlavného cieľa projektu – simulácie križovatky.

Zjednodušený prístup umožňuje:

* jednoduchú implementáciu,
* prehľadné správanie systému,
* zameranie na logiku semaforov a ich efektivitu.
