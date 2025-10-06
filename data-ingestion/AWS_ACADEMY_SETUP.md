# 🎓 Configuración para AWS Academy Lab

Esta guía está específicamente diseñada para trabajar con **AWS Academy Learner Lab**.

## 🔐 Obtener Credenciales de AWS Academy

### Paso 1: Iniciar el Lab

1. Accede a tu curso de AWS Academy
2. Ve a **Modules** → **Learner Lab**
3. Click en **Start Lab** (espera a que el círculo se ponga verde ✅)

### Paso 2: Obtener Credenciales Temporales

1. Click en **AWS Details** (arriba a la derecha)
2. Click en **Show** junto a "AWS CLI:"
3. Verás algo como:

```ini
[default]
aws_access_key_id=ASIAV...
aws_secret_access_key=wJalr...
aws_session_token=IQoJb3JpZ2luX2VjEH...
```

### Paso 3: Copiar al Archivo .env

```bash
cd data-ingestion

# Crear archivo .env desde el ejemplo
cp .env.example .env

# Editar el archivo
nano .env
```

Pega las credenciales:

```env
# AWS Credentials - AWS Academy Lab
AWS_ACCESS_KEY_ID=ASIAV... # Copiar de AWS Details
AWS_SECRET_ACCESS_KEY=wJalr... # Copiar de AWS Details
AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjEH... # ¡IMPORTANTE! Copiar de AWS Details
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration
S3_BUCKET=bus-mvp-datalake-1

# Microservices URLs
PASSENGERS_API_URL=http://host.docker.internal:3001/api
TRIPS_API_URL=http://host.docker.internal:3002/api
TICKETS_API_URL=http://host.docker.internal:3003/api

# Glue Configuration
GLUE_DATABASE=bus_mvp_db

# Athena Configuration
ATHENA_OUTPUT_LOCATION=s3://bus-mvp-datalake-1/athena-results/
```

## ⚠️ Limitaciones de AWS Academy Lab

### Presupuesto
- **$100 USD** de crédito
- Monitorea el uso en el dashboard

### Servicios Disponibles
- ✅ **S3**: Totalmente disponible
- ✅ **Glue**: Disponible (puede tener límites)
- ✅ **Athena**: Disponible
- ⚠️ **EC2**: Limitado (no todos los tipos de instancia)
- ❌ **IAM Roles**: Limitado (usa credenciales temporales)

### Sesión Temporal
- ⏰ La sesión expira después de **4 horas**
- 🔄 Necesitas renovar credenciales cuando expire

## 🔄 Renovar Credenciales (Cada 4 horas)

Cuando veas errores como:
```
ExpiredToken: The security token included in the request is expired
```

Sigue estos pasos:

```bash
# 1. Detener servicios si están corriendo
docker-compose down

# 2. Ir a AWS Academy y obtener nuevas credenciales
# AWS Details → Show → Copiar nuevas credenciales

# 3. Actualizar archivo .env
nano .env
# Pegar NUEVOS valores de:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - AWS_SESSION_TOKEN

# 4. Reiniciar servicios
docker-compose up
```

## 🚀 Setup Rápido para AWS Academy

### Opción 1: Setup Automático

```bash
# Ejecutar script de setup
./quick_start.sh
```

### Opción 2: Setup Manual

```bash
# 1. Configurar credenciales
cp .env.example .env
nano .env  # Pegar credenciales de AWS Academy

# 2. Crear bucket S3
python3 scripts/setup_s3.py

# 3. Build contenedores
docker-compose build

# 4. Ejecutar ingesta
docker-compose up passengers-ingestion trips-ingestion tickets-ingestion

# 5. Verificar datos en S3
aws s3 ls s3://bus-mvp-datalake-1/raw/ --recursive

# 6. Configurar Glue (después de tener datos en S3)
python3 scripts/setup_glue.py
```

## 🪣 Crear Bucket S3 en AWS Academy

### Opción A: Usando Script Python

```bash
# Instalar dependencias
pip3 install boto3

# Ejecutar script
python3 scripts/setup_s3.py
```

### Opción B: Usando AWS CLI

```bash
# Crear bucket
aws s3 mb s3://bus-mvp-datalake-1

# Crear estructura de carpetas
aws s3api put-object --bucket bus-mvp-datalake-1 --key raw/passengers/
aws s3api put-object --bucket bus-mvp-datalake-1 --key raw/trips/
aws s3api put-object --bucket bus-mvp-datalake-1 --key raw/tickets/
aws s3api put-object --bucket bus-mvp-datalake-1 --key athena-results/
```

### Opción C: Usando Console Web

1. Ir a **AWS Console** (click en "AWS" en AWS Academy)
2. Buscar servicio **S3**
3. Click **Create bucket**
4. Nombre: `bus-mvp-datalake-1`
5. Region: `us-east-1`
6. Dejar resto por defecto
7. Click **Create bucket**

## 📊 Configurar AWS Glue

⚠️ **IMPORTANTE**: En AWS Academy Lab, NO necesitas crear IAM Roles manualmente.

### Modificar script setup_glue.py

```bash
nano scripts/setup_glue.py
```

Busca la línea:
```python
self.role_arn = 'arn:aws:iam::YOUR_ACCOUNT_ID:role/AWSGlueServiceRole'
```

Reemplaza con el ARN del Lab Role:
```python
self.role_arn = 'arn:aws:iam::YOUR_ACCOUNT_ID:role/LabRole'
```

Para obtener tu Account ID:
```bash
aws sts get-caller-identity --query Account --output text
```

### Ejecutar Setup de Glue

```bash
python3 scripts/setup_glue.py
```

## 🔍 Verificar Todo Funciona

```bash
# 1. Verificar credenciales
aws sts get-caller-identity

# Deberías ver algo como:
# {
#     "UserId": "AIDAI...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:sts::123456789012:assumed-role/voclabs/user..."
# }

# 2. Verificar acceso a S3
aws s3 ls

# Deberías ver tu bucket: bus-mvp-datalake-1

# 3. Verificar Glue
aws glue get-database --name bus_mvp_db

# 4. Test de ingesta
docker-compose up passengers-ingestion
```

## 💰 Optimizar Costos en AWS Academy

### S3
- ✅ Solo guarda datos necesarios
- ✅ Elimina archivos antiguos si no los necesitas
- ✅ No uses versioning (cuesta más)

### Glue
- ✅ Ejecuta crawlers solo cuando sea necesario
- ✅ No dejes crawlers corriendo en loop

### Athena
- ✅ Optimiza queries (usa LIMIT)
- ✅ No hagas SELECT * en tablas grandes
- ✅ Particiona datos si es posible

### Limpiar Recursos

```bash
# Detener todos los contenedores
docker-compose down

# Eliminar archivos de S3 (si ya no los necesitas)
aws s3 rm s3://bus-mvp-datalake-1/raw/ --recursive

# Eliminar bucket S3 (al final del proyecto)
aws s3 rb s3://bus-mvp-datalake-1 --force

# Eliminar database de Glue
aws glue delete-database --name bus_mvp_db
```

## 🎯 Checklist de Setup para AWS Academy

- [ ] Lab iniciado (círculo verde)
- [ ] Credenciales copiadas (incluyendo SESSION_TOKEN)
- [ ] Archivo `.env` configurado
- [ ] Bucket S3 creado
- [ ] Microservicios corriendo localmente
- [ ] Contenedores de ingesta ejecutados
- [ ] Datos verificados en S3
- [ ] Glue database creada
- [ ] Crawlers ejecutados
- [ ] Consultas en Athena funcionando

## 🐛 Troubleshooting AWS Academy

### Error: ExpiredToken
```bash
# Solución: Renovar credenciales en .env
# 1. AWS Details → Show → Copiar nuevas credenciales
# 2. Actualizar .env
# 3. Reiniciar servicios
```

### Error: Access Denied
```bash
# Verificar que incluiste AWS_SESSION_TOKEN
cat .env | grep SESSION_TOKEN

# Si no está, agregarlo
nano .env
```

### Error: Region not supported
```bash
# AWS Academy solo permite us-east-1
# Verificar en .env:
AWS_DEFAULT_REGION=us-east-1
```

### Error: Cannot create IAM Role
```bash
# En AWS Academy usa el LabRole existente
# No intentes crear nuevos roles IAM
```

## 📝 Ejemplo Completo de .env para AWS Academy

```env
# AWS Credentials - AWS Academy Lab (Renovar cada 4 horas)
AWS_ACCESS_KEY_ID=ASIAVQWDXRFG6K3EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjEHwaCXVzLWVhc3QtMSJHMEUCIQDExampleTokenVeryLongString...
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration
S3_BUCKET=bus-mvp-datalake-1

# Microservices URLs (ajustar según tu setup)
PASSENGERS_API_URL=http://host.docker.internal:3001/api
TRIPS_API_URL=http://host.docker.internal:3002/api
TICKETS_API_URL=http://host.docker.internal:3003/api

# Glue Configuration
GLUE_DATABASE=bus_mvp_db

# Athena Configuration
ATHENA_OUTPUT_LOCATION=s3://bus-mvp-datalake-1/athena-results/

# Ingestion Schedule (optional)
INGESTION_INTERVAL=3600
```

## ⏰ Recordatorios Importantes

1. 🔄 **Renovar credenciales cada 4 horas**
2. 💰 **Monitorear presupuesto de $100**
3. 🧹 **Limpiar recursos al terminar**
4. 📊 **Usar LIMIT en queries de Athena**
5. ⏸️ **Detener Lab cuando no lo uses** (para ahorrar tiempo)

---

**¡Listo!** Ahora puedes trabajar con AWS Academy Lab sin problemas. 🚀
