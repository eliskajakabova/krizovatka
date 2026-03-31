# Use cases

## 1. Účel dokumentu
Tento dokument zachytáva hlavné prípady použitia systému z pohľadu používateľa.

---

## 2. Zoznam use cases
-	UC-01 Vytvoriť konfiguráciu
-	UC-02 Validovať konfiguráciu
-	UC-03 Upraviť konfiguráciu
-	UC-04 Zmazať konfiguráciu
-	UC-05 Zobraziť zoznam konfigurácií
-	UC-06 Spustiť simuláciu
-	UC-07 Sledovať priebeh simulácie
-	UC-08 Zastaviť simuláciu
-	UC-09 Zobraziť finálne štatistiky
-	UC-10 Prezerať históriu simulácií

---

### UC-01 Vytvoriť konfiguráciu
Cieľom je aby  používateľ vytvoril novú konfiguráciu semaforov.

### Primárny aktér
-	používateľ

### Predpodmienky
-	aplikácia je dostupná
-	používateľ sa nachádza v editore konfigurácie

### Postup
1. Používateľ zadá názov konfigurácie.
2. Zadá popis.
3. Nastaví dĺžku cyklu.
4. Vyplní časovanie semaforov.
5. Klikne na „Uložiť konfiguráciu“.
6. Systém vykoná validáciu.
7. Systém uloží konfiguráciu.
8. Systém zobrazí potvrdenie.

### Výstup
Nová konfigurácia je uložená v systéme.

---


### UC-02 Validovať konfiguráciu
Cieľom je aby používateľ overil, či je konfigurácia bezpečná.

### Postup
1. Používateľ vyplní alebo upraví konfiguráciu.
2. Klikne na „Validovať“ alebo sa validácia spustí automaticky.
3. Systém vyhodnotí pravidlá.
4. Systém zobrazí konflikty alebo warningy.

### Výstup
Používateľ vie, či je konfigurácia vhodná na uloženie.

---


### UC-03 Upraviť konfiguráciu
Cieľom je aby používateľ zmenil existujúcu konfiguráciu.

### Predpodmienka
-	konfigurácia nie je preset

### Postup
1. Používateľ vyberie konfiguráciu.
2. Klikne na „Upraviť“.
3. Systém načíta jej údaje do editora.
4. Používateľ vykoná zmeny.
5. Uloží konfiguráciu.
6. Systém vykoná validáciu a uloží zmeny.

---


### UC-04 Zmazať konfiguráciu
Cieľom je aby používateľ odstránil konfiguráciu.

### Predpodmienka
-	konfigurácia nie je preset

### Postup
1. Používateľ klikne na „Zmazať“.
2. Systém zobrazí potvrdenie.
3. Používateľ potvrdí akciu.
4. Systém konfiguráciu odstráni zo zoznamu.

---


### UC-05 Zobraziť zoznam konfigurácií
Cieľom je aby si používateľ prezrel dostupné konfigurácie.

### Postup
1. Používateľ otvorí aplikáciu.
2. Frontend načíta zoznam konfigurácií.
3. Systém zobrazí používateľské aj prednastavené konfigurácie.
4. Používateľ môže filtrovať zoznam.

---


### UC-06 Spustiť simuláciu
 Cieľom je aby používateľ spustil simuláciu nad vybranou konfiguráciou.

### Predpodmienky
-	existuje platná konfigurácia
-	používateľ zadal parametre premávky

### Postup
1. Používateľ vyberie konfiguráciu.
2. Zadá intenzitu dopravy pre jednotlivé smery.
3. Zadá rýchlosť a trvanie simulácie.
4. Klikne na „Spustiť simuláciu“.
5. Frontend odošle REST požiadavku.
6. Backend založí simuláciu.
7. Backend vráti simulation_id  a websocket_url.
8. Frontend otvorí WebSocket spojenie.
9. Simulácia sa zobrazí na obrazovke.

---


### UC-07 Sledovať priebeh simulácie
Cieľom je aby používateľ sledoval stav križovatky v reálnom čase.

### Postup
1. Frontend prijíma setup správu.
2. Frontend vykreslí križovatku.
3. Frontend prijíma priebežné state správy.
4. Aktualizuje semafory, autá a štatistiky.
5. Používateľ sleduje výsledky.

---


### UC-08 Zastaviť simuláciu
Cieľom je aby používateľ manuálne zastavil simuláciu.

### Postup
1. Používateľ klikne na „Stop“.
2. Frontend zavolá endpoint pre zastavenie simulácie.
3. Backend zastaví simuláciu.
4. Frontend zobrazí finálne štatistiky.

---


### UC-09 Zobraziť finálne štatistiky
Cieľom je aby používateľ po skončení simulácie videl výsledné metriky.

### Postup
1. Simulácia sa dokončí.
2. Backend pošle správu „completed“.
3. Frontend zobrazí finálne štatistiky.
4. Výsledok sa uloží do histórie.

---


### UC-10 Prezerať históriu simulácií
Cieľom je aby si používateľ mohol prezrieť minulé simulácie.

### Postup
1. Používateľ otvorí sekciu histórie.
2. Frontend načíta minulé simulácie.
3. Používateľ filtruje podľa konfigurácie.
4. Systém zobrazí výsledky behov.

---


## 3. Priorita 

| Use case | Priorita |
|---|---|
| UC-01 Vytvoriť konfiguráciu | vysoká |
| UC-02 Validovať konfiguráciu | vysoká |
| UC-05 Zobraziť zoznam konfigurácií | vysoká |
| UC-06 Spustiť simuláciu | vysoká |
| UC-07 Sledovať priebeh simulácie | vysoká |
| UC-08 Zastaviť simuláciu | stredná |
| UC-09 Zobraziť finálne štatistiky | vysoká |
| UC-10 Prezerať históriu simulácií | stredná |
| UC-03 Upraviť konfiguráciu | stredná |
| UC-04 Zmazať konfiguráciu | stredná |
