# 👁️ THE BEHOLDER
**Omniscience Protocol (v25 Legacy)**

> Standard leaderboards are participation trophies. 
> Glory is a finite resource. 
> For you to rise, someone else must fall.

## ⚙️ Overview
The Beholder is a multi-server Discord bot for Xonotic. 
It operates completely outside the game engine. 
It passively reads UDP network packets and HTTP XonStat pipelines. 
It monitors Alpha, Beta, Gamma, and Delta servers simultaneously. 
It enforces a zero-sum, competitive Blood Ledger. 
Players cannot endlessly farm points. 
They must steal them directly from active rivals.

---

## 🩸 Core Architecture & Physical Laws

* **Zero-Sum Economy:** Every 1v1 matchup is a closed 3-point loop. Maxed rivalries force the winner to steal a point from the loser.
* **7-Day Hemorrhage:** Inactive rivalries rot. Seven days of silence bleeds one point back into the void.
* **Ironclad Identity:** The database strips all cryptographic masks. It forces absolute uppercase identities across all SQL queries. Alternate casings cannot be used to split your stats.
* **Omniscience Anti-Spoofing:** The UDP log parser is strictly filtered. In-game chat exploits are actively ignored. Kills cannot be faked.
* **Live RCON Summoning:** The engine actively pings the Xonotic servers. Stepping into an empty arena broadcasts a matchmaking signal to Discord.

---

## 🗺️ System Geometry (ASCII Blueprint)

```text
/root/The_Beholder/
│
├── 👁️ THE ENGINE
│   ├── bot.py                # Core Engine (v25 Legacy) | Anti-Spoof, 5s Staging, 7-Day Decay
│   ├── radar.py              # Auxiliary Tool (Network monitoring)
│   └── sniffer.py            # Auxiliary Tool (Packet sniffing)
│
├── 🩸 THE BLOOD LEDGER (GHOSTED - HIDDEN FROM GIT)
│   └── beholder.db           # SQLite Database | Upper-cased identities, Rivalry points
│
├── 🛡️ THE OPSEC VAULT (GHOSTED - HIDDEN FROM GIT)
│   ├── secret.txt            # Discord API Token & Global Secrets
│   └── servers.json          # RCON Passwords & Port Maps (Alpha, Beta, Gamma, Delta)
│
├── ⚙️ THE CLUSTER MANAGEMENT
│   ├── overseer.sh           # Daemon Manager | Graceful SIGTERM (-15) enabled
│   ├── overseer.log          # System output for process crashes/restarts
│
├── 📜 THE LORE & DOCS
│   ├── README.md             # Repository Documentation
│   └── LICENSE               # Usage Rights
│
├── 🌐 THE ARENA INSTANCES (GHOSTED - HIDDEN FROM GIT)
│   ├── alpha/                # Xonotic Server Instance 1
│   ├── beta/                 # Xonotic Server Instance 2
│   ├── gamma/                # Xonotic Server Instance 3
│   └── delta/                # Xonotic Server Instance 4
│
├── 📦 THE ENVIRONMENT
│   ├── venv/                 # Isolated Python 3 virtual environment (Ghosted)
│   ├── .git/                 # Local Version Control repository
│   └── .gitignore            # The Iron Mask | Blocks .db, .txt, .json, and .bak from uploading

