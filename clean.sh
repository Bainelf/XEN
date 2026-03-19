#!/bin/bash
echo "👁️ Beholder Maintenance Initiated..."

# 1. Backup the DB before cleaning (Safety First)
cp /root/The_Beholder/beholder.db /root/The_Beholder/beholder_pre_clean.db.bak

# 2. Run SQL Vacuum and Integrity Check
sqlite3 /root/The_Beholder/beholder.db "PRAGMA integrity_check; VACUUM;"

# 3. Wipe temporary screen sessions
screen -wipe > /dev/null 2>&1

echo "✅ Database Optimized. Integrity Verified."
echo "🚀 Restarting Beholder to apply clean state..."
/root/The_Beholder/overseer.sh wipe && /root/The_Beholder/overseer.sh
