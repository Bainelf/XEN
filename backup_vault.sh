#!/bin/bash
# 👁️ OMNISCIENCE VAULT BACKUP v1.0

TIMESTAMP=$(date +"%Y-%m-%d_%H%M%S")
BACKUP_NAME="Borderworld_Backup_$TIMESTAMP.tar.gz"
BACKUP_DIR="/root/Backups"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "📦 Initializing Vault Backup: $BACKUP_NAME..."

# Create the compressed archive
tar -czf $BACKUP_DIR/$BACKUP_NAME \
    /root/The_Beholder/bot.py \
    /root/The_Beholder/overseer.sh \
    /root/The_Beholder/servers.json \
    /root/The_Beholder/beholder.db \
    /root/The_Beholder/requirements.txt \
    /home/xonotic/Xonotic/data/server.cfg \
    /home/xonotic/Xonotic/data/beta.cfg \
    /home/xonotic/Xonotic/data/gamma.cfg \
    /home/xonotic/Xonotic/data/delta.cfg

echo "✅ Backup Complete: $BACKUP_DIR/$BACKUP_NAME"
echo "🛡️ Total size: $(du -sh $BACKUP_DIR/$BACKUP_NAME | cut -f1)"
