import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'beholder.db'

def apply_decay(ptsA, ptsB, days_gap):
    """Applies decay for every 7 days of silence."""
    weeks_silent = days_gap // 7
    for _ in range(weeks_silent):
        total = ptsA + ptsB
        if ptsA > ptsB: # pA is leader
            ptsA = max(0, ptsA - 1)
            if total == 9: ptsB = min(9, ptsB + 1)
        elif ptsB > ptsA: # pB is leader
            ptsB = max(0, ptsB - 1)
            if total == 9: ptsA = min(9, ptsA + 1)
    return ptsA, ptsB

def rebuild():
    print("👁️ OMNISCIENCE: Recalculating Shard History with Temporal Decay...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("UPDATE rivalries SET p1_pts = 0, p2_pts = 0")
    matches = c.execute("SELECT p1, p2, winner, timestamp FROM matches ORDER BY timestamp ASC").fetchall()
    
    last_match_time = {}

    for p1, p2, winner, ts_str in matches:
        pair = tuple(sorted([p1, p2]))
        pA, pB = pair[0], pair[1]

        try:
            current_ts = datetime.fromisoformat(ts_str)
        except:
            continue

        row = c.execute("SELECT p1_pts, p2_pts FROM rivalries WHERE p1_name = ? AND p2_name = ?", (pA, pB)).fetchone()
        if not row:
            c.execute("INSERT INTO rivalries (p1_name, p2_name, p1_pts, p2_pts) VALUES (?, ?, 0, 0)", (pA, pB))
            ptsA, ptsB = 0, 0
        else:
            ptsA, ptsB = row

        if pair in last_match_time:
            gap = (current_ts - last_match_time[pair]).days
            if gap >= 7:
                ptsA, ptsB = apply_decay(ptsA, ptsB, gap)
        
        last_match_time[pair] = current_ts

        if winner == pA:
            if ptsA + ptsB < 9:
                ptsA += 1
            elif ptsB > 0:
                ptsB -= 1
                ptsA += 1
        else: # winner == pB
            if ptsA + ptsB < 9:
                ptsB += 1
            elif ptsA > 0:
                ptsA -= 1
                ptsB += 1
        
        c.execute("UPDATE rivalries SET p1_pts = ?, p2_pts = ? WHERE p1_name = ? AND p2_name = ?", (ptsA, ptsB, pA, pB))

    conn.commit()
    conn.close()
    print(f"✅ OMNISCIENCE SYNC COMPLETE. Processed {len(matches)} matches.")

if __name__ == "__main__":
    rebuild()
