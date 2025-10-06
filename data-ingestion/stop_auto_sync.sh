#!/bin/bash
# Script para detener Auto-Sync

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.auto_sync.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  Auto-Sync no está corriendo"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "🛑 Deteniendo Auto-Sync (PID: $PID)..."
    kill "$PID"

    # Esperar a que termine
    sleep 2

    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  Proceso no respondió, forzando..."
        kill -9 "$PID"
    fi

    rm "$PID_FILE"
    echo "✅ Auto-Sync detenido"
else
    echo "⚠️  Proceso no encontrado (PID: $PID)"
    rm "$PID_FILE"
fi
