# Guía de Despliegue - AWS EC2

Esta guía detalla cómo crear y configurar la máquina virtual de ingesta en AWS EC2.

## 📋 Prerequisitos

- Cuenta de AWS activa
- AWS CLI instalado y configurado
- Par de claves SSH (.pem)

## 🚀 Paso 1: Crear Instancia EC2

### Opción A: Usando AWS Console

1. **Ir a EC2 Dashboard**
   - Console AWS → EC2 → Instances → Launch Instance

2. **Configuración de la Instancia**
   - **Name**: `bus-mvp-ingesta-vm`
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type**: t3.medium (2 vCPU, 4 GB RAM)
   - **Key pair**: Crear o seleccionar existente
   - **Network settings**:
     - VPC: Default
     - Auto-assign public IP: Enable
     - Security group: Crear nuevo

3. **Security Group Rules**:
   ```
   Type        Protocol   Port Range   Source        Description
   SSH         TCP        22          Mi IP         SSH access
   HTTP        TCP        80          0.0.0.0/0     HTTP
   HTTPS       TCP        443         0.0.0.0/0     HTTPS
   Custom TCP  TCP        5000        0.0.0.0/0     Analytics API
   ```

4. **Storage**: 30 GB gp3

5. **Launch Instance**

### Opción B: Usando AWS CLI

```bash
# Crear Security Group
aws ec2 create-security-group \
    --group-name bus-mvp-ingesta-sg \
    --description "Security group for Bus MVP ingestion VM"

# Obtener el Security Group ID
SG_ID=$(aws ec2 describe-security-groups \
    --group-names bus-mvp-ingesta-sg \
    --query 'SecurityGroups[0].GroupId' \
    --output text)

# Agregar reglas al Security Group
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp --port 443 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp --port 5000 --cidr 0.0.0.0/0

# Lanzar instancia EC2
aws ec2 run-instances \
    --image-id ami-0c7217cdde317cfec \
    --instance-type t3.medium \
    --key-name your-key-pair-name \
    --security-group-ids $SG_ID \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":30,"VolumeType":"gp3"}}]' \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=bus-mvp-ingesta-vm}]'
```

## 🔧 Paso 2: Conectarse a la Instancia

```bash
# Obtener la IP pública
aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=bus-mvp-ingesta-vm" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text

# Conectarse vía SSH
ssh -i "your-key.pem" ubuntu@<PUBLIC_IP>
```

## 📦 Paso 3: Instalar Dependencias

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar AWS CLI
sudo apt install -y awscli

# Instalar Python y pip
sudo apt install -y python3 python3-pip

# Instalar git
sudo apt install -y git

# Reiniciar sesión para aplicar cambios de grupo
exit
# Reconectar
ssh -i "your-key.pem" ubuntu@<PUBLIC_IP>

# Verificar instalaciones
docker --version
docker-compose --version
aws --version
python3 --version
```

## 🔐 Paso 4: Configurar IAM Role (Recomendado)

### Opción A: Usando IAM Role (Más seguro)

```bash
# 1. En AWS Console, crear IAM Role
# IAM → Roles → Create role
# Trusted entity: EC2
# Permissions: 
#   - AmazonS3FullAccess
#   - AWSGlueConsoleFullAccess
#   - AmazonAthenaFullAccess

# 2. Attachar role a la instancia EC2
# EC2 → Instance → Actions → Security → Modify IAM role
# Select: bus-mvp-ingestion-role

# 3. En la VM, verificar credenciales
aws sts get-caller-identity
```

### Opción B: Usando Credenciales (Alternativa)

```bash
# Configurar AWS CLI
aws configure
# Ingresar:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Default output: json
```

## 📂 Paso 5: Clonar Repositorio

```bash
# Clonar el proyecto
cd ~
git clone https://github.com/CloudComputing-ProyectoParcial-G9/bus-mvp.git

cd bus-mvp/data-ingestion
```

## ⚙️ Paso 6: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar archivo .env
nano .env

# Configurar:
# - AWS_ACCESS_KEY_ID (si no usas IAM Role)
# - AWS_SECRET_ACCESS_KEY (si no usas IAM Role)
# - S3_BUCKET=bus-mvp-datalake
# - PASSENGERS_API_URL=http://<YOUR_BACKEND_IP>:3001/api
# - TRIPS_API_URL=http://<YOUR_BACKEND_IP>:3002/api
# - TICKETS_API_URL=http://<YOUR_BACKEND_IP>:3003/api
```

## 🪣 Paso 7: Crear Bucket S3

```bash
# Instalar boto3
pip3 install -r scripts/requirements.txt

# Ejecutar script de setup S3
python3 scripts/setup_s3.py us-east-1

# O manualmente con AWS CLI
aws s3 mb s3://bus-mvp-datalake-1 --region us-east-1

# Crear estructura de carpetas
aws s3api put-object --bucket bus-mvp-datalake-1 --key raw/passengers/
aws s3api put-object --bucket bus-mvp-datalake-1 --key raw/trips/
aws s3api put-object --bucket bus-mvp-datalake-1 --key raw/tickets/
aws s3api put-object --bucket bus-mvp-datalake-1 --key athena-results/
```

## 🐳 Paso 8: Ejecutar Contenedores de Ingesta

```bash
# Build de contenedores
docker-compose build

# Ejecutar ingesta completa
docker-compose up

# O ejecutar cada servicio individualmente
docker-compose up passengers-ingestion
docker-compose up trips-ingestion
docker-compose up tickets-ingestion

# Verificar logs
docker-compose logs -f
```

## 📊 Paso 9: Configurar AWS Glue

```bash
# Actualizar setup_glue.py con tu Account ID
nano scripts/setup_glue.py
# Cambiar: YOUR_ACCOUNT_ID por tu Account ID real

# Obtener tu Account ID
aws sts get-caller-identity --query Account --output text

# Ejecutar setup de Glue
python3 scripts/setup_glue.py us-east-1
```

## 🔍 Paso 10: Verificar Resultados

```bash
# Verificar archivos en S3
aws s3 ls s3://bus-mvp-datalake-1/raw/ --recursive

# Listar tablas en Glue
aws glue get-tables --database-name bus_mvp_db

# Ejecutar query de prueba en Athena (desde AWS Console)
# Athena → Query Editor
# Database: bus_mvp_db
# Query: SELECT COUNT(*) FROM passengers;
```

## 🚀 Paso 11: Iniciar Analytics API

```bash
# Iniciar servicio de analytics
docker-compose up -d analytics-service

# Verificar que esté corriendo
curl http://localhost:5000/health

# Desde fuera de la VM
curl http://<PUBLIC_IP>:5000/health
```

## 🔄 Automatización con Cron

```bash
# Editar crontab
crontab -e

# Agregar job para ejecutar ingesta cada hora
0 * * * * cd /home/ubuntu/bus-mvp/data-ingestion && /usr/local/bin/docker-compose up >> /var/log/ingestion.log 2>&1

# Agregar job para ejecutar ingesta diaria a las 2 AM
0 2 * * * cd /home/ubuntu/bus-mvp/data-ingestion && /usr/local/bin/docker-compose up >> /var/log/ingestion.log 2>&1
```

## 📝 Notas Importantes

1. **Costos**: Recuerda que EC2, S3, Glue y Athena tienen costos asociados
2. **Security Groups**: Restringe el acceso SSH solo a tu IP
3. **IAM Roles**: Usa IAM roles en lugar de credenciales hardcodeadas
4. **Monitoreo**: Configura CloudWatch para monitorear la instancia
5. **Backups**: Configura snapshots automáticos del volumen EBS

## 🛑 Detener/Eliminar Recursos

```bash
# Detener contenedores
docker-compose down

# Detener instancia EC2 (desde CLI)
aws ec2 stop-instances --instance-ids <INSTANCE_ID>

# Eliminar instancia EC2
aws ec2 terminate-instances --instance-ids <INSTANCE_ID>

# Eliminar bucket S3 (¡cuidado! elimina todos los datos)
aws s3 rb s3://bus-mvp-datalake-1 --force
```

## 📚 Troubleshooting

### Error: Cannot connect to Docker daemon
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
# Cerrar y volver a abrir la sesión
```

### Error: Permission denied (publickey)
```bash
# Verificar permisos del archivo .pem
chmod 400 your-key.pem
```

### Error: No space left on device
```bash
# Verificar espacio en disco
df -h

# Limpiar imágenes Docker no usadas
docker system prune -a
```

### Error: Cannot connect to microservices
```bash
# Verificar que las URLs en .env sean correctas
# Verificar que los microservicios estén corriendo
# Verificar Security Groups permitan el tráfico
```
