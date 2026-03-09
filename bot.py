# ==============================================================================
# 👁️ THE BEHOLDER - EMERALD GAZE (v20.8.5-OMNISCIENCE)
# ==============================================================================
# Architecture: Gemini (AI) | Concept: Drummer (BAINELF)
# Multi-Server Expansion: Decoupled State, Dynamic Porting, Unified Ledger
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

# --- OPSEC SHIELD: DISCORD TOKEN ONLY ---
try:
    with open('secret.txt', 'r') as f:
        DISCORD_TOKEN = f.readline().strip()
except FileNotFoundError:
    print("❌ FATAL: 'secret.txt' missing. The Eye remains closed.")
    exit()

VERSION = "20.8.5-OMNISCIENCE"
HAS_STARTED = False # The Reconnect Lock

# --- GLOBAL DATABASE INITIALIZATION ---
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

RE_COLOR = re.compile(r'\^([0-9]|x[0-9a-fA-F]{3})')
RE_IP_SCRUB = re.compile(r'^([0-9a-fA-F\.:]{4,}:)+')

def clean_xon(raw_text):
    return RE_IP_SCRUB.sub('', RE_COLOR.sub('', raw_text).strip())

def is_human(name):
    if not name or len(name) < 2: return False
    n = name.lower()
    return "[guard]" not in n and n not in ["bot", "none", "unknown"]

# --- GLOBAL HELPERS ---
async def global_broadcast(content=None, embed=None, mention_drilla=False):
    with sqlite3.connect('beholder.db') as conn:
        res = conn.cursor().execute("SELECT value FROM config WHERE key = 'announcement_channel'").fetchone()
    if res and (chan := bot.get_channel(int(res[0]))):
        prefix = "👁️ **@drilla:** " if mention_drilla else ""
        await chan.send(content=f"{prefix}{content}" if content else None, embed=embed)

def process_rivalry(winner, loser):
    if not is_human(winner) or not is_human(loser): return "*Automaton match logged. No blood drawn.*"
    with sqlite3.connect('beholder.db') as conn:
        c = conn.cursor()
        pair_list = sorted([winner, loser], key=str.lower)
        pair_key = "_".join([n.lower() for n in pair_list])
        p1, p2 = pair_list[0], pair_list[1]

        c.execute("INSERT OR IGNORE INTO players (xon_name) VALUES (?)", (winner,))
        c.execute("INSERT OR IGNORE INTO players (xon_name) VALUES (?)", (loser,))

        res = c.execute("SELECT p1_pts, p2_pts FROM rivalries WHERE pair_key = ?", (pair_key,)).fetchone()
        pt1, pt2 = res if res else (0, 0)

        is_p1_win = (winner.lower() == p1.lower())
        w_pts, l_pts = (pt1, pt2) if is_p1_win else (pt2, pt1)

        if w_pts + l_pts < 3: w_pts += 1
        elif l_pts > 0: w_pts += 1; l_pts -= 1

        n1, n2 = (w_pts, l_pts) if is_p1_win else (l_pts, w_pts)

        c.execute("INSERT OR REPLACE INTO rivalries VALUES (?, ?, ?, ?, ?, ?)", (pair_key, p1, p2, n1, n2, datetime.now().isoformat()))
        c.execute("INSERT INTO matches (winner, loser, pair_key) VALUES (?, ?, ?)", (winner, loser, pair_key))
        conn.commit()
        return f"⚖️ **Rivalry Pool:** {n1} - {n2}"

# ==============================================================================
# ⚔️ THE ARENA BLUEPRINT (Per-Server Isolation)
# ==============================================================================
class ArenaTracker:
    def __init__(self, name, game_port, udp_port, http_port, rcon_pass):
        self.name = name
        self.game_port = game_port
        self.udp_port = udp_port
        self.http_port = http_port
        self.rcon_pass = rcon_pass
        
        # ISOLATED STATE MAP
        self.state = {
            "id_map": {}, "conn_map": {}, "frags": {}, "deaths": {}, "acc": {},
            "intermission": False, "welcomed": set(), "disconnect_tasks": {},
            "current_map": "Unknown"
        }

    def rcon_say(self, msg: str):
        if not self.rcon_pass: return
        try:
            pkt = b'\xff\xff\xff\xffrcon ' + self.rcon_pass.encode() + b' say ' + msg.encode()
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
                s.sendto(pkt, ('127.0.0.1', self.game_port))
        except Exception: pass

    async def handle_xonstat(self, request):
        """HTTP Endpoint for accuracy tracking, isolated to this specific arena."""
        data = await request.text()
        curr_pid, stats = None, {}
        for line in data.split('\n'):
            p = line.split()
            if not p: continue
            if p[0] == 'i':
                curr_pid = p[1]
                stats[curr_pid] = {'f': 0, 'h': 0}
            elif p[0] == 'e' and curr_pid:
                if p[1].lower() == 'acc-vaporizer-cnt-fired': stats[curr_pid]['f'] = float(p[2])
                elif p[1].lower() == 'acc-vaporizer-cnt-hit': stats[curr_pid]['h'] = float(p[2])

        for pid, val in stats.items():
            if val['f'] > 0:
                acc = (val['h'] / val['f']) * 100
                self.state["acc"][pid] = math.trunc(min(acc, 100.0) * 10) / 10.0
        return web.Response(text="OK")

    async def confirm_disconnect(self, pname):
        await asyncio.sleep(45)
        if pname in self.state["welcomed"]:
            self.state["welcomed"].remove(pname)
            await global_broadcast(content=f"💨 The arena grows cold. `{pname}` has disconnected from **{self.name}**.")
            self.rcon_say(f"^2[THE BEHOLDER] ^7The arena grows cold... ^3{pname}^7 has fled.")
        if pname in self.state["disconnect_tasks"]: del self.state["disconnect_tasks"][pname]

    async def publish_judgment(self):
        if self.state["intermission"]: return
        self.state["intermission"] = True
        await asyncio.sleep(3.0)

        scoreboard = sorted([(self.state["id_map"].get(p, "Unknown"), f, p) for p, f in self.state["frags"].items()], key=lambda x: x[1], reverse=True)
        if len(scoreboard) < 2: return

        (w_n, w_f, w_id), (l_n, l_f, l_id) = scoreboard[0], scoreboard[1]

        if w_f == 0 and l_f == 0: return
        if not is_human(w_n) and not is_human(l_n): return

        w_acc, l_acc = self.state["acc"].get(w_id, "0.0"), self.state["acc"].get(l_id, "0.0")
        w_d, l_d = self.state["deaths"].get(w_id, 0), self.state["deaths"].get(l_id, 0)

        rival_text = process_rivalry(w_n, l_n)
        map_n = self.state["current_map"]

        self.rcon_say(f"^2[JUDGMENT] ^3{w_n} ^7VICTORIOUS on ^5{map_n}!")
        self.rcon_say(f"^2[BLOOD LEDGER] ^7{rival_text.replace('*', '').replace('⚖️ ', '').replace('**', '')}")

        e = discord.Embed(title=f"⚔️ JUDGMENT: {w_n} VICTORIOUS", color=0x8B0000)
        e.description = f"**Arena:** `{self.name}` | **Map:** `{map_n}`\n{rival_text}"
        e.add_field(name="👑 PREDATOR", value=f"> **{w_n}**\n> 🎯 Accuracy: `{w_acc}%`\n> 💀 K/D: `{w_f}` / `{w_d}`", inline=False)
        e.add_field(name="💀 PREY", value=f"> **{l_n}**\n> 🎯 Accuracy: `{l_acc}%`\n> 💀 K/D: `{l_f}` / `{l_d}`", inline=False)
        e.set_footer(text=f"The Beholder v{VERSION} | Omniscience Protocol")

        await global_broadcast(embed=e)

    async def start_services(self):
        """Launches both the UDP listener and the HTTP server for this specific arena."""
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

                    if ":gamestart:" in raw:
                        try: self.state["current_map"] = raw.split(":gamestart:")[1].split(":")[0]
                        except: pass
                        self.state["frags"], self.state["deaths"], self.state["acc"], self.state["intermission"] = {}, {}, {}, False

                    elif ":join:" in raw:
                        try:
                            d = raw.split(":join:")[1].split(":", 3)
                            if len(d) >= 4:
                                pid, pname = d[0].strip(), d[3].strip()
                                self.state["id_map"][pid] = pname
                                self.state["conn_map"][pid] = pname
                                self.state["frags"][pid] = self.state["frags"].get(pid, 0)
                                self.state["deaths"][pid] = self.state["deaths"].get(pid, 0)

                                if pname in self.state["disconnect_tasks"]:
                                    self.state["disconnect_tasks"][pname].cancel(); del self.state["disconnect_tasks"][pname]

                                if is_human(pname) and pname not in self.state["welcomed"]:
                                    self.state["welcomed"].add(pname)
                                    bot.loop.create_task(global_broadcast(content=f"Human blood detected. `{pname}` entered **{self.name}**.", mention_drilla=True))
                                    self.rcon_say(f"^2[THE BEHOLDER] ^7Human blood detected: ^3{pname}")
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
            except Exception as e:
                # Silently catch malformed network packets so the loop doesn't break
                await asyncio.sleep(0.1)

# ==============================================================================
# 🌐 GLOBAL COMMANDS & LIFECYCLE
# ==============================================================================

@bot.command()
async def board(ctx):
    with sqlite3.connect('beholder.db') as conn:
        c = conn.cursor()
        rivals = c.execute("SELECT p1_name, p2_name, p1_pts, p2_pts FROM rivalries").fetchall()
        grinder = c.execute("SELECT name, COUNT(*) as c FROM (SELECT winner as name FROM matches UNION ALL SELECT loser FROM matches) GROUP BY name ORDER BY c DESC LIMIT 1").fetchone()
        feud = c.execute("SELECT r.p1_name, r.p2_name, COUNT(m.match_id) as c FROM matches m JOIN rivalries r ON m.pair_key = r.pair_key GROUP BY m.pair_key ORDER BY c DESC LIMIT 1").fetchone()

    scores = {}
    for p1, p2, pt1, pt2 in rivals:
        scores[p1], scores[p2] = scores.get(p1, 0) + pt1, scores.get(p2, 0) + pt2
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    e = discord.Embed(title="🩸 THE BLOOD LEDGER", description="*Glory is finite. To rise, others must fall.*", color=0x8B0000)
    list_txt = "\n".join([f"{i+1}. `{n}` — **{p} pts**" for i, (n, p) in enumerate(sorted_scores) if p > 0])

    e.add_field(name="🏆 ACTIVE POINTS", value=list_txt or "The void is currently empty.", inline=False)
    if grinder: e.add_field(name="⚙️ THE GRINDER", value=f"`{grinder[0]}` ({grinder[1]} games)", inline=True)
    if feud: e.add_field(name="🩸 BLOOD FEUD", value=f"`{feud[0]}` vs `{feud[1]}` ({feud[2]} games)", inline=True)
    e.set_footer(text=f"The Beholder v{VERSION} | Omniscience Protocol")

    await ctx.send(embed=e)

@tasks.loop(hours=24)
async def temporal_decay():
    with sqlite3.connect('beholder.db') as conn:
        c = conn.cursor()
        limit = (datetime.now() - timedelta(days=30)).isoformat()
        old_rivals = c.execute("SELECT pair_key, p1_pts, p2_pts FROM rivalries WHERE last_update < ? AND (p1_pts > 0 OR p2_pts > 0)", (limit,)).fetchall()
        for pk, p1, p2 in old_rivals:
            n1, n2 = (max(0, p1-1), p2) if p1 > p2 else (p1, max(0, p2-1)) if p2 > p1 else (max(0, p1-1), max(0, p2-1))
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

    if not temporal_decay.is_running(): temporal_decay.start()

# --- IGNITION ---
bot.run(DISCORD_TOKEN)
