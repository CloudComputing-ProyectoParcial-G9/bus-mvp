# 🔐 Configuración de Credenciales AWS - ACTUALIZADO

## ⚠️ CAMBIO IMPORTANTE

**Todas las credenciales de AWS ahora están centralizadas en un solo archivo.**

### Ubicación del archivo de credenciales

```
/root/bus-mvp/.env  ← ARCHIVO ÚNICO Y CENTRALIZADO
```

Ya **NO se usa** el archivo `data-ingestion/.env`. Todas las partes del proyecto (ingesta, analytics, scripts) leen desde el archivo `.env` en la raíz.

---

## 📋 Configuración Rápida

### Opción 1: Script Automático (Recomendado)

```bash
cd /root/bus-mvp/data-ingestion
bash setup_aws_academy.sh
```

Este script:
- Te guiará paso a paso para ingresar tus credenciales
- Configurará automáticamente el archivo `/root/bus-mvp/.env`
- Verificará que las credenciales sean válidas
- Agregará el Account ID automáticamente

### Opción 2: Manual

1. Copia el archivo de ejemplo:
```bash
cd /root/bus-mvp
cp .env.example .env
```

2. Edita el archivo y agrega tus credenciales:
```bash
nano .env
```

3. Actualiza estas variables:
```bash
AWS_ACCESS_KEY_ID=tu_access_key_aquí
AWS_SECRET_ACCESS_KEY=tu_secret_key_aquí
AWS_SESSION_TOKEN=tu_session_token_aquí
AWS_DEFAULT_REGION=us-east-1
AWS_ACCOUNT_ID=tu_account_id_aquí
```

---

## 🔍 Dónde se usan las credenciales

### 1. Scripts de Python (data-ingestion/scripts/)
Todos los scripts ahora leen desde `/root/bus-mvp/.env`:
- `setup_s3.py`
- `setup_glue.py`
- `create_athena_tables.py`
- `create_athena_views.py`
- `run_athena_queries.py`
- `auto_sync.py`
- `test_athena_queries.py`
- `check_crawlers.py`

### 2. Contenedores Docker (data-ingestion/)
El `docker-compose.yml` en data-ingestion usa `env_file: ../.env`:
- `passengers-ingestion`
- `trips-ingestion`
- `tickets-ingestion`

### 3. Microservicio ms-analytics
El docker-compose principal pasa las credenciales desde `/root/bus-mvp/.env` al contenedor `ms-analytics`.

---

## ✅ Verificación

Para verificar que las credenciales están configuradas correctamente:

```bash
# Opción 1: Verificar con AWS CLI
aws sts get-caller-identity

# Opción 2: Ver las variables (sin mostrar los valores secretos)
cd /root/bus-mvp
grep -E "^AWS_|^S3_|^GLUE_|^ATHENA_" .env | sed 's/=.*/=***/'
```

---

## 🔄 Actualizar credenciales expiradas

Las credenciales de AWS Academy expiran cada 4 horas. Para actualizarlas:

```bash
cd /root/bus-mvp/data-ingestion
bash setup_aws_academy.sh
```

El script detectará que el archivo `.env` ya existe y te preguntará si quieres actualizar las credenciales.

---

## 📦 Variables requeridas en .env

### AWS Credentials
```bash
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
AWS_DEFAULT_REGION=us-east-1
AWS_ACCOUNT_ID=
```

### S3 & Data Lake
```bash
S3_BUCKET=bus-mvp-datalake-1
```

### Glue & Athena
```bash
GLUE_DATABASE=bus_mvp_db
ATHENA_OUTPUT_LOCATION=s3://bus-mvp-datalake-1/athena-results/
ATHENA_QUERY_TIMEOUT=60
```

### Data Ingestion APIs
```bash
PASSENGERS_API_URL=http://host.docker.internal:8001/api/v1
TRIPS_API_URL=http://host.docker.internal:8002/api/v1
TICKETS_API_URL=http://host.docker.internal:8003/api/v1
```

---

## 🛠️ Troubleshooting

### Error: "No se encontró archivo .env"
```bash
# Verifica que el archivo existe en la raíz
ls -la /root/bus-mvp/.env

# Si no existe, créalo desde el ejemplo
cp /root/bus-mvp/.env.example /root/bus-mvp/.env
```

### Error: "Credenciales inválidas"
- Verifica que copiaste correctamente todas las credenciales desde AWS Academy
- Asegúrate de que el Lab de AWS Academy esté activo (botón verde)
- Las credenciales expiran cada 4 horas

### Error: "Access Denied" al usar S3 o Glue
- Verifica que hayas incluido el `AWS_SESSION_TOKEN`
- Para AWS Academy, el session token es OBLIGATORIO

---

## 💡 Beneficios de la centralización

1. **Un solo lugar** para configurar credenciales
2. **Menos archivos** que mantener sincronizados
3. **Menos errores** por credenciales desactualizadas en múltiples lugares
4. **Más seguro** - un solo archivo en `.gitignore`
5. **Más fácil** de actualizar cuando expiran las credenciales

---

## 📚 Recursos adicionales

- [AWS Academy Learner Lab](https://awsacademy.instructure.com)
- [Documentación AWS CLI](https://docs.aws.amazon.com/cli/)
- [Documentación Athena](https://docs.aws.amazon.com/athena/)
