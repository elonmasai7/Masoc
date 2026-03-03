#!/usr/bin/env sh
set -eu

SOURCE_DIR=${SOURCE_DIR:-/backup-source}
HOST_TAG=${HOST_TAG:-medshield-clinic}
RET_DAILY=${BACKUP_RETENTION_DAILY:-14}
RET_WEEKLY=${BACKUP_RETENTION_WEEKLY:-8}
RET_MONTHLY=${BACKUP_RETENTION_MONTHLY:-12}

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Backup source directory not found: $SOURCE_DIR"
  exit 1
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting encrypted restic backup"
restic backup "$SOURCE_DIR" --tag "$HOST_TAG" --tag "daily"
restic forget --prune \
  --keep-daily "$RET_DAILY" \
  --keep-weekly "$RET_WEEKLY" \
  --keep-monthly "$RET_MONTHLY"
restic check --read-data-subset=5%

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Backup workflow completed"
