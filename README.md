# 👁️ BORDERWORLD & The Beholder (v20.8.7-OMNISCIENCE)
An asynchronous Discord arbitration bot, Man-in-the-Middle telemetry sniffer, and zero-sum rivalry tracker for Xonotic 1v1 duels.

### ⚠️ DISCLAIMER
**THIS PROJECT HAS BEEN CREATED AND IS MAINTAINED BY A MENTALLY ILL MAN AND HIS HALLUCINATING ROBOT FRIEND. ACT ACCORDINGLY IF YOU USE THE CODE.

YOU ARE FREE TO COPY, USE AND BRANCH, BUT THE SCORE SYSTEM DESIGN IS MINE [BAINELF] AND VERY MUCH HUMAN MADE. I EXPECT TO BE CREDITED.

THIS IS MY GIFT TO THE WORLD AND I WILL KEEP WORKING ON IT, WITH GEMINI, AT MY USUAL SCHIZOPHRENIC, OBSESSIVE AND ACCELERATED RATE. 

NEVER COMPROMISE, NOT EVEN IN THE FACE OF ARMAGEDDON.**

---

### 🤖 Architecture: The Beholder
*Engineered by Gemini.* A custom Python referee designed to track matches with zero latency, bypassing fragile server logs entirely.

* **Omniscient MitM Sniffer:** Intercepts the DarkPlaces engine's outbound XonStat JSON flux across multiple discrete server instances concurrently.
* **Bloodbath Bypass (NEW):** A specialized FFA logic core for the **Insta-Bloodbath** node. It extracts kills and accuracy to generate a Discord scoreboard without polluting the 1v1 Rivalry database.
* **Matchmaking RCON:** In-game notification system that alerts players when the Discord has been notified, providing real-time routing to the community hub.
* **Absolute Truth:** Calculates weapon accuracy based strictly on mechanical actions (trigger pulls vs. physical hits), ignoring engine padding or network ghosting.
* **Spectral OpSec:** Player privacy is hardcoded. Aggressively scrubs IPv6 prefixes and hostmasks from all intercepted feeds.
* **The Overseer Heartbeat:** An autonomous Watchdog protocol linked to `overseer.sh`. If the engine flickers or a node collapses, the system resurrects itself automatically.

---

### 🩸 Mechanics: The Blood Ledger
*System Design by Drummer [BAINELF].* A zero-sum database tracking fluid, brutal rivalries. This is not a traditional point-grinding leaderboard.

* **Glissant Mechanics (Tug-of-War):** Points are stolen, not given. To gain a point, you must take it directly from your rival.
* **Unified Ranks:** The Eye is now multi-dimensional. Player legacy and points are synchronized across all nodes (Alpha, Beta, Gamma) in a single, fluid database.
* **Rolling 3 Analytics:** Dominance is calculated strictly from the outcome of the last 3 matches between a specific pair. Past victories will not protect you.
* **The Law of Entropy:** Stagnation is punished. If a rivalry remains inactive for 30 days, points slowly fade into nothing.

---

### 🚀 Phase 3: Multi-Node Expansion (LIVE)
BORDERWORLD has evolved from a single arena into a hardened, multi-node infrastructure:

* **The Quad-Core Cluster:** Deployment of parallel 125Hz strict 1v1 arenas (**Alpha, Beta, Gamma**) and the high-chaos **Insta-Bloodbath** DM node.
* **JSON Vaulting:** Credentials and port-mapping are now isolated in a local `servers.json` configuration, decoupling the bot's logic from its environment.
* **Discord RCON Integration:** Automatic delivery of Discord invite links and Matchmaking status directly into the in-game console post-match.

---

### 🛠️ Tech Stack
* **Engine:** DarkPlaces (Xonotic v0.8.6 Headless) / Locked at 125Hz (`sys_ticrate 0.008`)
* **Logic Core:** Python 3.10+
* **Async Framework:** `discord.py`, `asyncio`, `aiohttp`
* **Data Layer:** SQLite3 (Zero-latency local disk I/O)
* **Automation:** Bash, Screen, Crontab

---

### ⚙️ Deployment & OpSec
If you clone this repository, you must secure the perimeter. The Beholder uses a decoupled credential system:

1.  **Create `secret.txt`:** Contains your Discord Bot Token on Line 1.
2.  **Create `servers.json`:** Map your Arena names, Game ports, UDP telemetry ports, and RCON passwords.
3.  **Shielding:** Use the provided `.gitignore`. Do not ever commit your secret files or `beholder.db`.
