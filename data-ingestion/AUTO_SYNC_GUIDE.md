# 🔄 Auto-Sync - Sincronización Automática de Datos

## ¿Qué es Auto-Sync?

Auto-Sync es un sistema automatizado que mantiene sincronizados los datos entre tus microservicios, S3 y AWS Glue, permitiendo que los datos creados desde el frontend estén disponibles automáticamente en Athena para análisis.

## ¿Cómo funciona?

```
Frontend → API → Database
                    ↓
            (Auto-Sync cada X minutos)
                    ↓
         1. Ingesta de datos → S3
         2. Ejecuta Crawlers → Glue Catalog
         3. Tablas actualizadas → Athena
```

## 🚀 Inicio Rápido

### 1. Iniciar Auto-Sync

```bash
cd /root/bus-mvp/data-ingestion

# Sincronizar cada 60 minutos (default)
./start_auto_sync.sh

# O especificar intervalo personalizado (en minutos)
./start_auto_sync.sh --interval 30   # Cada 30 minutos
./start_auto_sync.sh --interval 5    # Cada 5 minutos
```

### 2. Verificar Estado

```bash
./status_auto_sync.sh
```

Verás:
- ✅ Si está corriendo
- PID del proceso
- Uptime
- Últimas 10 líneas del log

### 3. Ver Logs en Tiempo Real

```bash
tail -f logs/auto_sync.log
```

### 4. Detener Auto-Sync

```bash
./stop_auto_sync.sh
```

## 📋 Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `./start_auto_sync.sh` | Inicia sincronización automática |
| `./start_auto_sync.sh --interval 30` | Inicia con intervalo personalizado |
| `./status_auto_sync.sh` | Verifica si está corriendo |
| `./stop_auto_sync.sh` | Detiene la sincronización |
| `tail -f logs/auto_sync.log` | Ver logs en vivo |

## 🔧 Configuración Recomendada

### Para Desarrollo
```bash
# Sincronizar cada 5-10 minutos
./start_auto_sync.sh --interval 5
```

### Para Producción
```bash
# Sincronizar cada 60 minutos
./start_auto_sync.sh --interval 60
```

### Para Demos/Testing
```bash
# Sincronizar cada 1-2 minutos
./start_auto_sync.sh --interval 1
```

## 📊 ¿Qué hace cada ciclo?

Cada vez que se ejecuta un ciclo de sincronización:

1. **Ingesta de Datos** (2-3 minutos)
   - Extrae datos de `ms-passengers`
   - Extrae datos de `ms-trips`
   - Extrae datos de `ms-tickets`
   - Sube todo a S3 en formato CSV y JSON

2. **Ejecuta Crawlers** (1-2 minutos)
   - Inicia `passengers-crawler`
   - Inicia `trips-crawler`
   - Inicia `tickets-crawler`
   - Espera a que terminen

3. **Actualiza Catálogo**
   - Las tablas en Glue se actualizan con nuevos datos
   - Athena puede consultar los datos inmediatamente

**Tiempo total por ciclo:** ~3-5 minutos

## 🎯 Casos de Uso

### Caso 1: Desarrollo activo
```bash
# El usuario está creando datos desde el frontend frecuentemente
./start_auto_sync.sh --interval 5
```

### Caso 2: Aplicación en producción
```bash
# Los datos se crean a lo largo del día, sincronizar cada hora
./start_auto_sync.sh --interval 60
```

### Caso 3: Demo o presentación
```bash
# Quieres que los datos aparezcan rápido en Athena
./start_auto_sync.sh --interval 2
```

## 🔍 Solución de Problemas

### El Auto-Sync no inicia

1. Verificar que Docker esté corriendo:
   ```bash
   docker ps
   ```

2. Verificar credenciales AWS:
   ```bash
   aws sts get-caller-identity
   ```

3. Ver errores en el log:
   ```bash
   cat logs/auto_sync.log
   ```

### El Auto-Sync se detiene solo

1. Ver el log completo:
   ```bash
   cat logs/auto_sync.log
   ```

2. Verificar que los microservicios estén corriendo:
   ```bash
   docker ps | grep ms-
   ```

3. Reiniciar:
   ```bash
   ./stop_auto_sync.sh
   ./start_auto_sync.sh
   ```

### Los datos no aparecen en Athena

1. Verificar que Auto-Sync esté corriendo:
   ```bash
   ./status_auto_sync.sh
   ```

2. Esperar a que termine un ciclo completo (~5 minutos)

3. Verificar tablas en Glue:
   ```bash
   python3 scripts/check_crawlers.py
   ```

## 🛠️ Ejecución Manual (Sin Auto-Sync)

Si prefieres ejecutar sincronización manualmente:

```bash
# Ejecutar solo una vez
python3 scripts/auto_sync.py --once

# O usar el pipeline completo
./run_all.sh
```

## 📌 Notas Importantes

- ✅ **Auto-Sync corre en background** - No necesitas mantener la terminal abierta
- ✅ **Logs persistentes** - Todos los logs se guardan en `logs/auto_sync.log`
- ✅ **Reinicio automático** - Si un ciclo falla, el siguiente ciclo se ejecutará normalmente
- ⚠️ **Costo AWS** - Cada ejecución de crawler consume recursos AWS (mínimo en AWS Academy)
- ⚠️ **Intervalo mínimo recomendado** - 5 minutos (para evitar throttling)

## 🎓 Flujo Completo de Trabajo

```bash
# 1. Iniciar microservicios (si no están corriendo)
cd /root/bus-mvp
docker-compose up -d

# 2. Iniciar Auto-Sync
cd data-ingestion
./start_auto_sync.sh --interval 10

# 3. Usar tu frontend para crear datos
# (Los datos se sincronizan automáticamente cada 10 minutos)

# 4. Consultar datos en Athena
# https://console.aws.amazon.com/athena/

# 5. Detener cuando termines
./stop_auto_sync.sh
```

## 🚦 Indicadores en el Log

- `📋` - Información general
- `✅` - Operación exitosa
- `⚠️` - Advertencia
- `❌` - Error
- `🔄` - Sincronización en progreso

## ❓ Preguntas Frecuentes

### ¿Cuánto tarda cada sincronización?
Entre 3-5 minutos dependiendo de la cantidad de datos.

### ¿Puedo cambiar el intervalo sin reiniciar?
No, debes detener y volver a iniciar con el nuevo intervalo:
```bash
./stop_auto_sync.sh
./start_auto_sync.sh --interval 15
```

### ¿Qué pasa si se cae el servidor?
Al reiniciar el servidor, debes volver a ejecutar `./start_auto_sync.sh`

### ¿Consume muchos recursos?
No mientras está esperando. Solo consume recursos durante los 3-5 minutos de sincronización activa.

### ¿Puedo ver qué está haciendo en tiempo real?
Sí, usa `tail -f logs/auto_sync.log`

---

**¿Necesitas ayuda?** Revisa el log en `logs/auto_sync.log` o ejecuta `./status_auto_sync.sh`
