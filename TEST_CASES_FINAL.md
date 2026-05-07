## Úvod

- **Názov projektu:** Simulácia dopravnej križovatky (krizovatka)
- **Cieľ testovania:** Overiť správnosť riadenia semaforov, detekciu konfliktov a stabilitu simulácie
- **Rozsah:** Webová aplikácia – backend (Python/FastAPI), frontend, WebSocket simulácia

## Testovacia stratégia

Typy testov:

- Funkčné testy (konfigurácia semaforov, spustenie simulácie)
- Negatívne testy (neplatné vstupy, konflikty semaforov)
- Výkonnostné testy (priebeh simulácie, WebSocket odozva)
- Boundary testy (hraničné hodnoty časovania)
- Chybové stavy (výpadok spojenia, power failure)

## Testované funkcie

Kľúčové časti aplikácie:

- Správa konfigurácií semaforov (CRUD, validácia)
- Spustenie a zastavenie simulácie
- Real-time vizualizácia cez WebSocket
- Detekcia konfliktov semaforov
- Štatistiky simulácie
- História simulácií

## Test scenáre (príklady)

Konkrétne situácie:

- Overenie trvania zelenej fázy semaforu
- Zabránenie súčasnej zelenej pre konfliktné smery
- Výpadok WebSocket spojenia počas simulácie
- Zadanie neplatných hodnôt časovania

## Prehľad testov

| ID   | Názov                            | Výsledok          |
| ---- | -------------------------------- | ----------------- |
| TC-1 | Overenie trvania zelenej fázy    | ✅ PASS            |
| TC-2 | Detekcia konfliktu semaforov     | ✅ PASS            |
| TC-3 | Zadanie zápornej hodnoty         | ⚠️ ČIASTOČNÝ PASS |
| TC-4 | Krajné hodnoty trvania simulácie | ⚠️ ČIASTOČNÝ PASS |
| TC-5 | Výpadok spojenia počas simulácie | ✅ PASS            |

---

## TC-1 – Overenie trvania zelenej fázy

**Predpodmienky**

- Aplikácia je spustená a dostupná v prehliadači

**Kroky**

1. Otvoriť formulár novej konfigurácie.
2. Zadať názov konfigurácie, napr. TEST 1. Cycle duration nastaviť na 120.
3. Pri SEVER – priamo zadať: start = 0, trvanie = 50.
4. Kliknúť Uložiť.
5. Spustiť simuláciu: trvanie 200 sekúnd, intenzita premávky 20 pre všetky smery.
6. Sledovať semafor na severe – merať ako dlho svieti zelená.
7. Overiť, že po 50 sekundách sa zelená prepne na červenú.

**Očakávaný výsledok** Semafor na severe svieti zeleno presne 50 sekúnd a potom sa prepne na červenú. Cyklus sa opakuje každých 120 sekúnd.

**Výsledok testu: ✅ PASS** Manuálne overené dňa 7.5.2025. Semafor na severe (priamo) svietil zeleno 50 sekúnd a následne sa prepol na červenú. Správanie zodpovedá očakávanému výsledku.

---

## TC-2 – Detekcia konfliktu semaforov

**Predpodmienky**

- Aplikácia je spustená a dostupná v prehliadači

**Kroky**

1. Otvoriť formulár novej konfigurácie.
2. Pri SEVER – priamo zadať: start = 0, trvanie = 60.
3. Pri VÝCHOD – vľavo zadať: start = 30, trvanie = 60.
4. Kliknúť Uložiť.
5. Skontrolovať či sa konfigurácia uložila alebo aplikácia zobrazila chybu.

**Očakávaný výsledok** Aplikácia zobrazí chybovú hlášku o konflikte semaforov. Konfigurácia sa neuloží, pretože oba semafory by mali zelenú súčasne v rovnakom čase.

> **Poznámka:** Konflikt nastáva v čase 30–60 sekúnd, kedy majú obaja semafory zelenú súčasne.

**Výsledok testu: ✅ PASS** Manuálne overené dňa 7.5.2025. Aplikácia zobrazila hlášku: „Konflikt semaforov: E_L vs N_S (30–60s)" a konfiguráciu odmietla uložiť. Správanie zodpovedá očakávanému výsledku.

---

## TC-3 – Zadanie zápornej hodnoty

**Predpodmienky**

- Aplikácia je spustená a dostupná v prehliadači

**Kroky**

1. Otvoriť formulár novej konfigurácie.
2. Pri SEVER – priamo zadať: start = -10, trvanie = 40.
3. Cycle duration nastaviť na 120.
4. Kliknúť Uložiť.
5. Skontrolovať či sa zobrazila chybová hláška a či sa konfigurácia uložila.

**Očakávaný výsledok** Aplikácia zobrazí chybovú hlášku, že hodnota start nemôže byť záporná. Konfigurácia sa neuloží.

**Výsledok testu: ⚠️ ČIASTOČNÝ PASS** Manuálne overené dňa 7.5.2025. Konfigurácia so zápornou hodnotou start=-10 sa neuložila – to je správne. Avšak aplikácia na obrazovke nezobrazila žiadnu chybovú správu. Používateľ teda nevidí prečo sa nič nestalo a čo má opraviť. Toto je chyba v aplikácii – chýba chybová hláška na obrazovke.

---

## TC-4 – Krajné hodnoty trvania simulácie

**Predpodmienky**

- Aplikácia je spustená a dostupná v prehliadači
- Existuje aspoň jedna uložená konfigurácia

**Kroky**

1. Otvoriť formulár novej simulácie.
2. Zadať trvanie simulácie = 0 a kliknúť Spustiť simuláciu. Poznačiť čo sa stalo.
3. Zadať trvanie simulácie = 1 a kliknúť Spustiť simuláciu. Poznačiť čo sa stalo.
4. Zadať trvanie simulácie = 3600 a kliknúť Spustiť simuláciu. Poznačiť čo sa stalo.
5. Zadať trvanie simulácie = 3601 a kliknúť Spustiť simuláciu. Poznačiť čo sa stalo.

**Očakávaný výsledok** Povolené hodnoty sú 1 až 3600 sekúnd. Pri hodnotách mimo tohto rozsahu sa simulácia nespustí a aplikácia zobrazí chybovú hlášku.

|Hodnota|Očakávané|
|---|---|
|0|Simulácia sa nespustí|
|1|Simulácia sa spustí|
|3600|Simulácia sa spustí|
|3601|Simulácia sa nespustí|

**Výsledok testu: ⚠️ ČIASTOČNÝ PASS** Manuálne overené dňa 7.5.2025. Hodnota 0 – simulácia sa nespustila. Hodnota 1 – simulácia sa spustila na 1 sekundu, semafory rýchlo preblikli. Hodnota 3600 – simulácia sa spustila normálne. Hodnota 3601 – simulácia sa nespustila. Aplikácia pri neplatných hodnotách (0 a 3601) nezobrazila žiadnu chybovú správu na obrazovke – rovnaká chyba ako v TC-3.

---

## TC-5 – Výpadok spojenia počas simulácie

**Predpodmienky**

- Aplikácia je spustená a dostupná v prehliadači
- Existuje aspoň jedna uložená konfigurácia

**Kroky**

1. Spustiť simuláciu s trvaním 120 sekúnd.
2. Počkať kým simulácia beží a semafory sa prepínajú.
3. Vypnúť internet (wifi alebo sieťové pripojenie).
4. Počkať 2–3 sekundy.
5. Znovu zapnúť internet.
6. Sledovať čo sa stalo so simuláciou – beží ďalej? Obnovila sa? Zobrazila hlášku?

**Očakávaný výsledok** Simulácia nezostane zaseknutá počas výpadku. Po obnovení internetu pokračuje ďalej, semafory sú na inej farbe ako pred výpadkom – čas plynul aj počas výpadku.

**Výsledok testu: ✅ PASS** Manuálne overené dňa 7.5.2025. Po odpojení internetu a opätovnom pripojení simulácia bežala ďalej. Semafory boli na inej farbe ako pred výpadkom, čo je správne – čas plynul aj počas výpadku spojenia. Aplikácia si s výpadkom poradila správne.