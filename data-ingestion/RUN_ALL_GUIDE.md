# Script Centralizado - Data Ingestion

Script que ejecuta automáticamente todo el proceso de ingesta de datos.

## 🚀 Uso Básico

### Windows
```powershell
# Configurar credenciales (primera vez o cuando expiren)
.\setup_aws_academy.ps1

# Ejecutar todo el proceso
.\run_all.ps1
```

### Linux/Mac
```bash
# Configurar credenciales (primera vez o cuando expiren)
./setup_aws_academy.sh

# Ejecutar todo el proceso
chmod +x run_all.sh
./run_all.sh
```

## ⚙️ Opciones

### Windows
```powershell
# Solo actualizar datos (modo rápido)
.\run_all.ps1 -QuickMode

# Saltar pasos específicos
.\run_all.ps1 -SkipS3Setup      # No crear bucket S3
.\run_all.ps1 -SkipIngestion    # No ejecutar ingesta
.\run_all.ps1 -SkipGlue         # No configurar Glue
.\run_all.ps1 -SkipAthena       # No configurar Athena
```

### Linux/Mac
```bash
# Solo actualizar datos (modo rápido)
./run_all.sh --quick

# Saltar pasos específicos
./run_all.sh --skip-s3          # No crear bucket S3
./run_all.sh --skip-ingestion   # No ejecutar ingesta
./run_all.sh --skip-glue        # No configurar Glue
./run_all.sh --skip-athena      # No configurar Athena

# Ver ayuda
./run_all.sh --help
```

## 📋 ¿Qué Hace?

El script ejecuta automáticamente:

1. **Verificación de prerequisitos** - Docker, Python, AWS CLI, credenciales
2. **Configuración de S3** - Crea bucket y estructura de carpetas
3. **Ingesta de datos** - Ejecuta los 3 contenedores (passengers, trips, tickets)
4. **Configuración de Glue** - Crea database y crawlers
5. **Configuración de Athena** - Crea tablas y vistas
6. **Validación** - Verifica que todo funcione

**Tiempo**: 8-12 minutos

## 🔧 Prerequisitos

Antes de ejecutar:

1. **Software instalado**: Docker, Docker Compose, Python 3.8+, AWS CLI
2. **Microservicios corriendo**: `docker ps` debe mostrar ms-passengers, ms-trips, ms-tickets
3. **Credenciales AWS configuradas**: Ejecutar `setup_aws_academy.ps1` o `setup_aws_academy.sh`

## 🐛 Problemas Comunes

### "Docker no está disponible"
```bash
# Verificar que Docker Desktop esté corriendo
docker --version
```

### "Credenciales AWS no configuradas"
```bash
# Windows
.\setup_aws_academy.ps1

# Linux/Mac
./setup_aws_academy.sh
```

### "Microservicios no están corriendo"
```bash
cd ../backend
docker-compose up -d
```

### Credenciales de AWS Academy expiraron (cada 4 horas)
```bash
# Re-ejecutar setup
.\setup_aws_academy.ps1   # Windows
./setup_aws_academy.sh    # Linux/Mac
```

## ✅ Verificación

Después de ejecutar el script:

```bash
# Ver archivos en S3
aws s3 ls s3://bus-mvp-datalake/raw/ --recursive

# Ver tablas en Glue
aws glue get-tables --database-name bus_mvp_db

# Abrir Athena en navegador
# https://console.aws.amazon.com/athena/
```

## 🔄 Casos de Uso

### Primera vez - Setup completo
```bash
.\setup_aws_academy.ps1
.\run_all.ps1
```

### Actualizar solo datos
```bash
.\run_all.ps1 -QuickMode
```

### Re-configurar AWS (sin ingesta)
```bash
.\run_all.ps1 -SkipIngestion
```

---

Para más información, ver [README.md](./README.md)
