# MS-Analytics - Comandos Útiles

## 🚀 Comandos Rápidos de Desarrollo

### Instalación y Setup

```bash
# Setup completo con script automatizado
.\setup.ps1

# Setup manual
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Ejecución

```bash
# Desarrollo (con hot-reload)
uvicorn src.main:app --reload --port 8005

# Desarrollo con log level DEBUG
uvicorn src.main:app --reload --port 8005 --log-level debug

# Producción (sin reload)
uvicorn src.main:app --host 0.0.0.0 --port 8005 --workers 4

# Con Gunicorn (producción)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8005
```

### Testing

```bash
# Ejecutar todos los tests
pytest

# Con verbose
pytest -v

# Con coverage
pytest --cov=src --cov-report=term-missing

# Coverage HTML report
pytest --cov=src --cov-report=html
# Abre htmlcov/index.html

# Test específico
pytest tests/test_health.py -v
pytest tests/test_analytics.py::test_dashboard_summary_endpoint -v

# Con output de prints
pytest -s

# Parar en primer error
pytest -x
```

### Docker

```bash
# Build
docker build -t ms-analytics:latest .

# Build sin cache
docker build --no-cache -t ms-analytics:latest .

# Run
docker run -d --name ms-analytics -p 8005:8005 --env-file .env ms-analytics:latest

# Run con logs
docker run --name ms-analytics -p 8005:8005 --env-file .env ms-analytics:latest

# Ver logs
docker logs -f ms-analytics

# Entrar al contenedor
docker exec -it ms-analytics /bin/bash

# Parar
docker stop ms-analytics

# Eliminar
docker rm ms-analytics

# Ver stats
docker stats ms-analytics
```

### Docker Compose

```bash
# Desde data-ingestion/
cd ../data-ingestion

# Ejecutar solo ms-analytics
docker-compose up ms-analytics

# Ejecutar en background
docker-compose up -d ms-analytics

# Ver logs
docker-compose logs -f ms-analytics

# Rebuild y ejecutar
docker-compose up --build ms-analytics

# Parar
docker-compose stop ms-analytics

# Eliminar
docker-compose down ms-analytics

# Ver estado
docker-compose ps
```

### AWS Athena

```bash
# Verificar credenciales
aws sts get-caller-identity

# Listar buckets S3
aws s3 ls

# Ver contenido del bucket
aws s3 ls s3://bus-mvp-datalake-1/
aws s3 ls s3://bus-mvp-datalake-1/raw/
aws s3 ls s3://bus-mvp-datalake-1/raw/passengers_csv/

# Descargar archivo
aws s3 cp s3://bus-mvp-datalake-1/raw/passengers_csv/passengers.csv .

# Verificar database Glue
aws glue get-database --name bus_mvp_db

# Listar tablas
aws glue get-tables --database-name bus_mvp_db --query 'TableList[].Name'

# Describir tabla
aws glue get-table --database-name bus_mvp_db --name passengers_csv

# Ejecutar query Athena (CLI)
aws athena start-query-execution \
  --query-string "SELECT COUNT(*) FROM bus_mvp_db.passengers_csv" \
  --result-configuration OutputLocation=s3://bus-mvp-datalake-1/athena-results/
```

### API Testing

```bash
# Health Check
curl http://localhost:8005/api/v1/health

# Root endpoint
curl http://localhost:8005/

# Dashboard summary
curl http://localhost:8005/api/v1/analytics/summary

# Con formato JSON (requiere jq)
curl http://localhost:8005/api/v1/analytics/summary | jq

# Passengers analytics
curl http://localhost:8005/api/v1/analytics/passengers | jq

# Revenue analytics
curl http://localhost:8005/api/v1/analytics/revenue | jq

# Occupancy analytics
curl http://localhost:8005/api/v1/analytics/occupancy | jq

# Trip analytics
curl http://localhost:8005/api/v1/analytics/trips | jq

# Ver solo status code
curl -s -o /dev/null -w "%{http_code}" http://localhost:8005/api/v1/health

# Con headers
curl -i http://localhost:8005/api/v1/health

# Medir tiempo de respuesta
curl -w "@-" -o /dev/null -s http://localhost:8005/api/v1/analytics/summary << 'EOF'
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
      time_redirect:  %{time_redirect}\n
   time_pretransfer:  %{time_pretransfer}\n
 time_starttransfer:  %{time_starttransfer}\n
                    ----------\n
         time_total:  %{time_total}\n
EOF
```

### API Testing (PowerShell)

```powershell
# Health Check
Invoke-RestMethod -Uri "http://localhost:8005/api/v1/health"

# Con formato
Invoke-RestMethod -Uri "http://localhost:8005/api/v1/health" | ConvertTo-Json

# Dashboard summary
Invoke-RestMethod -Uri "http://localhost:8005/api/v1/analytics/summary" | ConvertTo-Json

# Passengers
$response = Invoke-RestMethod -Uri "http://localhost:8005/api/v1/analytics/passengers"
$response.top_customers | Format-Table

# Revenue
$revenue = Invoke-RestMethod -Uri "http://localhost:8005/api/v1/analytics/revenue"
$revenue.by_route | Format-Table

# Measure response time
Measure-Command { Invoke-RestMethod -Uri "http://localhost:8005/api/v1/analytics/summary" }

# Loop para health check
while ($true) {
    $status = (Invoke-RestMethod -Uri "http://localhost:8005/api/v1/health").status
    Write-Host "$(Get-Date) - Status: $status"
    Start-Sleep -Seconds 60
}
```

### Logs

```bash
# Ver logs en tiempo real
tail -f logs/app_*.log

# Ver últimas 100 líneas
tail -n 100 logs/app_*.log

# Buscar errores
grep ERROR logs/app_*.log

# Buscar por fecha
grep "2024-01-15" logs/app_*.log

# Contar errores
grep -c ERROR logs/app_*.log

# Logs más recientes primero
tail -r logs/app_*.log | head -n 50

# Limpiar logs antiguos
find logs/ -name "*.log" -mtime +7 -delete
```

### Logs (PowerShell)

```powershell
# Ver logs en tiempo real
Get-Content logs\app_*.log -Wait -Tail 50

# Ver últimas 100 líneas
Get-Content logs\app_*.log -Tail 100

# Buscar errores
Select-String -Path logs\app_*.log -Pattern "ERROR"

# Contar errores
(Select-String -Path logs\app_*.log -Pattern "ERROR").Count

# Limpiar logs antiguos (>7 días)
Get-ChildItem logs\*.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item
```

### Desarrollo

```bash
# Formatear código con black
black src/ tests/

# Verificar con flake8
flake8 src/ tests/

# Type checking con mypy
mypy src/

# Instalar pre-commit hooks
pre-commit install
pre-commit run --all-files

# Actualizar dependencias
pip list --outdated
pip install --upgrade <package>

# Generar requirements.txt desde entorno
pip freeze > requirements.txt

# Verificar dependencias de seguridad
pip-audit
```

### Debugging

```bash
# Ejecutar con debugger
python -m pdb src/main.py

# Ejecutar con ipdb (mejor debugger)
pip install ipdb
python -m ipdb src/main.py

# Ver variables de entorno
env | grep AWS
env | grep GLUE

# Probar importaciones
python -c "import src.services.athena_service; print('OK')"

# Probar Pydantic models
python -c "from src.models.responses import HealthCheckResponse; print(HealthCheckResponse.schema_json(indent=2))"

# Verificar puerto disponible
# Windows
netstat -ano | findstr :8005
# Linux/Mac
lsof -i :8005
```

### Performance

```bash
# Benchmark con Apache Bench
ab -n 100 -c 10 http://localhost:8005/api/v1/health

# Con wrk (mejor)
wrk -t4 -c100 -d30s http://localhost:8005/api/v1/health

# Profiling con py-spy
pip install py-spy
py-spy record -o profile.svg -- python -m uvicorn src.main:app

# Memory profiling
pip install memory_profiler
python -m memory_profiler src/main.py
```

### Mantenimiento

```bash
# Backup de logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/

# Limpiar cache Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Limpiar virtual env
rm -rf venv/

# Reinstalar desde cero
rm -rf venv/ __pycache__/
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Git

```bash
# Ignorar cambios locales en .env
git update-index --assume-unchanged .env

# Status
git status

# Add todo excepto .env
git add .
git reset .env

# Commit
git commit -m "feat: implement ms-analytics microservice"

# Ver diferencias
git diff src/main.py
```

### Utilidades

```bash
# Ver estructura del proyecto
tree -L 3

# Contar líneas de código
find src -name "*.py" | xargs wc -l

# Buscar TODO en código
grep -r "TODO" src/

# Verificar sintaxis Python
python -m py_compile src/main.py

# Generar documentación con pdoc
pip install pdoc3
pdoc --html --output-dir docs src/

# Exportar OpenAPI
curl http://localhost:8005/openapi.json > openapi_generated.json
```

### Troubleshooting

```bash
# Verificar instalación de Python
python --version
python -m pip --version

# Verificar entorno virtual activo
which python  # Linux/Mac
where python  # Windows

# Reinstalar dependencia específica
pip uninstall fastapi
pip install fastapi==0.104.1

# Limpiar pip cache
pip cache purge

# Verificar puertos en uso
# Windows
netstat -ano | findstr LISTENING
# Linux/Mac
lsof -i -P -n | grep LISTEN

# Verificar proceso Python
# Windows
tasklist | findstr python
# Linux/Mac
ps aux | grep python

# Matar proceso por puerto
# Windows
netstat -ano | findstr :8005
taskkill /PID <PID> /F
# Linux/Mac
lsof -ti:8005 | xargs kill -9
```

### Shortcuts

```bash
# Alias útiles (agregar a .bashrc o perfil PowerShell)

# Bash
alias ms-analytics-run="cd backend/ms-analytics && uvicorn src.main:app --reload --port 8005"
alias ms-analytics-test="cd backend/ms-analytics && pytest -v"
alias ms-analytics-logs="cd backend/ms-analytics && tail -f logs/app_*.log"

# PowerShell (agregar a $PROFILE)
function ms-analytics-run { cd backend/ms-analytics; uvicorn src.main:app --reload --port 8005 }
function ms-analytics-test { cd backend/ms-analytics; pytest -v }
function ms-analytics-logs { cd backend/ms-analytics; Get-Content logs\app_*.log -Wait -Tail 50 }
```

### Quick Reference

```bash
# Setup → Run → Test (3 comandos)
.\setup.ps1
uvicorn src.main:app --reload --port 8005
pytest -v

# Docker → Run → Logs (3 comandos)
docker build -t ms-analytics:latest .
docker run -d --name ms-analytics -p 8005:8005 --env-file .env ms-analytics:latest
docker logs -f ms-analytics

# Health → Summary → Tests (verificación rápida)
curl http://localhost:8005/api/v1/health
curl http://localhost:8005/api/v1/analytics/summary | jq
pytest -v
```

---

**Tip**: Guarda este archivo como referencia rápida durante el desarrollo! 🚀
