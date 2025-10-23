# Guía de Configuración: Ingesta de Datos en Producción

## 🏗️ Arquitectura de Infraestructura

```
┌─────────────────────────────────────────────────────────────────┐
│                     AWS Load Balancer                            │
│        LB-Prod-308585431.us-east-1.elb.amazonaws.com            │
│                                                                   │
│  Distribuye peticiones entre ambas máquinas de producción       │
└────────────────────┬────────────────────┬───────────────────────┘
                     │                    │
         ┌───────────▼──────────┐  ┌──────▼──────────────┐
         │  Producción 1        │  │  Producción 2       │
         │  54.161.1.30         │  │  52.200.140.111     │
         │                      │  │                     │
         │  - ms-passengers     │  │  - ms-passengers    │
         │  - ms-trips          │  │  - ms-trips         │
         │  - ms-tickets        │  │  - ms-tickets       │
         │  - ms-history        │  │  - ms-history       │
         │  - ms-analytics      │  │  - ms-analytics     │
         │  - web-portal        │  │  - web-portal       │
         └──────────────────────┘  └─────────────────────┘
                     ▲                    ▲
                     │                    │
                     └────────┬───────────┘
                              │
                     ┌────────▼──────────┐
                     │  Ingesta          │
                     │  52.73.204.244    │
                     │                   │
                     │  Extrae datos     │
                     │  via Load         │
                     │  Balancer         │
                     └────────┬──────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   AWS S3        │
                     │   Data Lake     │
                     │                 │
                     │  bus-mvp-       │
                     │  datalake-1     │
                     └─────────────────┘
```

## 📋 Resumen de Configuración

### Máquinas en Producción

| Máquina | IP Pública | Rol |
|---------|------------|-----|
| **Producción 1** | `54.161.1.30` | Microservicios + Frontend |
| **Producción 2** | `52.200.140.111` | Microservicios + Frontend |
| **Ingesta** | `52.73.204.244` | Ingesta de datos a S3 |
| **Load Balancer** | `LB-Prod-308585431.us-east-1.elb.amazonaws.com` | Balanceador de carga |

### Puertos de Microservicios

| Servicio | Puerto |
|----------|--------|
| ms-passengers | 8001 |
| ms-trips | 8002 |
| ms-tickets | 8003 |
| ms-history | 8004 |
| ms-analytics | 8005 |
| web-portal | 5173 |

## 🚀 Configuración Paso a Paso

### PASO 1: Configurar Máquinas de Producción (YA COMPLETADO)

En ambas máquinas de producción (`54.161.1.30` y `52.200.140.111`):

✅ **Archivo `.env` principal** configurado para usar Load Balancer:
```bash
# Ubicación: /root/bus-mvp/.env

VITE_PASSENGERS_API=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8001
VITE_TRIPS_API=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8002
VITE_TICKETS_API=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8003
VITE_HISTORY_API=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8004
VITE_ANALYTICS_API=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8005

PASSENGERS_API_URL=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8001/api/v1
TRIPS_API_URL=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8002/api/v1
TICKETS_API_URL=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8003/api/v1
```

✅ **Frontend configurado** en `frontend/web-portal/.env`

✅ **Vite configurado** para permitir conexiones desde todas las IPs en `frontend/web-portal/vite.config.ts`

### PASO 2: Configurar Máquina de Ingesta

#### 2.1. Conectarse a la máquina de ingesta

```bash
ssh -i <tu-clave.pem> ubuntu@52.73.204.244
# o
ssh -i <tu-clave.pem> ec2-user@52.73.204.244
```

#### 2.2. Clonar el repositorio (si no existe)

```bash
cd /root
git clone <url-del-repo> bus-mvp
cd bus-mvp
```

#### 2.3. Ejecutar el script de configuración

```bash
cd /root/bus-mvp/data-ingestion
bash setup_ingestion_machine.sh
```

Este script:
- ✅ Verifica que estás en la máquina de ingesta
- ✅ Crea/actualiza el archivo `.env` con las URLs del Load Balancer
- ✅ Verifica conectividad con el Load Balancer
- ✅ Muestra instrucciones para los próximos pasos

#### 2.4. Actualizar credenciales de AWS (IMPORTANTE)

Las credenciales de AWS Academy **expiran cada pocas horas**. Debes actualizarlas:

```bash
cd /root/bus-mvp/data-ingestion
bash setup_aws_academy.sh
```

Sigue las instrucciones del script para copiar tus credenciales desde AWS Academy Learner Lab.

#### 2.5. Ejecutar la ingesta

```bash
cd /root/bus-mvp/data-ingestion
docker-compose up -d
```

#### 2.6. Verificar que la ingesta está funcionando

```bash
# Ver logs de cada servicio
docker logs -f passengers-ingestion
docker logs -f trips-ingestion
docker logs -f tickets-ingestion

# Ver todos los contenedores
docker-compose ps
```

#### 2.7. (Opcional) Configurar auto-sincronización

Para que la ingesta se ejecute automáticamente cada 5 minutos:

```bash
cd /root/bus-mvp/data-ingestion
bash start_auto_sync.sh

# Ver estado
bash status_auto_sync.sh

# Detener auto-sync
bash stop_auto_sync.sh
```

## 🔍 Verificación y Troubleshooting

### Verificar conectividad desde la máquina de ingesta

```bash
# Test Load Balancer - Passengers API
curl http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8001/api/v1/passengers?page=1&limit=1

# Test Load Balancer - Trips API
curl http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8002/api/v1/trips

# Test Load Balancer - Tickets API
curl http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8003/api/v1/tickets
```

### Problemas comunes

#### 1. **Error: Connection timeout al Load Balancer**

**Causa**: Security Groups no permiten tráfico desde la IP de ingesta.

**Solución**:
- Ve a AWS Console → EC2 → Load Balancers
- Selecciona tu Load Balancer
- Ve a Security Groups
- Agrega regla de entrada:
  - Type: Custom TCP
  - Port Range: 8001-8005
  - Source: `52.73.204.244/32` (IP de ingesta)

#### 2. **Error: AWS credentials expired**

**Causa**: Las credenciales de AWS Academy expiraron.

**Solución**:
```bash
cd /root/bus-mvp/data-ingestion
bash setup_aws_academy.sh
```

#### 3. **Error: Cannot upload to S3**

**Causa**: Credenciales incorrectas o bucket no existe.

**Solución**:
```bash
# Verificar credenciales
aws s3 ls s3://bus-mvp-datalake-1/

# Re-configurar credenciales
bash setup_aws_academy.sh
```

#### 4. **Error: 404 Not Found en APIs**

**Causa**: Los microservicios no están ejecutándose en las máquinas de producción.

**Solución**: En cada máquina de producción:
```bash
cd /root/bus-mvp
docker-compose ps  # Verificar que todos están running
docker-compose up -d  # Iniciar si no están corriendo
```

## 📊 Monitoreo de la Ingesta

### Ver archivos ingresados en S3

```bash
# Listar archivos de passengers
aws s3 ls s3://bus-mvp-datalake-1/raw/passengers_csv/
aws s3 ls s3://bus-mvp-datalake-1/raw/passengers_json/

# Listar archivos de trips
aws s3 ls s3://bus-mvp-datalake-1/raw/trips_csv/
aws s3 ls s3://bus-mvp-datalake-1/raw/trips_json/

# Listar archivos de tickets
aws s3 ls s3://bus-mvp-datalake-1/raw/tickets_csv/
aws s3 ls s3://bus-mvp-datalake-1/raw/tickets_json/
```

### Ver logs en tiempo real

```bash
cd /root/bus-mvp/data-ingestion

# Ver todos los logs
docker-compose logs -f

# Ver logs de un servicio específico
docker logs -f passengers-ingestion
```

### Ver logs guardados

```bash
cd /root/bus-mvp/data-ingestion/logs
ls -lh
cat auto_sync_*.log
```

## 🔄 Flujo de Datos Completo

```
1. Frontend (Usuario) → Load Balancer → Producción 1 o 2 → Base de Datos
   └─> Usuario crea/modifica datos en el sistema

2. Máquina de Ingesta (cada 5 min o manual)
   └─> Consulta Load Balancer → APIs de Producción
       └─> Extrae 100% de datos
           └─> Transforma a CSV/JSON
               └─> Carga a S3

3. AWS Glue Crawler (automático)
   └─> Lee archivos en S3
       └─> Crea/actualiza tablas en Glue Data Catalog

4. AWS Athena
   └─> Consulta datos usando Glue Catalog
       └─> Analytics API consulta Athena
           └─> Frontend muestra analytics
```

## 📝 Comandos Útiles de Referencia

### En Máquina de Producción

```bash
# Ver servicios corriendo
docker-compose ps

# Reiniciar todos los servicios
docker-compose restart

# Ver logs
docker-compose logs -f

# Rebuild y restart
docker-compose up -d --build
```

### En Máquina de Ingesta

```bash
# Ejecutar ingesta manual (una vez)
cd /root/bus-mvp/data-ingestion
docker-compose up

# Ejecutar ingesta en background
docker-compose up -d

# Ver estado de auto-sync
bash status_auto_sync.sh

# Detener todo
docker-compose down
bash stop_auto_sync.sh
```

### AWS CLI

```bash
# Ver contenido de S3
aws s3 ls s3://bus-mvp-datalake-1/ --recursive

# Descargar archivo de S3
aws s3 cp s3://bus-mvp-datalake-1/raw/passengers_csv/passengers_20241023_120000.csv .

# Ver Glue Databases
aws glue get-databases

# Ver Glue Tables
aws glue get-tables --database-name bus_mvp_db
```

## 🎯 Checklist Final

### Máquinas de Producción (54.161.1.30 y 52.200.140.111)

- [x] Archivo `.env` configurado con Load Balancer URLs
- [x] Frontend `.env` configurado con Load Balancer URLs
- [x] `vite.config.ts` permite conexiones desde todas las IPs
- [ ] Microservicios ejecutándose (`docker-compose ps`)
- [ ] Security Groups permiten tráfico desde IP de ingesta
- [ ] Security Groups permiten tráfico del Load Balancer

### Máquina de Ingesta (52.73.204.244)

- [ ] Repositorio clonado en `/root/bus-mvp`
- [ ] Script de configuración ejecutado (`setup_ingestion_machine.sh`)
- [ ] Credenciales de AWS actualizadas
- [ ] Conectividad con Load Balancer verificada
- [ ] Docker y Docker Compose instalados
- [ ] Ingesta ejecutándose correctamente
- [ ] (Opcional) Auto-sync configurado

### AWS

- [ ] Security Groups del Load Balancer permiten tráfico desde ingesta
- [ ] Security Groups de instancias EC2 permiten tráfico del Load Balancer
- [ ] Bucket S3 `bus-mvp-datalake-1` existe
- [ ] Credenciales de AWS Academy activas
- [ ] Glue Crawlers configurados (opcional)

## 📞 Soporte

Si encuentras problemas:

1. Verifica los logs: `docker-compose logs -f`
2. Verifica conectividad: `curl http://LB-Prod-...`
3. Verifica credenciales: `aws s3 ls`
4. Revisa Security Groups en AWS Console

---

**Última actualización**: 2025-10-23
**Versión**: 1.0
**Autor**: Claude Code
