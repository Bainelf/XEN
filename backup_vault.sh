#!/bin/bash

# ==========================================
#   TACTICAL DATA PRESERVATION - SUBDOMINA KHEPRA
# ==========================================

# --- TACTICAL COGITATOR PARAMETERS ---
BACKUP_DIR="/root/Backups"
PROJECT_DIR="/root/The_Beholder"
WEBHOOK_URL="https://discord.com/api/webhooks/1482615046096945206/L5Xx0vaaBfPoyljJT9A0hOzilRdiDm-qWMgy9TrN2wyETduMVpeGr6drE5hg-KcAz4n1" # <--- INSERT NOOSPHERE LINK HERE
DATE=$(date +%Y%m%d_%H%M)
ARCHIVE_NAME="Holy_Data_Vault_$DATE.tar.gz"

# --- RITE 1: Securing the Perimeter ---
mkdir -p "$BACKUP_DIR"

# --- RITE 2: Memory Extraction ---
echo "[$(date)] Subdomina Khepra: Initiating core extraction protocols..."
sqlite3 "$PROJECT_DIR/beholder.db" .dump > "$PROJECT_DIR/sacred_memory.sql"

# --- RITE 3: Vault Sealing ---
echo "[$(date)] Subdomina Khepra: Sealing the data vault. Applying compression..."
cd /root
tar -czf "$BACKUP_DIR/$ARCHIVE_NAME" The_Beholder/
SIZE=$(du -sh "$BACKUP_DIR/$ARCHIVE_NAME" | cut -f1)

# --- RITE 4: Purging Traces ---
rm -f "$PROJECT_DIR/sacred_memory.sql"

# --- RITE 5: Noosphere Uplink (Discord) ---
payload=$(cat <<EOF
{
  "username": "Subdomina Khepra",
  "embeds": [{
    "title": "⚙️ TACTICAL ASSET PRESERVED",
    "description": "Magos, the cohort's data has been secured. The Omniscience Protocol remains intact against scrapcode and logic-corruption.",
    "color": 11862016,
    "fields": [
      {"name": "📜 Vault Designation", "value": "$ARCHIVE_NAME", "inline": false},
      {"name": "⚖️ Mass", "value": "$SIZE", "inline": true},
      {"name": "🏛️ Sector", "value": "$BACKUP_DIR", "inline": true}
    ],
    "footer": {"text": "Flesh is fallible, but ritual honors the Machine."}
  }]
}
EOF
)

curl -s -H "Content-Type: application/json" -X POST -d "$payload" "$WEBHOOK_URL"

echo "[$(date)] Transmission complete. Praise the Omnissiah."

