# MS-Analytics - Guía de Inicio Rápido

Esta guía te ayudará a poner en marcha el microservicio MS-Analytics en **5 minutos**.

## ⚡ Quick Start (Local)

### 1. Configurar Entorno (1 min)

```bash
# Navegar a la carpeta del microservicio
cd backend/ms-analytics

# Copiar configuración de ejemplo
cp .env.example .env

# Editar .env con tus credenciales AWS
# Usa tu editor favorito (notepad, vim, vscode, etc.)
notepad .env
```

**Variables requeridas en `.env`:**
```env
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_SESSION_TOKEN=tu_session_token  # Si usas AWS Academy
AWS_DEFAULT_REGION=us-east-1
GLUE_DATABASE=bus_mvp_db
ATHENA_OUTPUT_LOCATION=s3://bus-mvp-datalake/athena-results/
```

### 2. Instalar Dependencias (2 min)

```bash
# Crear entorno virtual (opcional pero recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows PowerShell:
.\venv\Scripts\Activate.ps1

# En Windows CMD:
venv\Scripts\activate.bat

# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Ejecutar el Servicio (1 min)

```bash
# Ejecutar con uvicorn
uvicorn src.main:app --reload --port 8005
```

### 4. Verificar Funcionamiento (1 min)

Abre tu navegador en:

- **Swagger UI**: http://localhost:8005/docs
- **Health Check**: http://localhost:8005/api/v1/health

Si ves la documentación Swagger, ¡ya está funcionando! 🎉

---

## 🐳 Quick Start (Docker)

### Opción A: Docker Standalone

```bash
# Build de la imagen
cd backend/ms-analytics
docker build -t ms-analytics:latest .

# Ejecutar contenedor
docker run -d \
  --name ms-analytics \
  -p 8005:8005 \
  --env-file .env \
  ms-analytics:latest

# Ver logs
docker logs -f ms-analytics
```

### Opción B: Docker Compose (Recomendado)

```bash
# Desde la carpeta data-ingestion
cd data-ingestion

# Asegúrate de tener las variables en .env
# El archivo docker-compose.yml ya incluye ms-analytics

# Ejecutar solo ms-analytics
docker-compose up ms-analytics

# O ejecutar todo el stack
docker-compose up -d
```

---

## 🧪 Verificar que Todo Funciona

### 1. Health Check

```bash
curl http://localhost:8005/api/v1/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "service": "ms-analytics",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00",
  "athena_connection": true
}
```

### 2. Dashboard Summary

```bash
curl http://localhost:8005/api/v1/analytics/summary
```

### 3. Passenger Analytics

```bash
curl http://localhost:8005/api/v1/analytics/passengers
```

---

## 📊 Probar Todos los Endpoints

### En Swagger UI

1. Abre http://localhost:8005/docs
2. Expande cada endpoint
3. Haz click en "Try it out"
4. Haz click en "Execute"
5. Ve los resultados

### Con curl

```bash
# Dashboard Summary
curl http://localhost:8005/api/v1/analytics/summary | jq

# Passengers
curl http://localhost:8005/api/v1/analytics/passengers | jq

# Revenue
curl http://localhost:8005/api/v1/analytics/revenue | jq

# Occupancy
curl http://localhost:8005/api/v1/analytics/occupancy | jq

# Trips
curl http://localhost:8005/api/v1/analytics/trips | jq
```

> **Nota**: `| jq` es opcional, sirve para formatear JSON (requiere instalar `jq`)

### Con PowerShell

```powershell
# Dashboard Summary
Invoke-RestMethod -Uri "http://localhost:8005/api/v1/analytics/summary" | ConvertTo-Json

# Passengers
Invoke-RestMethod -Uri "http://localhost:8005/api/v1/analytics/passengers" | ConvertTo-Json

# Revenue
Invoke-RestMethod -Uri "http://localhost:8005/api/v1/analytics/revenue" | ConvertTo-Json
```

---

## 🔧 Troubleshooting

### Error: "Import could not be resolved"

**Solución**: Instala las dependencias
```bash
pip install -r requirements.txt
```

### Error: "Athena connection test failed"

**Causas posibles:**

1. **Credenciales incorrectas**
   ```bash
   # Verificar .env
   cat .env  # Linux/Mac
   type .env  # Windows
   ```

2. **Bucket S3 no existe**
   ```bash
   # Verificar bucket
   aws s3 ls s3://bus-mvp-datalake/
   ```

3. **Database Glue no existe**
   ```bash
   # Verificar database
   aws glue get-database --name bus_mvp_db
   ```

4. **Credenciales AWS Academy expiradas** (4 horas)
   - Ve a AWS Academy
   - Obtén nuevas credenciales
   - Actualiza `.env`
   - Reinicia el servicio

### Error: "No data found"

**Solución**: Ejecuta el workflow completo

```bash
# 1. Ejecutar ingesta de datos
cd data-ingestion
docker-compose up passengers-ingestion trips-ingestion tickets-ingestion

# 2. Ejecutar crawlers de Glue
python scripts/setup_complete_glue.py

# 3. Crear vistas de Athena
python scripts/create_athena_views.py

# 4. Ahora sí, ejecutar ms-analytics
docker-compose up ms-analytics
```

### Puerto 8005 ya en uso

```bash
# Encontrar proceso usando puerto 8005
# Windows:
netstat -ano | findstr :8005

# Linux/Mac:
lsof -i :8005

# Matar proceso
# Windows:
taskkill /PID <PID> /F

# Linux/Mac:
kill -9 <PID>

# O cambiar puerto en .env
PORT=8006
# Y ejecutar con:
uvicorn src.main:app --reload --port 8006
```

---

## 📝 Siguiente Paso

Una vez que tengas ms-analytics corriendo:

1. **Explora los endpoints en Swagger**: http://localhost:8005/docs
2. **Revisa los logs**: `tail -f logs/app_*.log`
3. **Ejecuta los tests**: `pytest -v`
4. **Lee la documentación completa**: Ver `README.md`

---

## 🎯 Checklist de Verificación

- [ ] Archivo `.env` configurado con credenciales AWS
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Servicio corriendo en puerto 8005
- [ ] Swagger UI accesible en `/docs`
- [ ] Health check retorna status "healthy"
- [ ] Al menos un endpoint de analytics retorna datos
- [ ] Logs se están generando en `logs/`

---

## 💡 Tips

1. **Desarrollo**: Usa `--reload` para hot-reload automático
   ```bash
   uvicorn src.main:app --reload --port 8005
   ```

2. **Producción**: Usa Gunicorn con workers
   ```bash
   gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8005
   ```

3. **Debug**: Aumenta nivel de logs
   ```bash
   # En .env
   LOG_LEVEL=DEBUG
   ```

4. **Testing**: Ejecuta tests antes de deployment
   ```bash
   pytest --cov=src --cov-report=html
   ```

---

**¿Listo?** ¡Empieza ahora! 🚀

```bash
cd backend/ms-analytics
cp .env.example .env
# Edita .env con tus credenciales
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8005
# Abre http://localhost:8005/docs
```
