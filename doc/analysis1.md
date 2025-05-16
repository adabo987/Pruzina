# Analýza práce: Simulácia pružiny s guličkou

## 1. Celkový prehľad projektu

- **Cieľ:** Vytvoriť webovú aplikáciu, ktorá simuluje pohyb pružiny s guličkou na základe zadaných vstupných údajov (hmotnosť guličky, tuhosť pružiny, počiatočná výchylka). Frontend zobrazuje animáciu pružiny, backend vykonáva fyzikálne výpočty a komunikuje s frontendom cez WebSocket.
- **Technológie:**
  - Frontend: HTML, CSS, JavaScript, p5.js (pre animáciu), WebSocket
  - Backend: Python (FastAPI pre WebSocket a API), WebSocket na komunikáciu s frontendom
- **Komunikácia:** Frontend a backend komunikujú cez WebSocket pre real-time aktualizácie pomocou JSONu.

## 2. Funkčné požiadavky

- **Frontend:**
  - Formulár na zadanie vstupných údajov: Hmotnosť guličky (m), Pružinová tuhosť (k), Počiatočná výchylka (x0) a Tlmenie (z).
  - Pri štarte simulácie obdrží vstupné údaje (hmotnosť guličky, pružinová tuhosť, počiatočná výchylka) a pošle inicializačné parametre frontendu.
  - Zobrazenie pružiny ako harmoniky s guličkou na konci.
  - Animácia pružiny na základe aktuálnej polohy posielanej z backendu.
  - Možnosť spustiť simuláciu stlačením tlačidla.
- **Backend:**
  - Základná diferenciálna rovnica pre tlmený harmonický oscilátor:
![základná rovnica oscilátora](Pracovná plocha/Zakladna_rovnica.png)
$$m\ddot{x} + c\dot{x} + kx = 0$$
    - tuhosť - m
    - koeficient tlmenia - c
    - tuhost pruziny - k
  - Po vyriešení možeme výchylku v závislosti od času popisať rovnicou: 
$$x(t) = e^{-\zeta \omega t} \left( x_0 \cos(\omega_d t) + \frac{v_0 + \zeta \omega x_0}{\omega_d} \sin(\omega_d t) \right)$$
![konečná rovnica oscilátora](Pracovná plocha/Finalna_rovnica.png)
    - ω = (k/m)^(-1) (vlastná uhlová frekvencia),
    - ζ = 0.1 (koeficient tlmenia, pevne nastavený),
    - ω_d = ω (1-ζ^2)^(-1) (tlmená uhlová frekvencia),
    - v₀ = 0 (počiatočná rýchlosť, pevne nastavená).
  - Následne posiela iba aktuálnu polohu (x(t)) cez WebSocket.
  - Možnosť resetovať simuláciu na požiadanie z frontendu.

## 3. Nefunkčné požiadavky

- **Výkon:** Backend musí zvládať výpočty a posielanie dát v reálnom čase (aspoň 60 aktualizácií za sekundu).
- **Bezpečnosť:** Základná autentifikácia pre prístup k API (voliteľné, nie je implementované v základnej verzii).
- **Používateľská prívetivosť:** Intuitívne rozhranie na zadanie vstupných údajov a vizuálne atraktívna animácia.

## 4. Architektúra systému

### Frontend

- **Technológie:** HTML, CSS, JavaScript
- **Funkcionalita:**
  - Formulár na zadanie: Hmotnosť guličky (m), Pružinová tuhosť (k), Počiatočná výchylka (x0) a Tlmenie (z).
- **Komponenty:**
  - Formulár na zadanie vstupov.
  
### Simulator

- **Technológie:** p5.js
- **Funkcionalita:**
  - Zobrazuje pružinu ako harmoniku (podľa predchádzajúceho príkladu).
  - Pripojí sa k WebSocket serveru po stlačení tlačidla "Spustiť simuláciu".
  - Spracováva správy:
    - init: Inicializácia parametrov (mass, spring_constant, initial_displacement,damping).
    - update: Aktualizácia pozicia.
  - Po kliknutí myšou pošle požiadavku na reset simulácie.
- **Komponenty:**
  - Plátno (p5.js) na animáciu pružiny. 

### Backend (Python + FastAPI)

- **Technológie:** Python, FastAPI (pre WebSocket a API)
- **Funkcionalita:**
  - Simuluje pohyb pružiny podľa rovnice uvedenej vyššie.
  - Na základe vstupných údajov (m,k,x0,z) vypočíta ω,ω_d a následne x(t) v reálnom čase.
  - Posiela inicializačné parametre a aktualizácie polohy frontendu cez WebSocket.
- **Štruktúra:**
  - Simulácia:
    - Výpočet polohy x(t) v reálnom čase na základe vstupov (Hmotnosť guličky, Pružinová tuhosť, Počiatočná výchylka a Tlmenie).
    - Prevod polohy na pixely pre frontend (napr. 1 m = 200 pixelov).
  - WebSocket endpoint:
    - /ws: WebSocket endpoint pre komunikáciu s frontendom.
      - Pri štarte obdrží vstupné údaje a pošle inicializačné parametre.
      - Následne posiela aktualizácie polohy každú sekundu.

## 5. Komunikácia

- **Inicializácia:**
  - Frontend pošle pomocou Rest API pre Backend JSON :
    ```{ "type": "start", "mass": 1.0, "spring_constant": 10.0, "initial_displacement": 0.5, "damping": 0.0 }```
  - Backend pošle Simulatoru na vytvorenie canvas:
    ```{ "type": "init", "begin": 100, "finish": 300 }```
- **Aktualizácia:**
  - Backend posiela každú sekundu JSON pre Simulator:
    ```{ "type": "update", "position": 150 }```

## 6. Záver

Táto analýza popisuje projekt simulácie pružiny s guličkou, kde používateľ zadáva hmotnosť guličky, tuhosť pružiny a počiatočnú výchylku. Frontend zabezpečuje vizuálnu animáciu, backend vykonáva fyzikálne výpočty a komunikuje v reálnom čase cez WebSocket.