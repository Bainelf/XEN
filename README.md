# 👁️ THE BEHOLDER [v28.11-STABLE]
## PROJECT: OMNISCIENCE PROTOCOL

┌──────────────────────────────────────────────────────────────────────────┐
│  STATUS: ACTIVE                                       LOC: BORDERWORLD   │
│  USER: DRUMMER                                        SYSTEM: XONOTIC    │
└──────────────────────────────────────────────────────────────────────────┘

[1.0] FILE SYSTEM TOPOLOGY
============================================================================
The Beholder operates within a self-contained environment. 

/root/The_Beholder/
├── bot.py ................... The Core Intelligence (Discord & Listeners)
├── beholder.db .............. The Blood Ledger (SQLite3 Database)
├── secret.txt ............... OpSec Shield (Discord API Token)
├── servers.json ............. Arena Target Map (Ports & RCON Credentials)
├── README.md ................ This Blueprint
│
├── [MANAGEMENT]
│   ├── overseer.sh .......... Process Guardian (Startup & Recovery)
│   ├── clean.sh ............. Integrity & Optimization Tool
│   └── rebuild_history.py ... Math Sync (Recalculates all Shard history)
│
└── [ARCHIVE]
    └── /root/Backups/ ....... The Holy Data Vault (Tarball Restores)


[2.0] THE LOGISTICS ENGINE (ATTRITION MATH)
============================================================================
The system utilizes a 9-Shard Attrition Pool to track human dominance.
Unlike ELO, this is a finite resource "Tug-of-War."

      [BUILD PHASE]             [STEAL PHASE]             [TRUE POINTS]
   (0-8 Shards Total)         (9 Shards Total)         (Calculated / 3)
  ───────────────────       ───────────────────       ───────────────────
  Every win adds +1         Wins take -1 from         For every 3 shards
  to the victor's           loser and add +1          held, +1 True Point
  side of the pool.         to the victor.            is awarded.

        [SLIDER VISUALIZATION]
        <  P1 [ ╟──╫──╫──┼──╫──╫──╢ ] P2  >
                (9 Total Shards)


[3.0] COMMAND HIERARCHY
============================================================================

   [PUBLIC ACCESS]
   ├── !board ........... Ranks Apex Predators by True Points.
   ├── !archive ......... Raw Lifetime W/L (Total DB extraction).
   ├── !slider .......... Visualizes the current 9-shard track.
   │    └── ALIASES: !tug, !rivalry
   ├── !profile ......... The "Blood Trail" (Detailed victim list).
   │    └── ALIASES: !shards, !stats
   └── !help ............ Manifests the UI categorized help menu.

   [ADMIN OVERSIGHT]
   └── !fuse ............ Merges match history when names change.


[4.0] SYSTEM ARCHITECTURE
============================================================================

   [INPUTS]                 [ENGINE]                 [STORAGE]
   ┌──────────┐            ┌──────────────┐         ┌──────────────┐
   │ UDP 26001│───────────▶│ PYTHON 3.12  │────────▶│ SQLITE 3.db  │
   ├──────────┤            │ (BOT LOGIC)  │         └──────────────┘
   │ HTTP 8081│───────────▶│              │                 │
   └──────────┘            └──────────────┘                 │
                                  │                         ▼
                                  └─────────────────▶ [DISCORD API]


[5.0] TEMPORAL DECAY PROTOCOL
============================================================================
If a rivalry remains dormant for > 7 Days:
- Leader loses 1 Shard.
- Opponent gains 1 Shard (if pool is full).
- The "Puck" shifts back toward the center.

----------------------------------------------------------------------------
CONCEPT: DRUMMER (BAINELF) | ARCHITECTURE: GEMINI (AI)
[OMNISCIENCE PROTOCOL INITIALIZED]
----------------------------------------------------------------------------
