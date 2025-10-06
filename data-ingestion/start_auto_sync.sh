#!/bin/bash
# Script para iniciar Auto-Sync en background

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.auto_sync.pid"
LOG_FILE="$SCRIPT_DIR/logs/auto_sync.log"

# Crear directorio de logs si no existe
mkdir -p "$SCRIPT_DIR/logs"

# Verificar si ya está corriendo
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  Auto-Sync ya está corriendo (PID: $PID)"
        echo "   Para detenerlo: ./stop_auto_sync.sh"
        exit 1
    else
        # PID file existe pero proceso no, limpiar
        rm "$PID_FILE"
    fi
fi

# Parsear argumentos
INTERVAL=60  # Default: cada 60 minutos

while [[ $# -gt 0 ]]; do
    case $1 in
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        -h|--help)
            echo "Uso: $0 [--interval MINUTOS]"
            echo ""
            echo "Opciones:"
            echo "  --interval MINUTOS   Intervalo entre sincronizaciones (default: 60)"
            echo "  -h, --help           Mostrar esta ayuda"
            exit 0
            ;;
        *)
            echo "Opción desconocida: $1"
            exit 1
            ;;
    esac
done

echo "🚀 Iniciando Auto-Sync en background..."
echo "   Intervalo: $INTERVAL minutos"
echo "   Log: $LOG_FILE"

# Iniciar el proceso en background
nohup python3 "$SCRIPT_DIR/scripts/auto_sync.py" --interval "$INTERVAL" > "$LOG_FILE" 2>&1 &
PID=$!

# Guardar PID
echo "$PID" > "$PID_FILE"

echo "✅ Auto-Sync iniciado (PID: $PID)"
echo ""
echo "Comandos útiles:"
echo "  Ver logs:     tail -f $LOG_FILE"
echo "  Detener:      ./stop_auto_sync.sh"
echo "  Estado:       ./status_auto_sync.sh"
