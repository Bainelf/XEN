import sqlite3
from datetime import datetime

DB_PATH = 'beholder.db'

def is_human(name):
    if not name: return False
    n = name.lower()
    bot_tags = ["[guard]", "[blood-bot]", "bot", "none", "unknown", "void"]
    for tag in bot_tags:
        if tag in n: return False
    return len(n.strip()) > 0

def rebuild():
    print("👁️ OMNISCIENCE: Rebuilding Ledger (Stateless Mode)...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Clear existing rivalries
    c.execute("DELETE FROM rivalries")
    
    # 2. Fetch all matches (No timestamp in this schema)
    matches = c.execute("SELECT winner, loser FROM matches ORDER BY match_id ASC").fetchall()
    
    rivalry_state = {}
    now_ts = datetime.now().isoformat()

    for winner, loser in matches:
        if not is_human(winner) or not is_human(loser):
            continue

        # Bot's pair_key logic
        pair_list = sorted([winner.strip(), loser.strip()], key=str.lower)
        pair_key = "_".join([n.lower() for n in pair_list])
        p1_name, p2_name = pair_list[0], pair_list[1]
        
        if pair_key not in rivalry_state:
            rivalry_state[pair_key] = {'p1': p1_name, 'p2': p2_name, 'pt1': 0, 'pt2': 0}

        data = rivalry_state[pair_key]
        is_p1_win = (winner.strip().lower() == p1_name.lower())
        
        # Build-to-9 / Steal Phase
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

    # 3. Commit back to DB
    for pk, d in rivalry_state.items():
        c.execute("""INSERT INTO rivalries (pair_key, p1_name, p2_name, p1_pts, p2_pts, last_update) 
                     VALUES (?, ?, ?, ?, ?, ?)""", 
                  (pk, d['p1'], d['p2'], d['pt1'], d['pt2'], now_ts))

    conn.commit()
    conn.close()
    print(f"✅ REBUILD COMPLETE: {len(matches)} matches processed.")

if __name__ == "__main__":
    rebuild()
