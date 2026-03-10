#!/bin/bash
# 👁️ OMNISCIENCE OVERSEER v24.0 (SCORCHED EARTH)

PATH_BOT="/root/The_Beholder"
PATH_XONOTIC="/home/xonotic/Xonotic"

if [ "$1" == "wipe" ]; then
    echo "🧹 Wiping all sessions..."
    pkill -9 -f xonotic-
    pkill -9 -f bot.py
    screen -ls | grep Detached | cut -d. -f1 | awk '{print $1}' | xargs -r screen -X -S quit
    screen -wipe
    sleep 3
fi

if ! screen -list | grep -q "beholder"; then
    echo "👁️ Starting Beholder..."
    screen -dmS beholder bash -c "cd $PATH_BOT && source venv/bin/activate && python3 bot.py"
fi

# Isolated Binary Launches
screen -dmS arena_alpha bash -c "cd $PATH_XONOTIC && ./xonotic-alpha -userdir $PATH_XONOTIC/alpha"
sleep 3
screen -dmS arena_beta bash -c "cd $PATH_XONOTIC && ./xonotic-beta -userdir $PATH_XONOTIC/beta"
sleep 3
screen -dmS arena_gamma bash -c "cd $PATH_XONOTIC && ./xonotic-gamma -userdir $PATH_XONOTIC/gamma"
sleep 3
screen -dmS arena_delta bash -c "cd $PATH_XONOTIC && ./xonotic-delta -userdir $PATH_XONOTIC/delta"

echo "✅ Scorched Earth Cluster Synchronized."
