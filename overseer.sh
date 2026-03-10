#!/bin/bash
# 👁️ OMNISCIENCE OVERSEER v20.8.7 (STABLE CLUSTER)

# --- CONFIGURATION ---
PATH_BOT="/root/The_Beholder"
PATH_XONOTIC="/home/xonotic/Xonotic"

# 1. THE NUCLEAR WIPE
if [ "$1" == "wipe" ]; then
    echo "🧹 Wiping all sessions and killing ghost processes..."
    pkill -9 -f xonotic-linux64-dedicated
    pkill -9 -f bot.py
    screen -ls | grep Detached | cut -d. -f1 | awk '{print $1}' | xargs -r screen -X -S quit
    screen -wipe
    sleep 3
fi

# 2. START BEHOLDER
if ! screen -list | grep -q "beholder"; then
    echo "👁️ Starting Beholder..."
    screen -dmS beholder bash -c "cd $PATH_BOT && source venv/bin/activate && python3 bot.py"
fi

# 3. START ARENAS (Isolated Sessions)
# Alpha
screen -dmS arena_alpha bash -c "cd $PATH_XONOTIC && ./xonotic-linux64-dedicated -sessionid alpha -config server.cfg"

# Beta
screen -dmS arena_beta bash -c "cd $PATH_XONOTIC && ./xonotic-linux64-dedicated -sessionid beta -config beta.cfg"

# Gamma
screen -dmS arena_gamma bash -c "cd $PATH_XONOTIC && ./xonotic-linux64-dedicated -sessionid gamma -config gamma.cfg"

# Delta (Bloodbath)
screen -dmS arena_delta bash -c "cd $PATH_XONOTIC && ./xonotic-linux64-dedicated -sessionid delta -config delta.cfg"

echo "✅ All 4 arenas and the Beholder are synchronized."

