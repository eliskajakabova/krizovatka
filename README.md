# Krizovatka

Krizovatka je aplikácia na simuláciu riadenia svetelných signalizácií na cestnej križovatke.
Backend beží vo FastAPI, frontend je statická webová stránka a dáta sa ukladajú do SQLite databázy.

## Projektová štruktúra

```
krizovatka/
├── app/
│   ├── conflict.py
│   ├── models.py
│   ├── repository.py
│   ├── simulation_engine.py
│   ├── simulation_service.py
│   └── __init__.py
├── db/
│   └── db_config.py
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── api.js
│       ├── canvas.js
│       ├── main.js
│       └── websocket.js
├── main.py
├── README.md
└── requirements.txt
```

## Hlavné komponenty

- `main.py`
  - spúšťa FastAPI aplikáciu
  - definuje REST API pre konfigurácie a simulácie
  - obsluhuje WebSocket pre živé aktualizácie simulácie
  - mountuje frontend z `frontend/`

- `app/conflict.py`
  - detekuje konflikty medzi signalizačnými intervalmi
  - zabezpečuje, že nakombinované zelené intervaly sa neprekrývajú

- `app/models.py`
  - definuje modely pre konfigurácie a simulácie
  - overuje vstupné dáta pre cykly, signalizácie a intenzitu premávky

- `app/repository.py`
  - spravuje SQLite databázu
  - CRUD operácie pre konfigurácie
  - prevádza databázové riadky na JSON slovníky

- `app/simulation_engine.py`
  - modeluje pohyb áut v križovatke
  - vypočítava zelené a červené stavy semaforov
  - vytvára vozidlá, posúva ich a počíta finálne štatistiky

- `app/simulation_service.py`
  - spravuje životný cyklus simulácie
  - spúšťa asynchrónny beh simulácie na pozadí
  - spracúva live WebSocket prenosy a zapisuje výsledky do DB

- `db/db_config.py`
  - inicializuje SQLite databázu v `app/database.db`
  - vytvára tabuľky `configurations` a `simulations`
  - vkladá prednastavené konfigurácie pri štarte

- `frontend/index.html`
  - hlavná webová stránka frontend aplikácie
  - načítava skripty a vykresľuje rozhranie pre simuláciu križovatky

- `frontend/css/style.css`
  - obsahuje štýly používateľského rozhrania
  - definuje rozloženie, farebnú schému a vizuálne prvky pre panel simulácie

- `frontend/js/api.js`
  - komunikuje s REST API backendu
  - načítava konfigurácie, spúšťa simulácie a zobrazuje výsledky

- `frontend/js/canvas.js`
  - vykresľuje križovatku a pohyb vozidiel v canvas elemente
  - aktualizuje grafiku na základe prijatých dát zo simulácie

- `frontend/js/main.js`
  - riadi front-end logiku aplikácie
  - spravuje používateľské vstupy, štart simulácie a obnovovanie stavu

- `frontend/js/websocket.js`
  - spravuje WebSocket spojenie so serverom
  - zobrazuje live aktualizácie simulácie v reálnom čase

## Inštalácia a spustenie

1. Nainštalujte závislosti:

```bash
python -m pip install -r requirements.txt
```

2. Spustite aplikáciu:

```bash
uvicorn main:app --reload
```

3. Otvorte v prehliadači:

- Frontend: `http://127.0.0.1:8000`
- Dokumentácia: `http://127.0.0.1:8000/docs`

## Použitie

1. Otvorte hlavnú stránku aplikácie na `http://127.0.0.1:8000`.
2. V rozhraní vyberte existujúcu konfiguráciu alebo si vytvorte novú. Nová konfigurácia sa automaticky overí, či nespôsobí konflikt medzi signálmi.
3. Zadajte trvanie simulácie a intenzitu premávky z jednotlivých smerov.
4. Spustite simuláciu tlačidlom `Spustiť simuláciu`.
5. Sledujte live vizualizáciu na plátne, ktorá zobrazuje vozidlá a priebeh križovatky.
6. Počas behu simulácie sledujte aktuálne štatistiky a stav.