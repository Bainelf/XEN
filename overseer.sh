#!/bin/bash

# --- CONFIGURATION ---
PATH_BOT="/root/The_Beholder"
PATH_XONOTIC="/home/xonotic/Xonotic"

# 1. KILL EVERYTHING (If "wipe" argument is passed)
if [ "$1" == "wipe" ]; then
    echo "🧹 Wiping all sessions..."
    pkill -f xonotic
    pkill -f bot.py
    killall screen
    screen -wipe
    sleep 2
fi

# 2. CHECK/START BEHOLDER
if ! screen -list | grep -q "beholder"; then
    echo "👁️ Starting Beholder..."
    screen -dmS beholder bash -c "cd $PATH_BOT && source venv/bin/activate && python3 bot.py"
fi

# 3. CHECK/START ALPHA
if ! screen -list | grep -q "arena_alpha"; then
    echo "⚔️ Starting Arena Alpha..."
    screen -dmS arena_alpha bash -c "cd $PATH_XONOTIC && ./xonotic-linux64-dedicated +serverconfig server.cfg -sessionid alpha"
fi

# 4. CHECK/START BETA
if ! screen -list | grep -q "arena_beta"; then
    echo "⚔️ Starting Arena Beta..."
    screen -dmS arena_beta bash -c "cd $PATH_XONOTIC && ./xonotic-linux64-dedicated +serverconfig beta.cfg -sessionid beta"
fi

echo "✅ All systems operational."

