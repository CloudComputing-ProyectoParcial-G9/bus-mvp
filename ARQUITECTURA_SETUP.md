# Guía para Configurar la Arquitectura Completa

## Arquitectura Objetivo

```
[Cliente / Usuario]
        │
        ▼
  [Load Balancer AWS Público]
  LB-Prod-308585431.us-east-1.elb.amazonaws.com
        │
 ┌──────────────────────────┐
 │   Instancia Prod 1       │
 │   (54.161.1.30)          │
 │   Frontend + Backend     │
 ├──────────────────────────┤
 │   Instancia Prod 2       │
 │   (52.200.140.111)       │
 │   Frontend + Backend     │
 └──────────────────────────┘
        │
        ▼
  [Instancia Ingesta]
  (52.73.204.244)
  (Microservicio de datos)
        │
        ▼
Data Analytics: S3, Glue y Athena
```

## Estado Actual

### ✅ Completado en Instancia Prod 1 (54.161.1.30)

- ✅ Todos los microservicios corriendo:
  - ms-passengers (Puerto 8001)
  - ms-trips (Puerto 8002)
  - ms-tickets (Puerto 8003)
  - ms-history (Puerto 8004)
  - ms-analytics (Puerto 8005)

- ✅ Todas las bases de datos funcionando:
  - PostgreSQL (passengers)
  - MySQL (trips)
  - MongoDB (tickets)

### ⚠️ Pendiente de Configurar

1. **Credenciales AWS**: Expiradas, necesitan actualización
2. **Load Balancer AWS**: Configuración de Target Groups y Listeners
3. **Instancia Prod 2**: Verificar servicios corriendo
4. **Instancia Ingesta**: Configurar y conectar al LB
5. **Data Analytics**: Verificar S3, Glue, Athena

---

## Paso 1: Actualizar Credenciales AWS Academy

Las credenciales AWS Academy expiran cada 3-4 horas. Necesitas actualizarlas regularmente.

### 1.1 Obtener Nuevas Credenciales

1. Accede a AWS Academy Learner Lab
2. Haz clic en "AWS Details"
3. Haz clic en "Show" junto a "AWS CLI"
4. Copia las credenciales que aparecen

### 1.2 Actualizar en la Instancia Prod 1

```bash
# Opción 1: Usar el script automatizado (RECOMENDADO)
cd /root/bus-mvp/data-ingestion
./setup_aws_academy.sh

# El script te pedirá pegar las credenciales
# Luego las sincronizará automáticamente
```

### 1.3 Verificar Credenciales

```bash
aws sts get-caller-identity
```

Deberías ver tu Account ID y User ARN.

---

## Paso 2: Configurar Load Balancer AWS

El Load Balancer necesita:
- Security Groups que permitan tráfico en puertos 8001-8005
- Target Groups para cada microservicio
- Listeners configurados

### 2.1 Verificar Security Groups del Load Balancer

```bash
# Obtener el ARN del Load Balancer
aws elbv2 describe-load-balancers \
  --query "LoadBalancers[?DNSName=='LB-Prod-308585431.us-east-1.elb.amazonaws.com'].{Name:LoadBalancerName,ARN:LoadBalancerArn,SG:SecurityGroups}" \
  --output table

# Guardar el Security Group ID y verificar reglas
export LB_SG_ID="sg-xxxxx"  # Reemplazar con el ID obtenido

aws ec2 describe-security-groups \
  --group-ids $LB_SG_ID \
  --query "SecurityGroups[0].IpPermissions" \
  --output table
```

### 2.2 Agregar Reglas de Ingress al Security Group

```bash
# Permitir tráfico HTTP en puertos 8001-8005
for PORT in 8001 8002 8003 8004 8005; do
  aws ec2 authorize-security-group-ingress \
    --group-id $LB_SG_ID \
    --protocol tcp \
    --port $PORT \
    --cidr 0.0.0.0/0 \
    --region us-east-1
done
```

### 2.3 Obtener IDs de las Instancias

```bash
# Obtener ID de VPC
export VPC_ID=$(aws ec2 describe-vpcs \
  --query "Vpcs[0].VpcId" \
  --output text)

# Obtener IDs de instancias
export INSTANCE_1=$(aws ec2 describe-instances \
  --filters "Name=ip-address,Values=54.161.1.30" \
  --query "Reservations[0].Instances[0].InstanceId" \
  --output text)

export INSTANCE_2=$(aws ec2 describe-instances \
  --filters "Name=ip-address,Values=52.200.140.111" \
  --query "Reservations[0].Instances[0].InstanceId" \
  --output text)

echo "Instance 1: $INSTANCE_1"
echo "Instance 2: $INSTANCE_2"
```

### 2.4 Crear Target Groups para Cada Microservicio

```bash
# Target Group para ms-passengers (puerto 8001)
aws elbv2 create-target-group \
  --name tg-passengers \
  --protocol HTTP \
  --port 8001 \
  --vpc-id $VPC_ID \
  --health-check-enabled \
  --health-check-path /api/v1/passengers \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --region us-east-1

# Target Group para ms-trips (puerto 8002)
aws elbv2 create-target-group \
  --name tg-trips \
  --protocol HTTP \
  --port 8002 \
  --vpc-id $VPC_ID \
  --health-check-enabled \
  --health-check-path /api/v1/trips \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --region us-east-1

# Target Group para ms-tickets (puerto 8003)
aws elbv2 create-target-group \
  --name tg-tickets \
  --protocol HTTP \
  --port 8003 \
  --vpc-id $VPC_ID \
  --health-check-enabled \
  --health-check-path /actuator/health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --region us-east-1

# Target Group para ms-history (puerto 8004)
aws elbv2 create-target-group \
  --name tg-history \
  --protocol HTTP \
  --port 8004 \
  --vpc-id $VPC_ID \
  --health-check-enabled \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --region us-east-1

# Target Group para ms-analytics (puerto 8005)
aws elbv2 create-target-group \
  --name tg-analytics \
  --protocol HTTP \
  --port 8005 \
  --vpc-id $VPC_ID \
  --health-check-enabled \
  --health-check-path /api/v1/analytics \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --region us-east-1
```

### 2.5 Obtener ARNs de los Target Groups

```bash
export TG_PASSENGERS_ARN=$(aws elbv2 describe-target-groups \
  --names tg-passengers \
  --query "TargetGroups[0].TargetGroupArn" \
  --output text)

export TG_TRIPS_ARN=$(aws elbv2 describe-target-groups \
  --names tg-trips \
  --query "TargetGroups[0].TargetGroupArn" \
  --output text)

export TG_TICKETS_ARN=$(aws elbv2 describe-target-groups \
  --names tg-tickets \
  --query "TargetGroups[0].TargetGroupArn" \
  --output text)

export TG_HISTORY_ARN=$(aws elbv2 describe-target-groups \
  --names tg-history \
  --query "TargetGroups[0].TargetGroupArn" \
  --output text)

export TG_ANALYTICS_ARN=$(aws elbv2 describe-target-groups \
  --names tg-analytics \
  --query "TargetGroups[0].TargetGroupArn" \
  --output text)
```

### 2.6 Registrar Instancias en los Target Groups

```bash
# Registrar ambas instancias en cada Target Group

# ms-passengers
aws elbv2 register-targets \
  --target-group-arn $TG_PASSENGERS_ARN \
  --targets Id=$INSTANCE_1 Id=$INSTANCE_2

# ms-trips
aws elbv2 register-targets \
  --target-group-arn $TG_TRIPS_ARN \
  --targets Id=$INSTANCE_1 Id=$INSTANCE_2

# ms-tickets
aws elbv2 register-targets \
  --target-group-arn $TG_TICKETS_ARN \
  --targets Id=$INSTANCE_1 Id=$INSTANCE_2

# ms-history
aws elbv2 register-targets \
  --target-group-arn $TG_HISTORY_ARN \
  --targets Id=$INSTANCE_1 Id=$INSTANCE_2

# ms-analytics
aws elbv2 register-targets \
  --target-group-arn $TG_ANALYTICS_ARN \
  --targets Id=$INSTANCE_1 Id=$INSTANCE_2
```

### 2.7 Obtener ARN del Load Balancer

```bash
export LB_ARN=$(aws elbv2 describe-load-balancers \
  --query "LoadBalancers[?DNSName=='LB-Prod-308585431.us-east-1.elb.amazonaws.com'].LoadBalancerArn" \
  --output text)

echo "Load Balancer ARN: $LB_ARN"
```

### 2.8 Crear Listeners en el Load Balancer

```bash
# Listener para puerto 8001 (ms-passengers)
aws elbv2 create-listener \
  --load-balancer-arn $LB_ARN \
  --protocol HTTP \
  --port 8001 \
  --default-actions Type=forward,TargetGroupArn=$TG_PASSENGERS_ARN

# Listener para puerto 8002 (ms-trips)
aws elbv2 create-listener \
  --load-balancer-arn $LB_ARN \
  --protocol HTTP \
  --port 8002 \
  --default-actions Type=forward,TargetGroupArn=$TG_TRIPS_ARN

# Listener para puerto 8003 (ms-tickets)
aws elbv2 create-listener \
  --load-balancer-arn $LB_ARN \
  --protocol HTTP \
  --port 8003 \
  --default-actions Type=forward,TargetGroupArn=$TG_TICKETS_ARN

# Listener para puerto 8004 (ms-history)
aws elbv2 create-listener \
  --load-balancer-arn $LB_ARN \
  --protocol HTTP \
  --port 8004 \
  --default-actions Type=forward,TargetGroupArn=$TG_HISTORY_ARN

# Listener para puerto 8005 (ms-analytics)
aws elbv2 create-listener \
  --load-balancer-arn $LB_ARN \
  --protocol HTTP \
  --port 8005 \
  --default-actions Type=forward,TargetGroupArn=$TG_ANALYTICS_ARN
```

### 2.9 Verificar Configuración

```bash
# Ver listeners
aws elbv2 describe-listeners \
  --load-balancer-arn $LB_ARN \
  --query "Listeners[*].{Port:Port,Protocol:Protocol,TargetGroup:DefaultActions[0].TargetGroupArn}" \
  --output table

# Verificar health de targets
aws elbv2 describe-target-health \
  --target-group-arn $TG_PASSENGERS_ARN

aws elbv2 describe-target-health \
  --target-group-arn $TG_TRIPS_ARN
```

---

## Paso 3: Verificar Instancia Prod 2 (52.200.140.111)

### 3.1 Conectar a la Instancia

```bash
ssh -i tu-key.pem ubuntu@52.200.140.111
```

### 3.2 Verificar Servicios

```bash
cd /root/bus-mvp
docker compose ps

# Si los servicios no están corriendo:
docker compose up -d

# Esperar a que arranquen
sleep 30

# Verificar health
docker compose ps
```

### 3.3 Verificar Endpoints

```bash
curl http://localhost:8001/api/v1/passengers
curl http://localhost:8002/api/v1/trips
curl http://localhost:8003/actuator/health
curl http://localhost:8004/health
curl http://localhost:8005/api/v1/analytics
```

### 3.4 Actualizar Security Group de las Instancias

```bash
# Obtener Security Group de las instancias
export INSTANCE_SG=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_1 \
  --query "Reservations[0].Instances[0].SecurityGroups[0].GroupId" \
  --output text)

# Permitir tráfico desde el Load Balancer
aws ec2 authorize-security-group-ingress \
  --group-id $INSTANCE_SG \
  --protocol tcp \
  --port 8001-8005 \
  --source-group $LB_SG_ID
```

---

## Paso 4: Configurar Instancia de Ingesta (52.73.204.244)

### 4.1 Conectar a la Instancia de Ingesta

```bash
ssh -i tu-key.pem ubuntu@52.73.204.244
```

### 4.2 Verificar Configuración

```bash
cd /root/bus-mvp/data-ingestion

# Verificar que el .env apunta al Load Balancer
cat .env | grep LOAD_BALANCER
cat .env | grep API_URL
```

Debería mostrar:
```
LOAD_BALANCER_DNS=LB-Prod-308585431.us-east-1.elb.amazonaws.com
PASSENGERS_API_URL=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8001/api/v1
TRIPS_API_URL=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8002/api/v1
TICKETS_API_URL=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8003/api/v1
```

### 4.3 Actualizar Credenciales AWS

```bash
# Desde la máquina de ingesta
cd /root/bus-mvp/data-ingestion
./setup_aws_academy.sh

# Pegar las credenciales cuando te lo pida
```

### 4.4 Ejecutar Setup de Ingesta

```bash
# Ejecutar script completo de setup
./run_all.sh
```

Este script:
1. Configura S3 bucket
2. Configura AWS Glue database y tablas
3. Crea vistas en Athena
4. Ejecuta ingesta inicial
5. Verifica los datos

### 4.5 Configurar Auto-sync (Opcional)

```bash
# Iniciar auto-sync cada 5 minutos
./start_auto_sync.sh

# Verificar estado
./status_auto_sync.sh
```

---

## Paso 5: Verificar Data Analytics (S3, Glue, Athena)

### 5.1 Verificar S3 Bucket

```bash
# Listar bucket
aws s3 ls s3://bus-mvp-datalake-1/

# Ver estructura
aws s3 ls s3://bus-mvp-datalake-1/raw/ --recursive
```

### 5.2 Verificar Glue Database y Tablas

```bash
# Ver databases
aws glue get-databases

# Ver tablas
aws glue get-tables --database-name bus_mvp_db
```

### 5.3 Verificar Athena

```bash
# Desde Python
cd /root/bus-mvp/data-ingestion/scripts
python3 run_athena_queries.py
```

---

## Paso 6: Pruebas End-to-End

### 6.1 Probar Load Balancer

```bash
# Desde cualquier máquina con internet
curl http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8001/api/v1/passengers
curl http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8002/api/v1/trips
curl http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8003/actuator/health
curl http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8004/health
curl http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8005/api/v1/analytics
```

### 6.2 Verificar Distribución de Tráfico

```bash
# Hacer múltiples requests y ver logs en ambas instancias
for i in {1..10}; do
  curl -s http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8001/api/v1/passengers | head -1
done

# En cada instancia ver logs
# Instancia 1:
docker logs ms-passengers -f

# Instancia 2:
docker logs ms-passengers -f
```

### 6.3 Probar Failover

```bash
# En Instancia 1, detener un servicio
docker stop ms-passengers

# Hacer requests al LB - deberían ir solo a Instancia 2
curl http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8001/api/v1/passengers

# Reiniciar servicio
docker start ms-passengers

# Verificar que vuelve a recibir tráfico
```

---

## Resumen de Scripts Útiles

### En Instancias de Producción (54.161.1.30, 52.200.140.111)

```bash
# Ver estado de servicios
docker compose ps

# Iniciar todos los servicios
docker compose up -d

# Ver logs
docker compose logs -f

# Reiniciar un servicio
docker compose restart ms-passengers

# Verificar infraestructura
./verify_infrastructure.sh
```

### En Instancia de Ingesta (52.73.204.244)

```bash
# Setup completo
cd /root/bus-mvp/data-ingestion
./run_all.sh

# Actualizar credenciales
./setup_aws_academy.sh

# Iniciar auto-sync
./start_auto_sync.sh

# Ver estado de auto-sync
./status_auto_sync.sh

# Ver logs
cat logs/auto_sync_*.log
```

---

## Troubleshooting

### Load Balancer no responde

1. Verificar Security Groups
2. Verificar Listeners configurados
3. Verificar Target Groups tienen instancias healthy
4. Verificar reglas de firewall en instancias

### Target Health = Unhealthy

1. Verificar que el servicio esté corriendo: `docker compose ps`
2. Verificar que el health check path sea correcto
3. Verificar logs del servicio: `docker logs [servicio]`
4. Verificar conectividad desde el LB a la instancia

### Credenciales AWS Expiradas

```bash
# En cualquier instancia
cd /root/bus-mvp/data-ingestion
./setup_aws_academy.sh

# Pegar nuevas credenciales de AWS Academy
```

### Servicios no arrancan

```bash
# Ver logs
docker compose logs [servicio]

# Verificar variables de entorno
cat .env

# Reiniciar desde cero
docker compose down
docker compose up -d
```

### Ingesta falla

1. Verificar credenciales AWS
2. Verificar que el Load Balancer responde
3. Verificar S3 bucket existe
4. Ver logs: `cat /root/bus-mvp/data-ingestion/logs/*.log`

---

## Próximos Pasos

1. ✅ Actualizar credenciales AWS
2. ✅ Configurar Load Balancer completamente
3. ✅ Verificar ambas instancias de producción
4. ✅ Configurar instancia de ingesta
5. ✅ Probar end-to-end

Una vez completado todo, tu arquitectura estará funcionando completamente con:
- Alta disponibilidad (2 instancias + Load Balancer)
- Ingesta automática de datos
- Data Analytics con S3, Glue y Athena
