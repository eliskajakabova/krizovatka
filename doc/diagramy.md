# Diagramy systému riadenia križovatky

## 1\. Component diagram

```mermaid
flowchart LR
    U\[Používateľ] --> FE\[Frontend]
    FE -->|REST API| BE\[Backend]
    FE <-->|WebSocket state stream| BE
    BE --> DB\[(Databáza)]

```



### Popis

Systém pozostáva z frontendovej a backendovej časti. Frontend komunikuje s backendom pomocou REST API pre štandardné operácie a pomocou WebSocket spojenia pre prenos dát simulácie v reálnom čase. Backend zabezpečuje logiku aplikácie a komunikáciu s databázou.



## 2\. Procesný diagram – vytvorenie konfigurácie

```mermaid
flowchart TD
    A\[Používateľ nastaví časovanie] --> B\[Frontend odošle požiadavku na validáciu konfigurácie]
    B --> C\[Backend vykoná validáciu]
    C --> D{Konflikt?}
    D -- áno --> E\[Vráti chybu a konflikty]
    D -- nie --> F\[Uloží konfiguráciu]
    F --> G\[Vráti config\_id]
    G --> H\[Frontend zobrazí uloženú konfiguráciu]

```



### Popis

Používateľ nastaví konfiguráciu križovatky. Backend overí správnosť nastavení a identifikuje prípadné konflikty medzi smermi premávky. Ak je konfigurácia validná, uloží sa do databázy.



## 3\. Procesný diagram – spustenie simulácie

```mermaid
flowchart TD
    A\[Používateľ vyberie konfiguráciu] --> B\[Zadá parametre premávky]
    B --> C\[Frontend odošle požiadavku na spustenie simulácie]
    C --> D\[Backend vytvorí simuláciu]
    D --> E\[Backend vráti simulation\_id a websocket\_url]
    E --> F\[Frontend otvorí WebSocket]
    F --> G\[Backend pošle setup]
    G --> H\[Backend pošle state správy]
    H --> I\[Frontend vykresľuje simuláciu]
    I --> J\[Completed / Stop]

```



### Popis

Po spustení simulácie backend inicializuje simuláciu a poskytne WebSocket spojenie. Frontend následne prijíma priebežné dáta o stave premávky a vizualizuje ich.



## 4\. Sekvenčný diagram – validácia konfigurácie

```mermaid
sequenceDiagram
    participant U as Používateľ
    participant FE as Frontend
    participant BE as Backend
    participant DB as Databáza

    U->>FE: Vyplní konfiguráciu
    FE->>BE: POST /configurations/validate
    BE->>BE: Overenie rozsahov a konfliktov
    BE-->>FE: valid / conflicts / warnings
    U->>FE: Klikne uložiť
    FE->>BE: POST /configurations
    BE->>DB: Uloženie konfigurácie
    DB-->>BE: OK
    BE-->>FE: config\_id

```



## 5\. Sekvenčný diagram – simulácia

```mermaid
sequenceDiagram
    participant U as Používateľ
    participant FE as Frontend
    participant BE as Backend

    U->>FE: Klikne spustiť simuláciu
    FE->>BE: POST /simulations/start
    BE-->>FE: simulation\_id, websocket\_url
    FE->>BE: WebSocket connect
    BE-->>FE: setup
    loop každých 100 ms
        BE-->>FE: state
    end
    BE-->>FE: completed
```



