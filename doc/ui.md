# UI analýza

## 1. Účel dokumentu

V tomto dokumente popisujeme návrh používateľského rozhrania pre projekt Simulátor križovatky so semaformi. Cieľom je určiť:

- aké obrazovky a sekcie aplikácia obsahuje,
- aké prvky sa budú zobrazovať,
- aký bude workflow používateľa,
- aké dáta budú jednotlivé prvky zobrazovať.

UI má byť jednoduché, prehľadné a vhodné pre desktop aj mobil.

---

## 2. Hlavné princípy návrhu

- rozhranie má byť čo najprehľadnejšie,
- používateľ musí vedieť rýchlo vytvoriť konfiguráciu a spustiť simuláciu,
- chyba validácie musí byť jasne viditeľná,
- stav simulácie musí byť čitateľný aj počas pohybu áut,
- dôležité čísla a štatistiky majú byť dostupné bez potreby rolovania.

---

## 3. Navrhované hlavné sekcie stránky

1. Editor konfigurácie
2. Zoznam konfigurácií
3. Panel spustenia simulácie
4. Vizualizácia križovatky
5. Priebežné a finálne štatistiky
6. História simulácií

---

## 4. Sekcia 1 – Editor konfigurácie

### Účel

Používateľ tu nastavuje časovanie jednotlivých semaforov.

### Prvky

- textové pole: názov konfigurácie,
- textové pole: popis konfigurácie,
- číselné pole: dĺžka cyklu,
- **vizuálna časová os** – farebné bloky zelenej fázy pre každý semafor,
  presúvateľné a rozťahovateľné pomocou drag & drop (knižnica Interact.js),
- tabuľka 12 semaforov ako záloha (polia `start` a `duration`) pre mobil
  alebo ak drag & drop nie je dostupný,
- tlačidlo **Validovať**,
- tlačidlo **Uložiť konfiguráciu**.

### Zobrazenie validácie

- validácia prebieha **automaticky pri každej zmene** hodnoty,
- konflikty: červené zvýraznenie,
- warningy: oranžové upozornenie,
- úspešná validácia: zelené potvrdenie,
- tlačidlo **Uložiť konfiguráciu** je deaktivované, ak existujú neodstránené konflikty.

---

## 5. Sekcia 2 – Zoznam konfigurácií

### Účel

Zobraziť všetky uložené konfigurácie.

### Možné zobrazenie

- tabuľka,
- alebo karty.

### Stĺpce / údaje

- názov,
- popis,
- dĺžka cyklu,
- počet fáz,
- počet spustení,
- typ: preset / používateľská.

### Akcie

- Spustiť simuláciu
- Upraviť
- Zmazať
- Duplikovať

### Filter

- všetky,
- moje konfigurácie,
- prednastavené.

---

## 6. Sekcia 3 – Panel spustenia simulácie

### Účel

Používateľ nastaví parametre premávky pred spustením simulácie.

### Prvky

- vybraná konfigurácia,
- intenzita dopravy:
  - north,
  - south,
  - east,
  - west,
- rýchlosť vozidiel,
- trvanie simulácie,
- tlačidlo **Spustiť simuláciu**.

### Validácia

- intenzita nesmie byť záporná,
- rýchlosť musí byť v rozumnom rozsahu,
- trvanie musí byť kladné.

---

## 7. Sekcia 4 – Vizualizácia križovatky

### Účel

Zobraziť priebeh simulácie v reálnom čase.

### Odporúčaná technológia

- HTML Canvas,
- alternatívne SVG.

### Čo sa má zobrazovať

- križovatka zhora,
- 4 príjazdové smery,
- 3 pruhy na každom smere,
- 12 semaforov,
- autá ako jednoduché obdĺžniky alebo ikony,
- smer pohybu áut.

### Vizualizačné pravidlá

- zelený semafor = zelená šípka,
- červený semafor = červená šípka,
- čakajúce auto stojí pred stop čiarou,
- auto pri prejazde mení pozíciu podľa stavu simulácie.

### Doplnkové prvky

- progress bar cyklu,
- aktuálny čas simulácie,
- aktuálny čas v cykle.

### Ovládacie prvky

- tlačidlo **Stop** – zastaví bežiacu simuláciu a zobrazí finálne štatistiky,
- tlačidlo **Reset** – vymaže aktuálnu vizualizáciu a vráti UI do stavu pred spustením simulácie.

---

## 8. Sekcia 5 – Štatistiky

### Priebežné štatistiky

- čas simulácie,
- počet vygenerovaných áut,
- počet prejdených áut,
- počet čakajúcich áut,
- priemerná čakacia doba,
- dĺžka radu pre každý smer.

### Finálne štatistiky

- celkový počet áut,
- priemerná čakacia doba,
- maximálna čakacia doba,
- priemerná dĺžka radu,
- maximálna dĺžka radu,
- využitie križovatky.

### Grafy

- **dĺžky radov v čase** – jeden graf pre každý zo 4 smerov,
- **čakacie doby** – priemerná čakacia doba v čase,
- **využitie križovatky** – percentuálne vyjadrenie v čase.

### Zobrazenie

- čísla v kartách (priebežne aktualizované),
- grafy aktualizované v reálnom čase počas simulácie.

---

## 9. Sekcia 6 – História simulácií

### Účel

Používateľ si vie pozrieť minulé spustenia.

### Prvky

- zoznam behov,
- filter podľa konfigurácie,
- stavy: running, completed, stopped,
- pre každý beh:
  - konfigurácia,
  - čas spustenia,
  - dĺžka,
  - finálne výsledky.

### Prínos

Umožní porovnať, ktorá konfigurácia je efektívnejšia.

---

## 10. Odporúčaný layout stránky

### Desktop

Odporúčanie:

- ľavý panel: konfigurácie a formuláre,
- pravý panel: vizualizácia a štatistiky.

### Mobile

Odporúčanie:

- sekcie pod sebou,
- vizualizácia nad štatistikami,
- konfigurácie v accordion alebo tabuoch.

---

## 11. Používateľský workflow

## 11.1 Vytvorenie konfigurácie

1. Používateľ otvorí editor.
2. Nastaví dĺžku cyklu a časovanie každého semaforu
3. Editor zobrazuje konflikty v reálnom čase
4. Používateľ zadá názov a klikne "Uložiť"
5. Konfigurácia sa zobrazí v zozname.

## 11.2 Spustenie simulácie

1. Používateľ vyberie konfiguráciu zo zoznamu
2. Nastaví intenzitu premávky a trvanie
3. Klikne "Spustiť simuláciu"
4. Zobrazí sa vizualizácia s real-time aktualizáciami.

## 11.3 Ukončenie simulácie

1. Simulácia skončí automaticky alebo ju používateľ zastaví kliknutím na **Stop**.
2. Frontend zobrazí finálne štatistiky.
3. Výsledok sa uloží do histórie simulácií.
4. Používateľ môže kliknúť **Reset** – UI sa vráti do počiatočného stavu a je pripravené na nové spustenie.

---

## 12. UI stavy

- **Prázdny stav** – zoznam konfigurácií zobrazí správu „Zatiaľ neexistujú žiadne konfigurácie" s výzvou na vytvorenie prvej.
- **Loading** – spinner pri načítaní konfigurácií a pri spúšťaní simulácie.
- **Chyba** – API chyba v červenom boxe, nevalidná konfigurácia zvýraznená pri konkrétnych poliach.
- **Úspech** – potvrdenie po uložení konfigurácie a po spustení simulácie.

---

## 13. UX odporúčania

- používať jasné názvy tlačidiel,
- pri konfliktoch rovno uviesť dvojicu problémových semaforov,
- po kliknutí na konfiguráciu automaticky predvyplniť panel simulácie,
- zamedziť spusteniu simulácie bez vybratej konfigurácie,
- zobraziť posledné použité parametre.

---

## 14. Technické odporúčania

- vizualizácia cez **HTML Canvas** pre plynulú animáciu,
- drag & drop editor cez knižnicu **Interact.js**,
- debounce pri volaní validácie,
- rozdelenie UI do menších komponentov.

---

## 15. Záver

UI má podporovať tri hlavné činnosti:

1. nastaviť a uložiť konfiguráciu,
2. spustiť simuláciu,
3. sledovať a vyhodnotiť výsledok.
