# 🌍 G-Cards — Civilizations

An online real-time strategy game about civilizations through the centuries.

You start with **1 city** and **100 citizens**. Every **century lasts 5 minutes**.
At the **end of each century there is a war**. Win wars to take cities.
The player with the **most city points** (people + buildings + resources) wins!

---

## ▶️ How to start the game

1. Open a terminal in this folder.
2. Install the tools (only the first time):

   ```
   pip install -r requirements.txt
   ```

3. Start the server:

   ```
   python run.py
   ```

4. Open your browser at **http://127.0.0.1:8000**

---

## 🎮🎮🎮🎮🎮 Run 5 versions at once

Want five **separate** games at the same time? Each one is its own world with
its own save file:

```
python run_all.py
```

Or the **easiest way: double-click `start_5_games.bat`**.

It finds 5 **free** ports (it skips any port already in use) and opens five links — for example:

| Version | Link |
|---------|------|
| Game 1 | http://127.0.0.1:8001 |
| Game 2 | http://127.0.0.1:8002 |
| Game 3 | http://127.0.0.1:8003 |
| Game 4 | http://127.0.0.1:8004 |
| Game 5 | http://127.0.0.1:8005 |

- Press **Ctrl+C** to stop all five.

---

## 🌐 Play with friends on your network (Wi‑Fi)

By default the games only work on **your own computer** (`127.0.0.1`).
To let other devices join, the server must listen on the **network address**
(`0.0.0.0`):

**Easiest way:** double-click **`start_network_games.bat`**.
It prints an address like `http://192.168.1.61:8001` — send that to your friends
on the same Wi‑Fi.

**Firewall:** the first time, Windows may ask to allow Python — click **Allow**.
If you accidentally click Cancel/Block, other devices can't connect. To fix it,
open *Windows Defender Firewall → Allow an app through firewall*, find **Python**,
and tick **Private** and **Public** (this needs an administrator account).

> ℹ️ To play *one shared game* with friends, everyone uses the **same** link.
> The 5 versions are 5 **separate** games.

---

## 🧩 What each file does

| File | What it is |
|------|------------|
| `run.py` | Starts everything. |
| `run_all.py` | Starts 5 separate versions at once (finds free ports). |
| `start_5_games.bat` | Double-click this to start the 5 versions. |
| `start_network_games.bat` | Start the 5 versions on your Wi‑Fi network. |
| `start_network_game.bat` | Start one game on your Wi‑Fi network (port 8000). |
| `server/config.py` | All the game numbers (costs, times, countries…). Change numbers here! |
| `server/models.py` | The shapes of a Player and a City. |
| `server/game.py` | The brain: the clock, the economy, and the wars. |
| `server/bots.py` | Computer players. |
| `server/storage.py` | Saves the world to `data/save.json`. |
| `server/main.py` | The web addresses (API) the browser talks to. |
| `web/` | The page you see: HTML, CSS and JavaScript. |

---

## 🎮 How to play (first version)

1. Type your name and pick a country.
2. Everyone votes for a starting century (10–15 or 20–25).
3. Build houses, markets, walls and barracks with **building points**.
4. Make money and buy **iron, stone, gold, diamond**.
5. Spend **knowledge points** to unlock new things.
6. At the end of the century, choose a city to attack — the battle is automatic.
7. After 5 centuries, the biggest civilization wins.

---

## Credits

- World map background: "World map - low resolution" from Wikimedia Commons.

