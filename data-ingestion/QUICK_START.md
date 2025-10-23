# Quick Start - Configuración de Ingesta

## 🎯 Objetivo

Configurar la máquina de ingesta para extraer datos de las máquinas de producción (vía Load Balancer) y subirlos a S3.

## 📊 Arquitectura

```
Load Balancer (LB-Prod-308585431.us-east-1.elb.amazonaws.com)
    ↓ distribuye entre
Producción 1 (54.161.1.30) + Producción 2 (52.200.140.111)
    ↑ consulta desde
Máquina de Ingesta (52.73.204.244)
    ↓ sube datos a
AWS S3 (bus-mvp-datalake-1)
```

## 🚀 Setup Rápido (3 pasos)

### 1. Ejecutar script de configuración

```bash
cd /root/bus-mvp/data-ingestion
bash setup_ingestion_machine.sh
```

Este script:
- ✅ Crea archivo `.env` con URLs del Load Balancer
- ✅ Verifica conectividad
- ✅ Te guía en los próximos pasos

### 2. Actualizar credenciales de AWS

```bash
bash setup_aws_academy.sh
```

**IMPORTANTE**: Las credenciales de AWS Academy expiran cada pocas horas. Debes ejecutar este comando cada vez que expiren.

### 3. Ejecutar ingesta

```bash
docker-compose up -d
```

Ver logs:
```bash
docker logs -f passengers-ingestion
docker logs -f trips-ingestion
docker logs -f tickets-ingestion
```

## 🔄 Auto-Sincronización (Opcional)

Para ejecutar la ingesta automáticamente cada 5 minutos:

```bash
bash start_auto_sync.sh    # Iniciar
bash status_auto_sync.sh   # Ver estado
bash stop_auto_sync.sh     # Detener
```

## 🔍 Verificación

### Verificar que todo está configurado correctamente:

```bash
cd /root/bus-mvp
bash verify_infrastructure.sh
```

### Verificar conectividad manualmente:

```bash
# Test Load Balancer - Passengers
curl http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8001/api/v1/passengers?page=1&limit=1

# Test Load Balancer - Trips
curl http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8002/api/v1/trips

# Test Load Balancer - Tickets
curl http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8003/tickets
```

### Verificar archivos en S3:

```bash
# Listar archivos ingresados
aws s3 ls s3://bus-mvp-datalake-1/raw/passengers_csv/
aws s3 ls s3://bus-mvp-datalake-1/raw/trips_csv/
aws s3 ls s3://bus-mvp-datalake-1/raw/tickets_csv/
```

## ⚠️ Problemas Comunes

### 1. "Connection timeout" al Load Balancer

**Solución**: Verificar Security Groups del Load Balancer para permitir tráfico desde `52.73.204.244`

### 2. "AWS credentials expired"

**Solución**:
```bash
bash setup_aws_academy.sh
```

### 3. "Cannot upload to S3"

**Solución**: Verificar credenciales y bucket:
```bash
aws s3 ls s3://bus-mvp-datalake-1/
```

### 4. "404 Not Found" en APIs

**Solución**: Verificar que microservicios estén corriendo en máquinas de producción

## 📝 Comandos Útiles

```bash
# Ver contenedores
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar ingesta
docker-compose restart

# Detener todo
docker-compose down

# Ver logs guardados
cat logs/auto_sync_*.log
```

## 📚 Documentación Completa

Para más detalles, ver: `/root/bus-mvp/INGESTION_SETUP_GUIDE.md`

## 🎉 ¡Listo!

Una vez configurado, la ingesta:
1. Consulta datos de producción vía Load Balancer
2. Extrae el 100% de registros de passengers, trips, tickets
3. Los convierte a CSV y JSON
4. Los sube a S3 en `s3://bus-mvp-datalake-1/raw/`

Los datos en S3 pueden ser consultados con Athena para analytics.
