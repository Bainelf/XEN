import sqlite3
import re
from datetime import datetime, timedelta

DB_PATH = 'beholder.db'

def is_human(name):
    if not name: return False
    n = name.lower()
    bot_tags = ["[guard]", "[blood-bot]", "bot", "none", "unknown", "void"]
    for tag in bot_tags:
        if tag in n: return False
    return len(n.strip()) > 0

def apply_bot_decay(p1_pts, p2_pts, last_update, current_match_time):
    """Mirrors the bot's temporal_decay logic exactly."""
    # Convert string to datetime if needed
    if isinstance(last_update, str):
        last_update = datetime.fromisoformat(last_update)
    
    # The bot checks in 7-day increments
    while (current_match_time - last_update).days >= 7:
        total = p1_pts + p2_pts
        if p1_pts > p2_pts:
            p1_pts -= 1
            if total >= 9: p2_pts += 1
        elif p2_pts > p1_pts:
            p2_pts -= 1
            if total >= 9: p1_pts += 1
        else:
            # Bot Logic: "Tied, no decay" - breaks the chain for this interval
            break
        
        # Advance the virtual clock by 7 days
        last_update += timedelta(days=7)
        
    return p1_pts, p2_pts

def rebuild():
    print("👁️ OMNISCIENCE: Rebuilding Ledger to Bot v28.11 Specifications...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Wipe existing rivalries to ensure a clean recalculation
    c.execute("DELETE FROM rivalries")
    
    # 2. Fetch all matches (assuming they were already filtered for humans by bot.py)
    # We order by match_id or timestamp to ensure chronological order
    matches = c.execute("SELECT winner, loser, timestamp FROM matches ORDER BY match_id ASC").fetchall()
    
    # Tracking current state in memory for speed
    # state[(pair_key)] = {p1_name, p2_name, p1_pts, p2_pts, last_update}
    rivalry_state = {}

    for winner, loser, ts_str in matches:
        if not is_human(winner) or not is_human(loser):
            continue

        # Bot's pair_key logic
        pair_list = sorted([winner.strip(), loser.strip()], key=str.lower)
        pair_key = "_".join([n.lower() for n in pair_list])
        p1_name, p2_name = pair_list[0], pair_list[1]
        
        current_ts = datetime.fromisoformat(ts_str)

        # Initialize if new
        if pair_key not in rivalry_state:
            rivalry_state[pair_key] = {
                'p1': p1_name, 'p2': p2_name, 
                'pt1': 0, 'pt2': 0, 
                'last': current_ts
            }

        data = rivalry_state[pair_key]

        # --- STEP 1: DECAY (Mirroring Bot's 7-day threshold) ---
        data['pt1'], data['pt2'] = apply_bot_decay(
            data['pt1'], data['pt2'], data['last'], current_ts
        )

        # --- STEP 2: WIN LOGIC (Mirroring process_rivalry) ---
        is_p1_win = (winner.strip().lower() == p1_name.lower())
        
        if is_p1_win:
            if data['pt1'] + data['pt2'] < 9:
                data['pt1'] += 1
            elif data['pt2'] > 0:
                data['pt2'] -= 1
                data['pt1'] += 1
        else:
            if data['pt1'] + data['pt2'] < 9:
                data['pt2'] += 1
            elif data['pt1'] > 0:
                data['pt1'] -= 1
                data['pt2'] += 1
        
        # Update last_update to the match time
        data['last'] = current_ts

    # 3. Write back to DB
    for pk, d in rivalry_state.items():
        c.execute("""INSERT INTO rivalries (pair_key, p1_name, p2_name, p1_pts, p2_pts, last_update) 
                     VALUES (?, ?, ?, ?, ?, ?)""", 
                  (pk, d['p1'], d['p2'], d['pt1'], d['pt2'], d['last'].isoformat()))

    conn.commit()
    conn.close()
    print(f"✅ REBUILD COMPLETE: {len(matches)} matches processed.")

if __name__ == "__main__":
    rebuild()
