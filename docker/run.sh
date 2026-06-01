#!/bin/sh

LOCKFILE="/usr/src/app/logs/mumc.lock"

cd /usr/src/app

if ! flock -n "$LOCKFILE" python mumc.py
then
    echo "MUMC already running..."
    echo "Wait for it to finish before trying to run again."
    exit 1
fi