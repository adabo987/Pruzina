# Analýza práce: Simulácia pružiny s guličkou

## 1. Celkový prehľad projektu

- **Cieľ:** Vytvoriť webovú aplikáciu, ktorá simuluje pohyb pružiny s guličkou na základe zadaných vstupných údajov (hmotnosť guličky, tuhosť pružiny, počiatočná výchylka). Frontend zobrazuje animáciu pružiny, backend vykonáva fyzikálne výpočty a komunikuje s frontendom cez WebSocket, a SQLite databáza ukladá parametre simulácie a históriu pohybu.
- **Technológie:**
  - Frontend: HTML, CSS, JavaScript, p5.js (pre animáciu), WebSocket
  - Backend: Python (FastAPI pre WebSocket a API), WebSocket na komunikáciu s frontendom
  - Databáza: SQLite (relačná databáza) na ukladanie parametrov simulácie a histórie
- **Komunikácia:** Frontend a backend komunikujú cez WebSocket pre real-time aktualizácie pomocou JSONu. Backend ukladá a načítava dáta z SQLite.
  
## 2. Funkčné požiadavky

- **Frontend:**
  - Formulár na zadanie vstupných údajov: hmotnosť guličky (m), tuhosť pružiny (k), počiatočná výchylka (x0).
  - Zobrazenie pružiny ako harmoniky s guličkou na konci.
  - Animácia pružiny na základe aktuálnej polohy posielanej z backendu.
  - Možnosť spustiť simuláciu stlačením tlačidla a resetovať ju (kliknutím myšou).
- **Backend:**
  - Simulácia pohybu pružiny pomocou rovnice: `x(t) = e^(-ζ*ω*t)*(x₀*cos(ω_d*t)+((v₀+ζ*ω*x₀)/ω_d)*sin(ω_d*t))`
    - ω = (k/m)^(-1) (vlastná uhlová frekvencia),
    - ζ = 0.1 (koeficient tlmenia, pevne nastavený),
    - ω_d = ω (1-ζ^2)^(-1) (tlmená uhlová frekvencia),
    - v₀ = 0 (počiatočná rýchlosť, pevne nastavená).
  - Pri štarte simulácie obdrží vstupné údaje (hmotnosť guličky, tuhosť pružiny, počiatočná výchylka) a pošle inicializačné parametre frontendu.
  - Následne posiela iba aktuálnu polohu (x(t)) cez WebSocket.
  - Ukladanie parametrov simulácie a histórie pohybu do SQLite.
  - Možnosť resetovať simuláciu na požiadanie z frontendu.
- **Databáza:**
  - Ukladanie parametrov simulácie (hmotnosť guličky, tuhosť pružiny, počiatočná výchylka, čas začiatku).
  - Ukladanie histórie pohybu (čas a pozicia) pre neskoršiu analýzu.

## 3. Nefunkčné požiadavky

- **Výkon:** Backend musí zvládať výpočty a posielanie dát v reálnom čase (aspoň 60 aktualizácií za sekundu).
- **Škálovateľnosť:** SQLite je vhodná pre menšie aplikácie s jedným používateľom. Pre viac používateľov by bolo potrebné prejsť na inú databázu (napr. PostgreSQL).
- **Bezpečnosť:** Základná autentifikácia pre prístup k API (voliteľné, nie je implementované v základnej verzii).
- **Používateľská prívetivosť:** Intuitívne rozhranie na zadanie vstupných údajov a vizuálne atraktívna animácia.

## 4. Architektúra systému

### Frontend

- **Technológie:** HTML, CSS, JavaScript, p5.js
- **Funkcionalita:**
  - Formulár na zadanie hmotnosti guličky (m), tuhosti pružiny (k) a počiatočnej výchylky (x0).
  - Zobrazuje pružinu ako harmoniku (podľa predchádzajúceho príkladu), kde počet dielikov a rozsah dĺžky sú inicializované backendom.
  - Pripojí sa k WebSocket serveru po stlačení tlačidla "Spustiť simuláciu".
  - Spracováva správy:
    - init: Inicializácia parametrov (hmotnost_gulicky, tuhost_pruziny, pociatocna_vychylka).
    - update: Aktualizácia pozicia.
  - Po kliknutí myšou pošle požiadavku na reset simulácie.
- **Komponenty:**
  - Formulár na zadanie vstupov.
  - Plátno (p5.js) na animáciu pružiny.

### Backend (Python + FastAPI)

- **Technológie:** Python, FastAPI (pre WebSocket a API), sqlite3 (štandardná knižnica Pythonu pre SQLite)
- **Funkcionalita:**
  - Simuluje pohyb pružiny podľa rovnice uvedenej vyššie.
  - Na základe vstupných údajov (m,k,x0) vypočíta ω,ω_d a následne x(t) v reálnom čase.
  - Posiela inicializačné parametre a aktualizácie polohy frontendu cez WebSocket.
  - Ukladá vstupné parametre simulácie a históriu pohybu do SQLite.
- **Štruktúra:**
  - Simulácia:
    - Výpočet polohy x(t) v reálnom čase na základe vstupov (m, k, x0).
    - Prevod polohy na pixely pre frontend (napr. 1 m = 200 pixelov).
  - WebSocket endpoint:
    - /ws: WebSocket endpoint pre komunikáciu s frontendom.
      - Pri štarte obdrží vstupné údaje a pošle inicializačné parametre.
      - Následne posiela aktualizácie polohy každých ~16 ms.
  - Databázová vrstva:
    - Ukladá vstupné parametre a históriu polohy.

### Databáza (SQLite)

- **Štruktúra:**
  - Tabuľka simulations:

```sql
CREATE TABLE simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mass REAL NOT NULL,
    stiffness REAL NOT NULL,
    initial_displacement REAL NOT NULL,
    start_time TEXT NOT NULL
);
```

  - Tabuľka positions:

```sql
CREATE TABLE positions (
    simulation_id INTEGER,
    time REAL NOT NULL,
    position REAL NOT NULL,
    FOREIGN KEY(simulation_id) REFERENCES simulations(id)
);
```

- **Funkcionalita:**
  - Ukladanie parametrov simulácie (m, k, x0, čas začiatku) pri štarte simulácie.
  - Ukladanie histórie pohybu (čas a poloha) pre každú aktualizáciu polohy.

## 5. Komunikácia (WebSocket protokol)

- **Inicializácia:**
  - Frontend pošle:
    ```{ "type": "start", "mass": 1.0, "stiffness": 10.0, "initialDisplacement": 0.5 }```
  - Backend pošle:
    ```{ "type": "init", "zaciatok": 100, "koniec": 300, "pocet_casti": 10 }```
- **Aktualizácia:**
  - Backend posiela každých ~16 ms:
    ```{ "type": "update", "poloha": 150 }```
- **Reset:**
  - Frontend pošle pri kliknutí myšou:
    ```{ "type": "reset" }```

## 6. Záver

Táto analýza popisuje projekt simulácie pružiny s guličkou, kde používateľ zadáva hmotnosť guličky, tuhosť pružiny a počiatočnú výchylku. Frontend zabezpečuje vizuálnu animáciu, backend vykonáva fyzikálne výpočty a komunikuje v reálnom čase cez WebSocket, a SQLite ukladá vstupné parametre a históriu pohybu. SQLite je jednoduchá na implementáciu, ale menej škálovateľná pre väčšie aplikácie.