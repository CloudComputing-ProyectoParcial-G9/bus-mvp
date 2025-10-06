#!/bin/bash
# Script para configurar Auto-Sync para que inicie automáticamente

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Auto-Sync - Configuración de Inicio Automático       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Selecciona el método de inicio automático:"
echo ""
echo "1) Systemd Service (Recomendado)"
echo "   - Se inicia automáticamente al arrancar el servidor"
echo "   - No requiere login"
echo "   - Más profesional"
echo ""
echo "2) Cron @reboot"
echo "   - Se inicia automáticamente al arrancar el servidor"
echo "   - Simple y ligero"
echo ""
echo "3) Solo recordatorio en .bashrc"
echo "   - Te recuerda ejecutarlo cuando haces login"
echo "   - Debes iniciarlo manualmente"
echo ""
read -p "Opción (1/2/3): " option

case $option in
    1)
        echo ""
        echo "📝 Creando servicio systemd..."

        # Crear archivo de servicio
        sudo tee /etc/systemd/system/bus-mvp-autosync.service > /dev/null <<EOF
[Unit]
Description=Bus MVP Auto-Sync Service
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/bus-mvp/data-ingestion
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/usr/bin/python3 /root/bus-mvp/data-ingestion/scripts/auto_sync.py --interval 10
Restart=always
RestartSec=10
StandardOutput=append:/root/bus-mvp/data-ingestion/logs/auto_sync.log
StandardError=append:/root/bus-mvp/data-ingestion/logs/auto_sync.log

[Install]
WantedBy=multi-user.target
EOF

        # Recargar systemd
        sudo systemctl daemon-reload

        # Habilitar servicio
        sudo systemctl enable bus-mvp-autosync.service

        echo "✅ Servicio creado y habilitado"
        echo ""
        echo "Comandos útiles:"
        echo "  Iniciar:  sudo systemctl start bus-mvp-autosync"
        echo "  Detener:  sudo systemctl stop bus-mvp-autosync"
        echo "  Estado:   sudo systemctl status bus-mvp-autosync"
        echo "  Logs:     journalctl -u bus-mvp-autosync -f"
        echo ""
        read -p "¿Iniciar el servicio ahora? (y/N): " start_now
        if [[ "$start_now" =~ ^[Yy]$ ]]; then
            sudo systemctl start bus-mvp-autosync
            echo "✅ Servicio iniciado"
        fi
        ;;

    2)
        echo ""
        echo "📝 Configurando cron @reboot..."

        # Agregar a crontab si no existe
        (crontab -l 2>/dev/null | grep -v bus-mvp-autosync; echo "@reboot cd /root/bus-mvp/data-ingestion && ./start_auto_sync.sh --interval 10") | crontab -

        echo "✅ Cron job configurado"
        echo ""
        echo "Auto-Sync se iniciará automáticamente al reiniciar el servidor"
        echo ""
        read -p "¿Iniciar Auto-Sync ahora? (y/N): " start_now
        if [[ "$start_now" =~ ^[Yy]$ ]]; then
            cd /root/bus-mvp/data-ingestion
            ./start_auto_sync.sh --interval 10
        fi
        ;;

    3)
        echo ""
        echo "📝 Agregando recordatorio a .bashrc..."

        # Agregar recordatorio a .bashrc
        if ! grep -q "bus-mvp-autosync-reminder" ~/.bashrc; then
            cat >> ~/.bashrc <<'EOF'

# Bus MVP Auto-Sync Reminder
if [ -f /root/bus-mvp/data-ingestion/.auto_sync.pid ]; then
    PID=$(cat /root/bus-mvp/data-ingestion/.auto_sync.pid)
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  Auto-Sync no está corriendo"
        echo "   Para iniciar: cd /root/bus-mvp/data-ingestion && ./start_auto_sync.sh"
    fi
else
    echo "💡 Tip: Auto-Sync no está corriendo" # bus-mvp-autosync-reminder
    echo "   Para iniciar: cd /root/bus-mvp/data-ingestion && ./start_auto_sync.sh"
fi
EOF
        fi

        echo "✅ Recordatorio agregado"
        echo ""
        echo "Verás un recordatorio cada vez que hagas login"
        ;;

    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "✅ Configuración completada"
