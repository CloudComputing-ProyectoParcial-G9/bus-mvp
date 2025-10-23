# 🔐 Configuración de Credenciales AWS - ACTUALIZADO

## ⚠️ CAMBIO IMPORTANTE DE SEGURIDAD

**Las credenciales de AWS ya NO se almacenan en el archivo `.env`**

Ahora usamos el método estándar de AWS CLI (`~/.aws/credentials`) para gestionar credenciales:
- ✅ Más seguro (no expone credenciales en variables de entorno)
- ✅ Compatible con AWS CLI, boto3, y todas las herramientas de AWS
- ✅ Los contenedores Docker montan `~/.aws` en modo solo lectura
- ✅ Fácil de actualizar cuando las credenciales expiran (AWS Academy)

---

## 📋 Métodos de Configuración

### Método 1: Configuración Manual (Recomendado)

1. Crea el directorio `.aws` si no existe:
```bash
mkdir -p ~/.aws
```

2. Edita el archivo de credenciales:
```bash
nano ~/.aws/credentials
```

3. Agrega tus credenciales con el siguiente formato:
```ini
[default]
aws_access_key_id=TU_ACCESS_KEY_ID
aws_secret_access_key=TU_SECRET_ACCESS_KEY
aws_session_token=TU_SESSION_TOKEN
```

4. (Opcional) Configura la región por defecto:
```bash
nano ~/.aws/config
```

```ini
[default]
region=us-east-1
output=json
```

5. Establece permisos seguros:
```bash
chmod 600 ~/.aws/credentials
chmod 600 ~/.aws/config
```

### Método 2: Script de Sincronización Automática

Si ya tienes credenciales en el archivo `.env` y quieres copiarlas a `~/.aws/credentials`:

```bash
cd /root/bus-mvp/data-ingestion
bash sync_aws_credentials.sh
```

Este script:
- Lee las credenciales de `../.env`
- Las copia a `~/.aws/credentials`
- Establece los permisos correctos automáticamente

### Método 3: AWS CLI

Usa el comando de configuración de AWS CLI:

```bash
aws configure
```

Sigue las instrucciones e ingresa:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (ej: us-east-1)
- Default output format (ej: json)

---

## 🐳 Cómo Funciona con Docker

El archivo `docker-compose.yml` ahora monta el directorio `~/.aws` como un volumen de solo lectura:

```yaml
volumes:
  - ~/.aws:/root/.aws:ro  # Monta credenciales de AWS en modo solo lectura
```

Esto significa que:
- Los contenedores Docker tienen acceso a tus credenciales
- Las credenciales están en modo solo lectura (`:ro`) para mayor seguridad
- No se copian ni exponen en variables de entorno
- boto3 las encuentra automáticamente

---

## 🔍 Dónde se usan las credenciales

### 1. Contenedores Docker (data-ingestion/)
El `docker-compose.yml` monta `~/.aws:/root/.aws:ro`:
- `passengers-ingestion`
- `trips-ingestion`
- `tickets-ingestion`

### 2. Scripts de Python (data-ingestion/scripts/)
Todos los scripts usan boto3 que lee automáticamente de `~/.aws/credentials`:
- `setup_s3.py`
- `setup_glue.py`
- `create_athena_tables.py`
- `create_athena_views.py`
- `run_athena_queries.py`
- `auto_sync.py`
- `test_athena_queries.py`
- `check_crawlers.py`

### 3. Microservicio ms-analytics
Puede usar el mismo método de montar `~/.aws` como volumen.

---

## 🔄 Actualizar Credenciales de AWS Academy

AWS Academy genera credenciales temporales que expiran cada 4 horas. Para actualizarlas:

### Opción A: Actualización Manual

1. Ve a tu laboratorio en AWS Academy
2. Haz clic en "AWS Details"
3. Haz clic en "Show" junto a "AWS CLI"
4. Copia las tres líneas de credenciales

```bash
nano ~/.aws/credentials
```
Pega las nuevas credenciales

### Opción B: Actualización desde .env

Si copias las credenciales al archivo `.env` en la raíz del proyecto, ejecuta:
```bash
cd /root/bus-mvp/data-ingestion
bash sync_aws_credentials.sh
```

---

## ✅ Verificación

Verifica que tus credenciales funcionan correctamente:

```bash
# Listar buckets S3
aws s3 ls

# Verificar identidad
aws sts get-caller-identity

# Listar objetos en el bucket del proyecto
aws s3 ls s3://bus-mvp-datalake-1/
```

---

## 📦 Variables requeridas

### En ~/.aws/credentials
```ini
[default]
aws_access_key_id=TU_ACCESS_KEY_ID
aws_secret_access_key=TU_SECRET_ACCESS_KEY
aws_session_token=TU_SESSION_TOKEN
```

### En ~/.aws/config (opcional)
```ini
[default]
region=us-east-1
output=json
```

### En /root/bus-mvp/.env (sin credenciales)
```bash
# AWS Configuration
AWS_DEFAULT_REGION=us-east-1
AWS_ACCOUNT_ID=tu_account_id_aquí

# S3 & Data Lake
S3_BUCKET=bus-mvp-datalake-1

# Glue & Athena
GLUE_DATABASE=bus_mvp_db
ATHENA_OUTPUT_LOCATION=s3://bus-mvp-datalake-1/athena-results/
ATHENA_QUERY_TIMEOUT=60

# Data Ingestion APIs
PASSENGERS_API_URL=http://host.docker.internal:8001/api/v1
TRIPS_API_URL=http://host.docker.internal:8002/api/v1
TICKETS_API_URL=http://host.docker.internal:8003/api/v1
```

---

## 🔒 Seguridad

### ✅ Buenas Prácticas

- ✅ Las credenciales están en `~/.aws/credentials` (nunca en Git)
- ✅ El archivo `.env` está en `.gitignore`
- ✅ Los contenedores montan `~/.aws` en modo solo lectura (`:ro`)
- ✅ Permisos 600 en archivos de credenciales (solo el propietario puede leer/escribir)

### ❌ NO Hacer

- ❌ NO commitees archivos con credenciales a Git
- ❌ NO compartas tu archivo `.env` o `~/.aws/credentials`
- ❌ NO expongas credenciales en logs o código
- ❌ NO uses credenciales en URLs o parámetros de línea de comando
- ❌ NO definas AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY en variables de entorno

---

## 🛠️ Troubleshooting

### Error: "Unable to locate credentials"

**Causa:** boto3 no puede encontrar las credenciales

**Solución:**
```bash
# Verificar que existe el archivo
ls -la ~/.aws/credentials

# Verificar permisos
chmod 600 ~/.aws/credentials

# Verificar contenido (formato correcto)
cat ~/.aws/credentials
```

### Error: "An error occurred (ExpiredToken)"

**Causa:** Las credenciales de AWS Academy expiraron (cada 4 horas)

**Solución:**
1. Ve a AWS Academy y genera nuevas credenciales
2. Actualiza `~/.aws/credentials` con las nuevas credenciales
3. O ejecuta `bash data-ingestion/sync_aws_credentials.sh`

### Error: "Access Denied"

**Causa:** Las credenciales no tienen permisos suficientes

**Solución:**
- Verifica que estás usando las credenciales correctas
- En AWS Academy, asegúrate de que el laboratorio esté iniciado (botón verde)
- Verifica los permisos de tu usuario/rol en AWS

### Los contenedores Docker no encuentran las credenciales

**Causa:** El volumen no está montado correctamente

**Solución:**
```bash
# Verificar que docker-compose.yml tiene el volumen
grep -A5 "volumes:" docker-compose.yml

# Debería mostrar:
# volumes:
#   - ~/.aws:/root/.aws:ro

# Recrear los contenedores
docker-compose down
docker-compose up -d
```

---

## 📁 Estructura de Archivos

```
~/.aws/
├── credentials    # ✅ Credenciales de AWS (Access Key, Secret Key, Session Token)
└── config         # ✅ Configuración (región, output format)

/root/bus-mvp/
├── .env           # ✅ Variables de entorno (NO contiene credenciales AWS)
├── .env.example   # ✅ Plantilla de ejemplo
└── .gitignore     # ✅ Incluye .env

/root/bus-mvp/data-ingestion/
├── docker-compose.yml           # ✅ Monta ~/.aws como volumen
└── sync_aws_credentials.sh      # ✅ Script para sincronizar credenciales
```

---

## 💡 Beneficios del Nuevo Método

1. **Más seguro** - Las credenciales no están en variables de entorno
2. **Estándar de la industria** - Mismo método que AWS CLI
3. **Compatible** - Funciona con todas las herramientas de AWS (boto3, AWS CLI, etc.)
4. **Solo lectura en Docker** - Los contenedores no pueden modificar las credenciales
5. **Fácil de actualizar** - Solo actualiza `~/.aws/credentials`
6. **Sin duplicación** - Una sola fuente de verdad para credenciales

---

## 📚 Recursos adicionales

- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [Boto3 Credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)
- [AWS Academy Learner Lab](https://awsacademy.instructure.com/)
- [Docker Volumes](https://docs.docker.com/storage/volumes/)

---

## 🆘 Soporte

Si tienes problemas con la configuración de credenciales:

1. Verifica que tus credenciales sean válidas en AWS Academy
2. Asegúrate de que el laboratorio esté iniciado (botón verde)
3. Revisa los logs de Docker: `docker-compose logs`
4. Consulta la sección de resolución de problemas arriba
5. Ejecuta el script de verificación: `aws sts get-caller-identity`
