#!/bin/bash
# Script para verificar estado de Auto-Sync

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.auto_sync.pid"
LOG_FILE="$SCRIPT_DIR/logs/auto_sync.log"

echo "═══════════════════════════════════════════════════════"
echo "  AUTO-SYNC STATUS"
echo "═══════════════════════════════════════════════════════"
echo ""

if [ ! -f "$PID_FILE" ]; then
    echo "❌ Estado: NO CORRIENDO"
    echo ""
    echo "Para iniciar: ./start_auto_sync.sh"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ Estado: CORRIENDO"
    echo "   PID: $PID"

    # Calcular uptime
    if [ -f "/proc/$PID/stat" ]; then
        START_TIME=$(stat -c %Y "/proc/$PID")
        CURRENT_TIME=$(date +%s)
        UPTIME=$((CURRENT_TIME - START_TIME))
        HOURS=$((UPTIME / 3600))
        MINUTES=$(((UPTIME % 3600) / 60))
        echo "   Uptime: ${HOURS}h ${MINUTES}m"
    fi

    # Mostrar últimas líneas del log
    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo "📋 Últimas 10 líneas del log:"
        echo "───────────────────────────────────────────────────────"
        tail -n 10 "$LOG_FILE"
    fi
else
    echo "❌ Estado: NO CORRIENDO (PID stale: $PID)"
    rm "$PID_FILE"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "Comandos:"
echo "  Ver logs:  tail -f $LOG_FILE"
echo "  Detener:   ./stop_auto_sync.sh"
echo "  Iniciar:   ./start_auto_sync.sh"
echo "═══════════════════════════════════════════════════════"
