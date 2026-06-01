#!/bin/sh

if ! docker inspect "$MUMC_CONTAINER_NAME" >/dev/null 2>&1
then
    echo "[$(date)] Container '$MUMC_CONTAINER_NAME' not found."
    exit 0
fi

CONFIG_FILE="/usr/src/app/config/mumc_config.yaml"

if ! docker exec "$MUMC_CONTAINER_NAME" test -f "$CONFIG_FILE"
then
    echo "[$(date)] Initial setup has not been completed."
    exit 0
fi

echo "[$(date)] Running MUMC..."

if docker exec "$MUMC_CONTAINER_NAME" /run.sh
then
    echo "[$(date)] MUMC completed successfully."
else
    echo "[$(date)] MUMC failed."
fi