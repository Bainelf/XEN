# 👁️ BORDERWORLD & The Beholder (v20.8.5)

*An asynchronous Discord arbitration bot, Man-in-the-Middle telemetry sniffer, and zero-sum rivalry tracker for Xonotic 1v1 duels.*

> ### ⚠️ DISCLAIMER
> **THIS PROJECT HAS BEEN CREATED AND IS MAINTAINED BY A MENTALLY ILL MAN AND HIS HALLUCINATING ROBOT FRIEND. ACT ACCORDINGLY IF YOU USE THE CODE.**
> 
> **YOU ARE FREE TO COPY, USE AND BRANCH, BUT THE SCORE SYSTEM DESIGN IS MINE [BAINELF] AND VERY HUMAN. I EXPECT TO BE CREDITED.**
> 
> **THIS IS MY GIFT TO THE WORLD AND I WILL KEEP WORKING ON IT, WITH GEMINI, AT MY USUAL SCHIZOPHRENIC, OBSESSIVE AND ACCELERATED RATE.**
> 
> **NEVER COMPROMISE, NOT EVEN IN THE FACE OF ARMAGEDDON.**

---

## 🤖 Architecture: The Beholder
*Engineered by Gemini.*

A custom Python referee designed to track matches with zero latency, bypassing fragile server logs entirely.
* **MitM Telemetry Sniffer:** Intercepts the DarkPlaces engine's outbound XonStat JSON flux locally. Captures raw data before it ever leaves the host.
* **Absolute Truth:** Calculates weapon accuracy based strictly on mechanical actions (trigger pulls vs. physical hits), ignoring engine padding or network ghosting.
* **Spectral OpSec:** Player privacy is hardcoded. Aggressively scrubs IPv6 (`e0a`) prefixes and hostmasks from all intercepted feeds.
* **Bi-Directional UDP Bridge:** Injects color-coded text (`^2`) directly into live Xonotic chat to announce Nemesis shifts and database updates without heavy RCON libraries.

## 🩸 Mechanics: The Blood Ledger
*System Design by Drummer [BAINELF].*

A zero-sum database tracking fluid, brutal rivalries. This is not a traditional point-grinding leaderboard. 
* **Glissant Mechanics (Tug-of-War):** Points are stolen, not given. To gain a point, you must take it directly from your rival.
* **Rolling 3 Analytics:** Dominance is calculated strictly from the outcome of the last 3 matches between a specific pair. Past victories will not protect you.
* **The Law of Entropy:** Stagnation is punished. If a rivalry remains inactive for 30 days, the points slowly fade into nothing.

---

## 🚀 The Roadmap: Phase 3 Expansion
BORDERWORLD is currently expanding from a single arena into a multi-node infrastructure:
1. **The Network:** Deployment of 3 parallel 125Hz strict 1v1 arenas + 1 Bot-Training Ground.
2. **Omniscience:** Upgrading the `asyncio` event loop to concurrently tail and MitM-sniff multiple discrete server instances.
3. **The Web Portal:** A Flask-driven HTML interface serving the live SQLite Blood Ledger and server status directly to the public web via Nginx.

## 🛠️ Tech Stack
* **Engine:** DarkPlaces (Xonotic v0.8.6 Headless) / Locked at 125Hz (`sys_ticrate 0.008`)
* **Logic Core:** Python 3.10+
* **Async Framework:** `discord.py`, `asyncio`
* **Data Layer:** SQLite3 (Zero-latency local disk I/O)
* **Networking:** Custom UDP Sockets (RCON/MitM Proxy)

---

## ⚙️ Deployment & OpSec
If you clone this repository, you **must** create a `secret.txt` file in the root directory:
* **Line 1:** Discord Token
* **Line 2:** Server RCON Password

*Do not ever commit your `secret.txt` or `beholder.db`. Use the provided `.gitignore` to shield your environment.*
