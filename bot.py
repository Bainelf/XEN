# ==============================================================================
# 👁️ THE BEHOLDER - EMERALD GAZE (v28.11-STABLE)
# ==============================================================================
# Architecture: Gemini (AI) | Concept: Drummer (BAINELF)
# RESTORED: Exact, uncut original logic from v28.9. No amputations.
# FIXED: Dynamic field chunking to prevent Discord 1024-character limit crashes.
# FIXED: Markdown escaping applied to player names to prevent font corruption.
# ==============================================================================

import discord
from discord.ext import commands, tasks
from aiohttp import web
import sqlite3
import re
import socket
import asyncio
import math
import json
from datetime import datetime, timedelta

# --- OPSEC SHIELD ---
try:
    with open('/root/The_Beholder/secret.txt', 'r') as f:
        DISCORD_TOKEN = f.readline().strip()
except FileNotFoundError:
    print("❌ FATAL: 'secret.txt' missing. The Eye remains closed.")
    exit()

VERSION = "28.11-Stable"
HAS_STARTED = False

# --- DATABASE INITIALIZATION ---
def init_db():
    with sqlite3.connect('beholder.db') as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS players (xon_name TEXT PRIMARY KEY)')
        c.execute('CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS matches (match_id INTEGER PRIMARY KEY, winner TEXT, loser TEXT, pair_key TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS rivalries (pair_key TEXT PRIMARY KEY, p1_name TEXT, p2_name TEXT, p1_pts INTEGER, p2_pts INTEGER, last_update TEXT)')
        conn.commit()

init_db()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

# 🛡️ THE SHIELDS
RE_COLOR = re.compile(r'\^([0-9]|x[0-9a-fA-F]{3})')
RE_MASK_SCRUB = re.compile(r'^[\[\]\da-fA-F\.:]+:')

def clean_xon(raw_text):
    return RE_COLOR.sub('', raw_text).strip()

def is_human(name):
    if not name:
        return False
        
    n = name.lower()
    bot_tags = ["[guard]", "[blood-bot]", "bot", "none", "unknown", "void"]
    
    for tag in bot_tags:
        if tag in n:
            return False
            
    if len(n.strip()) == 0:
        return False
        
    return True

# --- GLOBAL HELPERS ---
async def global_broadcast(content=None, embed=None, mention_drilla=False):
    with sqlite3.connect('beholder.db') as conn:
        res = conn.cursor().execute("SELECT value FROM config WHERE key = 'announcement_channel'").fetchone()
    if res and (chan := bot.get_channel(int(res[0]))):
        prefix = "👁️ **@drilla:** " if mention_drilla else ""
        await chan.send(content=f"{prefix}{content}" if content else None, embed=embed)

def process_rivalry(winner, loser):
    if not is_human(winner) or not is_human(loser): 
        return f"*Automaton match logged ({winner} vs {loser}). No blood drawn.*"
    
    with sqlite3.connect('beholder.db') as conn:
        c = conn.cursor()
        winner_clean = winner.strip()
        loser_clean = loser.strip()
        
        pair_list = sorted([winner_clean, loser_clean], key=str.lower)
        pair_key = "_".join([n.lower() for n in pair_list])
        p1 = pair_list[0]
        p2 = pair_list[1]

        c.execute("INSERT OR IGNORE INTO players (xon_name) VALUES (?)", (winner_clean,))
        c.execute("INSERT OR IGNORE INTO players (xon_name) VALUES (?)", (loser_clean,))

        res = c.execute("SELECT p1_pts, p2_pts FROM rivalries WHERE pair_key = ?", (pair_key,)).fetchone()
        
        if res:
            pt1 = res[0]
            pt2 = res[1]
        else:
            pt1 = 0
            pt2 = 0

        is_p1_win = (winner_clean.lower() == p1.lower())

        if is_p1_win:
            # Build pool to 9 first, then steal
            if pt1 + pt2 < 9:
                pt1 += 1
            elif pt2 > 0:
                pt2 -= 1
                pt1 += 1
        else:
            if pt1 + pt2 < 9:
                pt2 += 1
            elif pt1 > 0:
                pt1 -= 1
                pt2 += 1

        c.execute("INSERT OR REPLACE INTO rivalries VALUES (?, ?, ?, ?, ?, ?)", (pair_key, p1, p2, pt1, pt2, datetime.now().isoformat()))
        c.execute("INSERT INTO matches (winner, loser, pair_key) VALUES (?, ?, ?)", (winner_clean, loser_clean, pair_key))
        conn.commit()

        true_w = pt1 // 3 if is_p1_win else pt2 // 3
        true_l = pt2 // 3 if is_p1_win else pt1 // 3
        w_shards = pt1 if is_p1_win else pt2
        l_shards = pt2 if is_p1_win else pt1

        return f"⚖️ **Attritional Slider:** `{w_shards}` to `{l_shards}` Shards | **True Points:** `{true_w}` to `{true_l}`"

# ==============================================================================
# ⚔️ THE ARENA BLUEPRINT
# ==============================================================================
class ArenaTracker:
    def __init__(self, name, game_port, udp_port, http_port, rcon_pass):
        self.name = name
        self.game_port = game_port
        self.udp_port = udp_port
        self.http_port = http_port
        self.rcon_pass = rcon_pass

        self.state = {
            "id_map": {}, "conn_map": {}, "frags": {}, "deaths": {}, "acc": {},
            "intermission": False, "welcomed": set(), "disconnect_tasks": {}, "current_map": "Unknown"
        }

    def rcon_say(self, msg: str):
        if not self.rcon_pass: return
        try:
            pkt = b'\xff\xff\xff\xffrcon ' + self.rcon_pass.encode() + b' say ' + msg.encode()
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(pkt, ('127.0.0.1', self.game_port))
        except Exception: pass

    async def handle_xonstat(self, request):
        data = await request.text()
        stats = {}
        curr_pid = None
        for line in data.split("\n"):
            p = line.split()
            if not p: continue
            if p[0] == "i":
                curr_pid = p[1]
                stats[curr_pid] = {"f": 0, "h": 0}
            elif p[0] == "e" and curr_pid:
                key = p[1].lower()
                is_utility = any(x in key for x in ["blaster", "laser", "hook"])
                if "cnt-fired" in key and not is_utility:
                    stats[curr_pid]["f"] += float(p[2])
                elif "cnt-hit" in key and not is_utility:
                    stats[curr_pid]["h"] += float(p[2])
        for pid, val in stats.items():
            if val["f"] > 0:
                acc = (val["h"] / val["f"]) * 100
                self.state["acc"][pid] = math.trunc(min(acc, 100.0) * 10) / 10.0
        return web.Response(text="OK")

    async def confirm_disconnect(self, pname):
        await asyncio.sleep(45)
        if pname in self.state["welcomed"]:
            self.state["welcomed"].remove(pname)
            await global_broadcast(content=f"💨 The arena grows cold. `{pname}` has disconnected from **{str(self.name)}**.")
            self.rcon_say(f"^2[THE BEHOLDER] ^7The arena grows cold... ^3{pname}^7 has fled.")
        if pname in self.state["disconnect_tasks"]:
            del self.state["disconnect_tasks"][pname]

    async def publish_judgment(self):
        if self.state["intermission"]: return
        self.state["intermission"] = True
        await asyncio.sleep(4.5)

        scoreboard = sorted([(self.state["id_map"].get(p, "Unknown"), f, p) for p, f in self.state["frags"].items()], key=lambda x: x[1], reverse=True)
        if not scoreboard: return

        map_n = self.state["current_map"]

        if self.name == "BLOODBATH":
            self.rcon_say(f"^1[CARNAGE] ^7The bloodbath on ^5{map_n}^7 has concluded!")
            e = discord.Embed(title="🩸 BLOODBATH REPORT", color=0x8B0000)
            e.description = f"**Arena:** `{self.name}` | **Map:** `{map_n}`"
            
            board_txt = ""
            rank = 1
            for p_n, p_f, p_id in scoreboard:
                if not is_human(p_n) and p_f == 0: continue
                p_a = self.state["acc"].get(p_id, "0.0")
                p_d = self.state["deaths"].get(p_id, 0)
                board_txt += f"**{rank}. {p_n}** ➔ 💀 `{p_f}` Kills | 🎯 `{p_a}%` Acc | ☠️ `{p_d}` Deaths\n"
                rank += 1
                
            if not board_txt: board_txt = "*Automaton skirmish. No human blood drawn.*"
            e.add_field(name="📜 THE FINAL TALLY", value=board_txt, inline=False)
            e.set_footer(text=f"The Beholder v{VERSION} | Omniscience Protocol")
            await global_broadcast(embed=e)
            return

        if len(scoreboard) < 2: return
        w_n, w_f, w_id = scoreboard[0][0], scoreboard[0][1], scoreboard[0][2]
        l_n, l_f, l_id = scoreboard[1][0], scoreboard[1][1], scoreboard[1][2]

        if w_f == 0 and l_f == 0: return
        if not is_human(w_n) and not is_human(l_n): return

        w_acc = self.state["acc"].get(w_id, "0.0")
        l_acc = self.state["acc"].get(l_id, "0.0")
        w_d = self.state["deaths"].get(w_id, 0)
        l_d = self.state["deaths"].get(l_id, 0)

        rival_text = process_rivalry(w_n, l_n)

        self.rcon_say(f"^2[JUDGMENT] ^3{w_n} ^7VICTORIOUS on ^5{map_n}!")
        self.rcon_say(f"^2[BLOOD LEDGER] ^7{rival_text.replace('*', '').replace('⚖️ ', '').replace('`', '')}")
        self.rcon_say(f"^5[DISCORD] ^7ACC-INTL: https://discord.gg/7qAh6rXsFY")

        e = discord.Embed(title=f"⚔️ JUDGMENT: {w_n} VICTORIOUS", color=0x8B0000)
        e.description = f"**Arena:** `{self.name}` | **Map:** `{map_n}`\n{rival_text}"
        
        safe_wn = discord.utils.escape_markdown(w_n)
        safe_ln = discord.utils.escape_markdown(l_n)
        
        e.add_field(name="👑 PREDATOR", value=f"> **{safe_wn}**\n> 🎯 Accuracy: `{w_acc}%`\n> 💀 K/D: `{w_f}` / `{w_d}`", inline=False)
        e.add_field(name="💀 PREY", value=f"> **{safe_ln}**\n> 🎯 Accuracy: `{l_acc}%`\n> 💀 K/D: `{l_f}` / `{l_d}`", inline=False)
        e.set_footer(text=f"The Beholder v{VERSION} | Omniscience Protocol")
        await global_broadcast(embed=e)

    async def start_services(self):
        app = web.Application()
        app.router.add_post('/submit', self.handle_xonstat)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '127.0.0.1', self.http_port)
        await site.start()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', self.udp_port))
        sock.setblocking(False)
        loop = asyncio.get_event_loop()

        print(f"[{self.name}] Eye open. UDP: {self.udp_port} | HTTP: {self.http_port} | Target: {self.game_port}")

        while True:
            try:
                data, _ = await loop.sock_recvfrom(sock, 4096)
                for line in data.decode('utf-8', errors='ignore').split('\n'):
                    raw = clean_xon(line)

                    if "chat:" in raw.lower(): continue

                    if ":gamestart:" in raw:
                        try: self.state["current_map"] = raw.split(":gamestart:")[1].split(":")[0]
                        except Exception: pass
                        self.state["frags"], self.state["deaths"], self.state["acc"], self.state["intermission"] = {}, {}, {}, False

                    elif ":join:" in raw:
                        try:
                            d = raw.split(":join:")[1].split(":", 3)
                            if len(d) >= 4:
                                pid = d[0].strip()
                                pname = RE_MASK_SCRUB.sub('', d[3].strip())

                                self.state["id_map"][pid] = pname
                                self.state["conn_map"][pid] = pname
                                self.state["frags"][pid] = self.state["frags"].get(pid, 0)
                                self.state["deaths"][pid] = self.state["deaths"].get(pid, 0)

                                if pname in self.state["disconnect_tasks"]:
                                    self.state["disconnect_tasks"][pname].cancel()
                                    del self.state["disconnect_tasks"][pname]

                                if is_human(pname) and pname not in self.state["welcomed"]:
                                    self.state["welcomed"].add(pname)
                                    
                                    async def delayed_join(p=pname, s=self):
                                        await asyncio.sleep(5)
                                        if p not in s.state["welcomed"]: return
                                        
                                        await global_broadcast(content=f"Human blood detected. `{p}` entered **{str(s.name)}**.", mention_drilla=True)
                                        s.rcon_say(f"^2[THE BEHOLDER] ^7Human blood detected: ^3{p}")
                                        if s.name != "BLOODBATH":
                                            s.rcon_say("^2[MATCHMAKING] ^7Online. The Discord has been notified.")
                                            s.rcon_say("^5[DISCORD] ^7Join the ACC-INTL Arena here: https://discord.gg/7qAh6rXsFY")
                                    bot.loop.create_task(delayed_join())
                        except Exception: pass

                    elif ":part:" in raw:
                        try:
                            conn_id = raw.split(":part:")[1].split(":")[0].strip()
                            if conn_id in self.state["conn_map"]:
                                pname = self.state["conn_map"][conn_id]
                                if pname in self.state["welcomed"]:
                                    if pname in self.state["disconnect_tasks"]: self.state["disconnect_tasks"][pname].cancel()
                                    self.state["disconnect_tasks"][pname] = bot.loop.create_task(self.confirm_disconnect(pname))
                        except Exception: pass

                    elif ":kill:frag:" in raw:
                        try:
                            d = raw.split(":kill:frag:")[1].split(":")
                            if d[0] in self.state["id_map"]: self.state["frags"][d[0]] += 1
                            if d[1] in self.state["id_map"]: self.state["deaths"][d[1]] += 1
                        except Exception: pass

                    elif ":kill:suicide:" in raw or ":kill:tk:" in raw:
                        try:
                            tag = ":kill:suicide:" if ":kill:suicide:" in raw else ":kill:tk:"
                            d = raw.split(tag)[1].split(":")
                            if d[0] in self.state["id_map"]: self.state["deaths"][d[0]] += 1
                        except Exception: pass

                    elif ":gameover" in raw:
                        bot.loop.create_task(self.publish_judgment())
            except Exception:
                await asyncio.sleep(0.1)

# ==============================================================================
# 🌐 GLOBAL COMMANDS & LIFECYCLE
# ==============================================================================

@bot.command(aliases=['tug', 'rivalry'])
async def slider(ctx, p1_search: str, p2_search: str):
    """Visualizes the Attrition Slider using Python's flawless Unicode search."""
    with sqlite3.connect('beholder.db') as conn:
        c = conn.cursor()
        rivalries = c.execute("SELECT p1_name, p2_name, p1_pts, p2_pts FROM rivalries").fetchall()

    s1 = p1_search.lower()
    s2 = p2_search.lower()
    
    target = None
    
    # Priority 1: Exact match check (prevents partial mismatches like EKKO matching ⚠EkkO⚠)
    for r in rivalries:
        db_p1 = r[0].lower()
        db_p2 = r[1].lower()
        if (s1 == db_p1 and s2 == db_p2) or (s1 == db_p2 and s2 == db_p1):
            target = r
            break
            
    # Priority 2: Substring match check (the original behavior)
    if not target:
        for r in rivalries:
            db_p1 = r[0].lower()
            db_p2 = r[1].lower()
            if (s1 in db_p1 and s2 in db_p2) or (s1 in db_p2 and s2 in db_p1):
                target = r
                break

    if not target:
        await ctx.send(f"👁️ The void holds no memory of a conflict matching `{p1_search}` and `{p2_search}`.\n*(Tip: If a name has spaces, wrap it in quotes like `!slider DRUMMER \"SOME GUY\"`)*")
        return

    db_p1 = target[0]
    db_p2 = target[1]
    pt1 = target[2]
    pt2 = target[3]

    if s1 in db_p1.lower():
        score1 = pt1
        score2 = pt2
        name1 = db_p1
        name2 = db_p2
    else:
        score1 = pt2
        score2 = pt1
        name1 = db_p2
        name2 = db_p1

    true1 = score1 // 3
    true2 = score2 // 3

    pos = 9 - score1 + score2
    track = list("╟──╫──╫──┼──╫──╫──╢")
    track[pos] = "█"
    visual = "".join(track)

    if score1 > score2:
        icon1, icon2 = "👑", "💀"
    elif score2 > score1:
        icon1, icon2 = "💀", "👑"
    else:
        icon1, icon2 = "⚖️", "⚖️"

    safe_n1 = discord.utils.escape_markdown(name1)
    safe_n2 = discord.utils.escape_markdown(name2)

    e = discord.Embed(title="⚖️ THE APEX SLIDER", color=0x8B0000)
    e.description = f"```\n{name1.upper()}\n[ {visual} ]\n{name2.upper().rjust(23)}\n```"
    
    e.add_field(name=f"{icon1} {safe_n1}", value=f"> Shards: `{score1}`\n> True Points: `{true1}`", inline=True)
    e.add_field(name=f"{icon2} {safe_n2}", value=f"> Shards: `{score2}`\n> True Points: `{true2}`", inline=True)
    e.set_footer(text=f"The Beholder v{VERSION} | Omniscience Protocol")

    await ctx.send(embed=e)


@bot.command()
@commands.has_permissions(administrator=True)
async def fuse(ctx, old_name: str, new_name: str):
    """Merges all match history from one name into another (Admin Only)."""
    with sqlite3.connect('beholder.db') as conn:
        c = conn.cursor()
        old_n, new_n = old_name.upper(), new_name.upper()
        
        # Update Matches
        c.execute("UPDATE matches SET winner = ? WHERE UPPER(winner) = ?", (new_name, old_n))
        c.execute("UPDATE matches SET loser = ? WHERE UPPER(loser) = ?", (new_name, old_n))
        
        # Update Rivalry Names (Math is too complex to merge, so we delete old rivalry entries 
        # and recommend running rebuild_history.py after a fuse)
        c.execute("DELETE FROM rivalries WHERE UPPER(p1_name) = ? OR UPPER(p2_name) = ?", (old_n, old_n))
        conn.commit()
        
    await ctx.send(f"☢️ **FUSION COMPLETE:** All records of `{old_name}` have been absorbed by `{new_name}`. Run `rebuild_history.py` to fix sliders.")

@bot.command()
async def board(ctx):
    with sqlite3.connect('beholder.db') as conn:
        c = conn.cursor()
        rivals = c.execute("SELECT p1_name, p2_name, p1_pts, p2_pts FROM rivalries").fetchall()
        
        grinder = c.execute("SELECT UPPER(name) as uname, COUNT(*) as c FROM (SELECT winner as name FROM matches WHERE winner NOT LIKE '%VOID%' UNION ALL SELECT loser FROM matches WHERE loser NOT LIKE '%VOID%') GROUP BY uname ORDER BY c DESC LIMIT 1").fetchone()
        feud = c.execute("SELECT UPPER(r.p1_name), UPPER(r.p2_name), COUNT(m.match_id) as c FROM matches m JOIN rivalries r ON m.pair_key = r.pair_key WHERE r.p1_name NOT LIKE '%VOID%' AND r.p2_name NOT LIKE '%VOID%' GROUP BY m.pair_key ORDER BY c DESC LIMIT 1").fetchone()

    player_stats = {}
    for p1, p2, pt1, pt2 in rivals:
        if "VOID" in p1.upper() or "VOID" in p2.upper():
            continue
            
        p1_u = p1.upper()
        p2_u = p2.upper()
        
        if p1_u not in player_stats: 
            player_stats[p1_u] = {"tp": 0, "shards": 0}
        if p2_u not in player_stats: 
            player_stats[p2_u] = {"tp": 0, "shards": 0}
        
        player_stats[p1_u]["tp"] += (pt1 // 3)
        player_stats[p1_u]["shards"] += pt1
        
        player_stats[p2_u]["tp"] += (pt2 // 3)
        player_stats[p2_u]["shards"] += pt2
        
    sorted_scores = sorted(player_stats.items(), key=lambda x: (x[1]["tp"], x[1]["shards"]), reverse=True)

    e = discord.Embed(title="🩸 THE BLOOD LEDGER", description="*Glory is finite. To rise, others must fall.*", color=0x8B0000)
    
    apex_list = []
    unproven_list = []
    
    rank = 1
    for n, stats in sorted_scores:
        tp = stats["tp"]
        shards = stats["shards"]
        safe_n = discord.utils.escape_markdown(n)
        
        if tp > 0:
            apex_list.append(f"{rank}. {safe_n} — **{tp} True Points** *(from {shards} Shards)*")
            rank += 1
        else:
            unproven_list.append(f"{safe_n} ({shards} Shards)")

    apex_txt = "\n".join(apex_list)
    e.add_field(name="🏆 APEX PREDATORS", value=apex_txt or "*The void is currently empty. No True Points secured.*", inline=False)
    
    if unproven_list:
        chunk = ""
        field_count = 0
        for item in unproven_list:
            if len(chunk) + len(item) > 950:
                title_name = "🌑 THE UNPROVEN (0 True Points)" if field_count == 0 else "🌑 THE UNPROVEN (Cont.)"
                e.add_field(name=title_name, value=chunk.rstrip(", "), inline=False)
                chunk = item + ", "
                field_count += 1
            else:
                chunk += item + ", "
        if chunk:
            title_name = "🌑 THE UNPROVEN (0 True Points)" if field_count == 0 else "🌑 THE UNPROVEN (Cont.)"
            e.add_field(name=title_name, value=chunk.rstrip(", "), inline=False)

    if grinder: 
        safe_g = discord.utils.escape_markdown(grinder[0])
        e.add_field(name="⚙️ THE GRINDER", value=f"{safe_g} ({grinder[1]} games)", inline=True)
    if feud: 
        safe_f1 = discord.utils.escape_markdown(feud[0])
        safe_f2 = discord.utils.escape_markdown(feud[1])
        e.add_field(name="🩸 BLOOD FEUD", value=f"{safe_f1} vs {safe_f2} ({feud[2]} games)", inline=True)
        
    e.set_footer(text=f"The Beholder v{VERSION} | Omniscience Protocol")
    await ctx.send(embed=e)

@bot.command()
async def archive(ctx):
    with sqlite3.connect('beholder.db') as conn:
        c = conn.cursor()
        query = """
        SELECT 
            UPPER(p.name), 
            SUM(CASE WHEN UPPER(m.winner) = UPPER(p.name) THEN 1 ELSE 0 END) as w,
            SUM(CASE WHEN UPPER(m.loser) = UPPER(p.name) THEN 1 ELSE 0 END) as l
        FROM (SELECT DISTINCT UPPER(winner) as name FROM matches UNION SELECT DISTINCT UPPER(loser) FROM matches) p
        JOIN matches m ON UPPER(m.winner) = p.name OR UPPER(m.loser) = p.name
        WHERE UPPER(p.name) NOT LIKE '%VOID%'
        GROUP BY p.name
        ORDER BY w DESC, l ASC
        """
        records = c.execute(query).fetchall()

    e = discord.Embed(title="📜 THE GRAND ARCHIVE (POOL STANDINGS)", description="*Raw Lifetime Match Records (Bypasses Attrition Math)*\n\n", color=0x8B0000)
    
    chunk = ""
    field_count = 0
    for i, (n, w, l) in enumerate(records, 1):
        safe_n = discord.utils.escape_markdown(n)
        line = f"{i}. **{safe_n}** — **{w} W** / {l} L *(Played: {w+l})*\n"
        if len(chunk) + len(line) > 950:
            e.add_field(name="🌐 ABSOLUTE RECORDS" if field_count == 0 else "🌐 ABSOLUTE RECORDS (Cont.)", value=chunk, inline=False)
            chunk = line
            field_count += 1
        else:
            chunk += line
    if chunk:
        e.add_field(name="🌐 ABSOLUTE RECORDS" if field_count == 0 else "🌐 ABSOLUTE RECORDS (Cont.)", value=chunk, inline=False)

    e.set_footer(text=f"The Beholder v{VERSION} | Raw Database Extraction")
    await ctx.send(embed=e)

@tasks.loop(hours=24)
async def temporal_decay():
    with sqlite3.connect('beholder.db') as conn:
        c = conn.cursor()
        limit = (datetime.now() - timedelta(days=7)).isoformat()
        
        query = "SELECT pair_key, p1_pts, p2_pts FROM rivalries WHERE last_update < ? AND (p1_pts > 0 OR p2_pts > 0)"
        old_rivals = c.execute(query, (limit,)).fetchall()
        
        for pk, p1, p2 in old_rivals:
            if p1 > p2:
                n1 = p1 - 1
                n2 = p2 + 1 if (p1 + p2 >= 9) else p2
            elif p2 > p1:
                n1 = p1 + 1 if (p1 + p2 >= 9) else p1
                n2 = p2 - 1
            else:
                n1, n2 = p1, p2 # Tied, no decay
                
            c.execute("UPDATE rivalries SET p1_pts=?, p2_pts=?, last_update=? WHERE pair_key=?", (n1, n2, datetime.now().isoformat(), pk))
        conn.commit()

@bot.event
async def on_ready():
    global HAS_STARTED
    if HAS_STARTED:
        print("👁️ Reconnected to Discord Gateway. Core loops are already running.")
        return
        
    HAS_STARTED = True
    print(f"👁️ Beholder v{VERSION} Ready. The Omniscience Protocol is online.")

    try:
        with open("servers.json", "r") as f:
            servers = json.load(f)
    except FileNotFoundError:
        print("🚨 FATAL: servers.json not found. The Beholder has no eyes.")
        return

    for srv in servers:
        arena = ArenaTracker(
            name=srv["name"],
            game_port=srv["game_port"],
            udp_port=srv["udp_port"],
            http_port=srv["http_port"],
            rcon_pass=srv["rcon_pass"]
        )
        bot.loop.create_task(arena.start_services())

    if not temporal_decay.is_running(): 
        temporal_decay.start()


@bot.command(aliases=['stats', 'shards'])
async def profile(ctx, *, player_name: str):
    """Shows exactly who a player got their shards from."""
    with sqlite3.connect('beholder.db') as conn:
        c = conn.cursor()
        search = player_name.lower()
        rivalries = c.execute("SELECT p1_name, p2_name, p1_pts, p2_pts FROM rivalries WHERE LOWER(p1_name) LIKE ? OR LOWER(p2_name) LIKE ?", (f'%{search}%', f'%{search}%')).fetchall()
        
    if not rivalries:
        return await ctx.send(f"👁️ The void holds no memory of `{player_name}`.")
        
    real_name = player_name
    for r in rivalries:
        if search == r[0].lower(): real_name = r[0]; break
        if search == r[1].lower(): real_name = r[1]; break

    total_shards, total_tp = 0, 0
    breakdown = []
    
    for p1, p2, pt1, pt2 in rivalries:
        if "VOID" in p1.upper() or "VOID" in p2.upper(): continue
        is_p1 = search in p1.lower()
        opponent = p2 if is_p1 else p1
        my_shards = pt1 if is_p1 else pt2
        
        if my_shards > 0:
            my_tp = my_shards // 3
            total_shards += my_shards
            total_tp += my_tp
            breakdown.append((my_shards, my_tp, opponent))
            
    breakdown.sort(key=lambda x: x[0], reverse=True)
    
    e = discord.Embed(title=f"🩸 BLOOD TRAIL: {discord.utils.escape_markdown(real_name.upper())}", color=0x8B0000)
    e.add_field(name="Total Spoils", value=f"> **True Points:** `{total_tp}`\n> **Total Shards:** `{total_shards}`", inline=False)
    
    if breakdown:
        chunk = ""
        for shards, tp, opp in breakdown:
            line = f"**{discord.utils.escape_markdown(opp)}** ➔ `{shards}` Shards *(Yields {tp} TP)*\n"
            if len(chunk) + len(line) > 900:
                e.add_field(name="The Blood Trail", value=chunk, inline=False)
                chunk = line
            else:
                chunk += line
        if chunk:
            e.add_field(name="The Blood Trail" if len(e.fields) == 1 else "The Blood Trail (Cont.)", value=chunk, inline=False)
    else:
        e.add_field(name="The Blood Trail", value="*No shards currently held against any opponent.*", inline=False)
        
    e.set_footer(text=f"The Beholder v{VERSION} | Omniscience Protocol")
    await ctx.send(embed=e)


@bot.command()
async def help(ctx):
    """Displays the Omniscience Protocol Command Directory."""
    e = discord.Embed(title="👁️ THE BEHOLDER: COMMAND DIRECTORY", color=0x8B0000)
    e.description = "*To rise in the Apex, others must fall. All blood is logged.*"
    
    e.add_field(name="🩸 BLOOD LEDGERS (Public)", 
                value="`!board` — The active Blood Ledger and Apex Rankings.\n`!archive` — Raw lifetime wins and losses records.", 
                inline=False)
    
    e.add_field(name="⚖️ TACTICAL ANALYSIS (Public)", 
                value="`!slider <P1> <P2>` — Visual 9-shard Attrition track.\n`!profile <Player>` — Personal spoils and victim list. *(Aliases: !shards, !stats)*", 
                inline=False)
    
    e.add_field(name="☢️ OVERSIGHT (Admin Only)", 
                value="`!fuse <Old> <New>` — Merge historical name records. Run `rebuild_history.py` after use.", 
                inline=False)

    e.set_footer(text=f"The Beholder v{VERSION} | Omniscience Protocol")
    await ctx.send(embed=e)

# --- IGNITION ---
bot.run(DISCORD_TOKEN)
