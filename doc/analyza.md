# Simulácia Dopravnej Križovatky – Business Analýza

| | |
| --- | --- |
| Názov dokumentu | Simulácia Dopravnej Križovatky |
| Verzia | 1.0 |

## 1. Základný popis riešenia

Projekt predstavuje webovú aplikáciu, ktorá simuluje premávku na križovatke v tvare plus (+) v reálnom čase. Na križovatke sa nachádzajú semafory riadiace jednotlivé smery jazdy a simulácia obsahuje generovanie áut, ich pohyb, čakanie na červenú a prejazd križovatkou.

Používateľ bude môcť:
- vytvárať a ukladať konfigurácie časovania semaforov,
- validovať konflikty medzi zelenými fázami,
- spúšťať simuláciu nad vybranou konfiguráciou,
- sledovať priebeh simulácie v reálnom čase,
- vyhodnocovať štatistiky simulácie,
- porovnávať výsledky pre rôzne nastavenia.

Systém bude rozdelený na:
- backend v Pythone, ktorý riadi logiku simulácie,
- frontend v JavaScripte, ktorý vizualizuje stav,
- REST API, ktoré spravuje konfigurácie a simulácie,
- WebSocket, ktorý posiela priebežné stavy zo servera klientovi.

---

## 2. Ciele projektu

### Hlavný cieľ
Vytvoriť prehľadnú a funkčnú aplikáciu, ktorá umožní simulovať správanie križovatky so semaformi a analyzovať vplyv rôznych konfigurácií na plynulosť premávky.

### Čiastkové ciele
- modelovať križovatku so 4 smermi a 12 semaformi,
- navrhnúť bezpečný stavový automat semaforov,
- oddeliť konfiguráciu semaforov od samotnej simulácie,
- vytvoriť prehľadné API so stabilným JSON formátom,
- zobraziť simuláciu v reálnom čase na frontende,
- zbierať a zobrazovať štatistiky premávky.

---

## 3. Definícia pojmov a skratiek

| Pojem / skratka | Význam |
|---|---|
| BA | Business analýza |
| Križovatka | Dopravná križovatka v tvare plus |
| Konfigurácia | Uložené nastavenie časovania semaforov |
| Simulácia | Beh dopravného modelu v čase |
| Semafor | Svetelný signál pre konkrétny pohyb |
| Fáza | Časový úsek cyklu, v ktorom je aktívna skupina zelených |
| Cyklus | Celé opakovanie časovania semaforov |
| REST API | HTTP rozhranie medzi frontendom a backendom |
| WebSocket | Spojenie pre priebežné posielanie stavov server → klient |
| Signal timing | Začiatok a dĺžka zelenej fázy pre konkrétny semafor |
| Conflict | Zakázaná kombinácia dvoch pohybov v tom istom čase |
| Queue length | Dĺžka radu čakajúcich áut |

---

## 4. Základné predpoklady

- Aplikácia bude dostupná ako webová aplikácia prostredníctvom internetového prehliadača bez nutnosti inštalácie.

- Používateľ musí mať prístup k internetu a podporovaný webový prehliadač.

- Systém rozlišuje dve úrovne používateľov:
  - Administrátor, ktorý môže vytvárať, upravovať konfigurácie a spúšťať simulácie.
  - Štandardný používateľ, ktorý môže iba spúšťať preddefinované simulácie.

- Autentifikácia a bezpečnostné mechanizmy (napr. šifrovanie alebo ochrana dát) nie sú predmetom riešenia projektu.

- Aplikácia slúži primárne na vzdelávacie účely a simuláciu správania dopravy.

- Simulácia nepracuje s reálnymi dopravnými dátami, ale s generovanými údajmi.

---

## 5. In Scope / Out of Scope

### 5.1 In Scope
Do rozsahu projektu patrí:
- model križovatky so 4 smermi,
- 12 semaforov pre jednotlivé smery a pohyby,
- validácia konfliktov medzi semaformi,
- editor konfigurácie časovania,
- CRUD operácie nad konfiguráciami,
- spúšťanie a zastavovanie simulácií,
- generovanie áut podľa intenzity premávky,
- výpočet základných dopravných štatistík,
- real-time vizualizácia stavu križovatky,
- história simulácií.

### 5.2 Out of Scope
Mimo rozsahu projektu je:
- realistická fyzika vozidiel,
- podpora chodcov a priechodov,
- viacúrovňové križovatky,
- adaptívne riadenie pomocou AI,
- synchronizácia viacerých križovatiek v meste,
- detailný 3D model prostredia,
- prihlásenie používateľov a komplexná správa účtov.

---

## 6. Biznis hodnota riešenia

Aplikácia slúži ako nástroj na analýzu dopravných scenárov, umožňuje porovnávať efektivitu rôznych konfigurácií semaforov a má potenciál využitia pri plánovaní mestskej dopravy.

---

## 7. Aktéri systému

| Aktér | Popis |
|---|---|
| Používateľ | Osoba, ktorá vytvára konfigurácie a spúšťa simulácie |
| Frontend klient | Webové rozhranie pre zadávanie údajov a vizualizáciu |
| Backend server | Riadi logiku, validáciu, simuláciu a ukladanie dát |
| Databáza | Uchováva konfigurácie a históriu simulácií |

---

## 8. Vysokoúrovňový funkčný prehľad

Systém podporuje tieto hlavné oblasti:

1. **Správa konfigurácií**
   - vytvorenie,
   - validácia,
   - úprava,
   - mazanie,
   - zoznam konfigurácií.

2. **Správa simulácií**
   - spustenie simulácie,
   - zastavenie simulácie,
   - priebežné štatistiky,
   - história simulácií.

3. **Real-time zobrazenie**
   - aktuálny stav semaforov,
   - pozície vozidiel.

---

## 9. Komponenty riešenia

### 9.1 Frontend
Frontend zabezpečuje:
- formuláre pre konfiguráciu,
- zoznam uložených konfigurácií,
- formulár pre spustenie simulácie,
- canvas alebo SVG vizualizáciu križovatky,
- zobrazovanie priebežných a finálnych štatistík.

### 9.2 Backend
Backend zabezpečuje:
- validáciu vstupov,
- validáciu konfliktov semaforov,
- správu konfigurácií,
- správu simulácií,
- simuláciu pohybu áut,
- výpočet štatistík,
- streamovanie stavov cez WebSocket.

### 9.3 Databáza
Databáza uchováva:
- uložené konfigurácie,
- metaúdaje o simuláciách,
- finálne výsledky simulácií.

---

## 10. Funkčná špecifikácia

### 10.1 Konfigurovateľné prvky
Používateľ môže meniť:

- časovanie semaforov,
- dĺžku cyklu,
- intenzitu premávky,
- trvanie simulácie,
- rýchlosť vozidiel.
---
### 10.2 Statické prvky
Tieto časti systému sú pevne dané:

- križovatka v tvare plus (+),
- štyri smery (sever, juh, východ, západ),
- tri typy pohybu (rovno, doľava, doprava),
- 12 semaforov,
- typ vozidla (osobné auto).
---
### 10.3 Zobrazenie simulácie križovatky
Aplikácia musí zobrazovať:

- križovatku zhora,
- stav semaforov (zelená/červená),
- pohyb áut,
- základné štatistiky.
---
### 10.4 Zobrazenie ovládacích prvkov
Používateľ musí mať k dispozícii:

- formulár na vytvorenie konfigurácie,
- zoznam konfigurácií,
- tlačidlo na spustenie simulácie,
- tlačidlo na zastavenie simulácie,
- nastavenie parametrov simulácie.

---

## 11. Nefunkčné požiadavky

### 11.1 Security (TLS)
- Bezpečnosť nie je hlavnou súčasťou projektu.
- Vstupy od používateľa by mali byť základne kontrolované.
- V produkcii by mala komunikácia prebiehať cez HTTPS/WSS.
---
### 11.2 Performance (rýchlosť, výkon, kapacita)
- Simulácia by mala posielať aktualizácie približne každých 100 ms.
- Aplikácia by mala fungovať plynulo pri bežnej záťaži.
- Reakcia systému na akcie používateľa by nemala byť príliš pomalá.
---
### 11.3 Paralelné využitie
- Systém by mal umožniť spustenie viacerých simulácií naraz.
- Jedna simulácia by nemala ovplyvniť inú.
---
### 11.4 Jazykové mutácie
- Aplikácia bude dostupná aspoň v jednom jazyku.
- Podpora viacerých jazykov nie je nutná.
---
### 11.5 Dizajnové obmedzenia
- Aplikácia bude webová (beží v prehliadači).
- Vizualizácia bude jednoduchá (2D, nie 3D).
- Križovatka má pevný tvar (plus).
- Používajú sa generované dáta, nie reálne.

---

## 12. Záver
Táto business analýza definuje hranice systému, očakávané správanie a základné pravidlá návrhu. Nadväzujúce dokumenty podrobnejšie špecifikujú:
- stavový automat križovatky,
- API kontrakt,
- používateľské rozhranie,
- use cases a diagramy.
