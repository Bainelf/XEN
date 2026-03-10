# 👁️ THE BEHOLDER - EMERALD GAZE (v24.0-OMNISCIENCE)

<div align="center">
  <h3>⚠️ DISCLAIMER</h3>
  <p>
    THIS PROJECT HAS BEEN CREATED AND IS MAINTAINED BY A MENTALLY ILL MAN AND HIS HALLUCINATING ROBOT FRIEND.<br><br>
    ACT ACCORDINGLY IF YOU USE THE CODE.<br><br>
    YOU ARE FREE TO COPY, USE AND BRANCH, BUT THE SCORE SYSTEM DESIGN IS MINE [BAINELF] AND VERY MUCH HUMAN MADE.<br><br>
    I EXPECT TO BE CREDITED.<br><br>
    THIS IS MY GIFT TO THE WORLD AND I WILL KEEP WORKING ON IT, WITH GEMINI, AT MY USUAL SCHIZOPHRENIC, OBSESSIVE AND ACCELERATED RATE.<br><br>
    NEVER COMPROMISE, NOT EVEN IN THE FACE OF ARMAGEDDON.
  </p>
</div>

---

## ⚡ v24.0 PATCH NOTES (SCORCHED EARTH)
* **Total Architectural Isolation:** Servers now run via unique binaries (`xonotic-alpha`, `beta`, `gamma`, `delta`) to prevent process locking.
* **Filesystem Sandboxing:** Implementation of `-userdir` for each arena to ensure complete separation of logs, configs, and temporary data.
* **UDP Identity Lock:** Each server now streams its console logs to a unique local port (**27000-27006**). No more "Duel 1" identity ghosting in Discord.
* **Improved RCON Injection:** Matchmaking messages are now dual-line and formatted in **Emerald Green (^2)** for high-visibility.
* **Bloodbath Optimization:** Automatic filtering of `[BLOOD-BOT]` join/part notifications from the Discord feed. Bloodbath (Delta) utilizes dynamic map rotation.
* **Process Stability:** `overseer.sh` updated with v24 logical wipes and synchronized binary launches.

---

## 🏗️ SYSTEM ARCHITECTURE

    /home/xonotic/Xonotic/ (Root)
    ├── xonotic-alpha  ────► [Port 26000] ──► -userdir alpha/
    ├── xonotic-beta   ────► [Port 26001] ──► -userdir beta/
    ├── xonotic-gamma  ────► [Port 26002] ──► -userdir gamma/
    └── xonotic-delta  ────► [Port 26003] ──► -userdir delta/ (Bloodbath Mode)
           │
           └─► Each binary is ISOLATED via -userdir. 
               No shared memory. No shared configs. No identity leaks.
    
    /root/The_Beholder/ (Intelligence)
    ├── bot.py (The Brain)
    ├── beholder.db (The Memory)
    ├── overseer.sh (The Heart) ──► Manages the 5 Screen Sockets
    └── servers.json (The Maps) ──► Points to the RCON/UDP Ports

---

## 🛰️ DATA FLOW (OMNISCIENCE PROTOCOL)

        [ DISCORD ] <───────┐
             │              │
        [ BOT.PY ] <──┐     │ (RCON/UDP Stats)
             │        │     │
       ┌─────┴────────┼─────┼──────────┐
       │              │     │          │
    [ALPHA]        [BETA] [GAMMA]   [DELTA]
    (26000)        (26001) (26002)   (26003)
       │              │     │          │
    [PORT 27000]   [27002] [27004]   [27006] <── BOT LISTENS HERE

---

## 🔧 QUICK COMMANDS
- **Ignition / Total Wipe:** `/root/The_Beholder/overseer.sh wipe`
- **Monitor the Brain:** `screen -r beholder`
- **Audit Network Ports:** `netstat -tulpn | grep xonotic`

**The Omniscience Protocol is Online. The Borderworld is Secure.**
