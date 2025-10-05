# 🚀 Quick Start - AWS Academy Lab

Guía rápida para comenzar con el proyecto usando AWS Academy Lab.

## ⚡ Setup en 5 Minutos

### 1️⃣ Obtener Credenciales de AWS Academy

1. **Iniciar el Lab**
   - Ve a AWS Academy → Learner Lab
   - Click **Start Lab** (espera el círculo verde ✅)

2. **Copiar Credenciales**
   - Click **AWS Details** (arriba a la derecha)
   - Click **Show** junto a "AWS CLI"
   - Verás 3 líneas de credenciales

### 2️⃣ Configurar Credenciales (Opción A - Automático)

```powershell
# En Windows PowerShell
cd data-ingestion
.\setup_aws_academy.ps1
```

Sigue las instrucciones en pantalla y pega:
- AWS Access Key ID
- AWS Secret Access Key  
- AWS Session Token

### 2️⃣ Configurar Credenciales (Opción B - Manual)

```powershell
# Copiar template
cp .env.example .env

# Editar archivo
notepad .env
```

Pegar las credenciales:
```env
AWS_ACCESS_KEY_ID=ASIAV...
AWS_SECRET_ACCESS_KEY=wJalr...
AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjEH... # ¡IMPORTANTE!
AWS_DEFAULT_REGION=us-east-1
```

### 3️⃣ Crear Bucket S3

```powershell
# Instalar boto3 si no lo tienes
pip install boto3

# Crear bucket
python scripts\setup_s3.py
```

### 4️⃣ Ejecutar Ingesta

```powershell
# Build de contenedores
docker-compose build

# Ejecutar ingesta
docker-compose up
```

### 5️⃣ Verificar Resultados

```powershell
# Ver archivos en S3
aws s3 ls s3://bus-mvp-datalake/raw/ --recursive
```

## ✅ Esperado

Deberías ver:
```
2025-10-05 14:30:22    1024 raw/passengers/passengers_20251005_143022.csv
2025-10-05 14:30:22    2048 raw/passengers/passengers_20251005_143022.json
2025-10-05 14:30:25    1024 raw/trips/trips_20251005_143025.csv
2025-10-05 14:30:25    2048 raw/trips/trips_20251005_143025.json
2025-10-05 14:30:28    1024 raw/tickets/tickets_20251005_143028.csv
2025-10-05 14:30:28    2048 raw/tickets/tickets_20251005_143028.json
```

## 🔄 Renovar Credenciales (Cada 4 horas)

Cuando veas el error `ExpiredToken`:

```powershell
# 1. Detener servicios
docker-compose down

# 2. Ejecutar script de nuevo
.\setup_aws_academy.ps1

# 3. Reiniciar servicios
docker-compose up
```

## 🐛 Troubleshooting

### ❌ Error: Cannot connect to Docker
```powershell
# Verificar que Docker Desktop está corriendo
docker ps
```

### ❌ Error: ExpiredToken
```powershell
# Renovar credenciales con el script
.\setup_aws_academy.ps1
```

### ❌ Error: Cannot connect to microservices
```powershell
# Verificar que los microservicios están corriendo
# En otro terminal, ir a cada microservicio y ejecutar:
docker-compose up -d
```

### ❌ Error: Access Denied S3
```powershell
# Verificar que incluiste AWS_SESSION_TOKEN
cat .env | Select-String "SESSION_TOKEN"
```

## 📚 Documentación Completa

- **[AWS_ACADEMY_SETUP.md](./AWS_ACADEMY_SETUP.md)** - Guía completa para AWS Academy
- **[README.md](./README.md)** - Documentación general
- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Guía de testing

## ⏰ Recordatorios

- 🔄 **Renovar credenciales cada 4 horas**
- 💰 **Presupuesto de $100 USD** - Monitorea el uso
- ⏸️ **Detener Lab** cuando no lo uses (ahorra tiempo de sesión)
- 🧹 **Limpiar recursos** al terminar

## 🎯 Siguientes Pasos

Después de tener datos en S3:

```powershell
# 1. Configurar Glue Catalog
python scripts\setup_glue.py

# 2. Iniciar Analytics API
docker-compose up -d analytics-service

# 3. Probar API
curl http://localhost:5000/health
```

## 💡 Tips

- ✅ Usa `LIMIT` en queries de Athena (ahorra dinero)
- ✅ No ejecutes crawlers en loop
- ✅ Elimina archivos antiguos de S3 si no los necesitas
- ✅ Detén el Lab cuando no lo uses

---

**¿Problemas?** Lee la documentación completa en [AWS_ACADEMY_SETUP.md](./AWS_ACADEMY_SETUP.md)
