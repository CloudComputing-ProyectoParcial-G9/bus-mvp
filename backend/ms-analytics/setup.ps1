# MS-Analytics Setup Script
# Automatiza la configuración y ejecución del microservicio

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "MS-Analytics - Setup Automático" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python no encontrado. Instala Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion encontrado" -ForegroundColor Green
Write-Host ""

# Verificar archivo .env
Write-Host "[2/5] Verificando configuración..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Archivo .env no encontrado" -ForegroundColor Yellow
    Write-Host "📄 Creando .env desde .env.example..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "⚠️  IMPORTANTE: Debes editar .env con tus credenciales AWS" -ForegroundColor Yellow
    Write-Host "Presiona Enter para abrir .env en Notepad..." -ForegroundColor Cyan
    Read-Host
    notepad .env
    Write-Host ""
    Write-Host "¿Ya configuraste las credenciales AWS? (S/N)" -ForegroundColor Cyan
    $response = Read-Host
    if ($response -ne "S" -and $response -ne "s") {
        Write-Host "❌ Configuración cancelada" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Archivo .env encontrado" -ForegroundColor Green
Write-Host ""

# Crear entorno virtual
Write-Host "[3/5] Configurando entorno virtual..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Cyan
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al crear entorno virtual" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Entorno virtual configurado" -ForegroundColor Green
Write-Host ""

# Activar entorno virtual e instalar dependencias
Write-Host "[4/5] Instalando dependencias..." -ForegroundColor Yellow
Write-Host "📥 Esto puede tomar unos minutos..." -ForegroundColor Cyan

# Activar venv y ejecutar pip
& "venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
& "venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al instalar dependencias" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
Write-Host ""

# Crear directorio de logs
Write-Host "[5/5] Finalizando configuración..." -ForegroundColor Yellow
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}
Write-Host "✅ Configuración completada" -ForegroundColor Green
Write-Host ""

# Resumen
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "✅ Setup completado exitosamente!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opciones disponibles:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Ejecutar servidor de desarrollo" -ForegroundColor White
Write-Host "2. Ejecutar tests" -ForegroundColor White
Write-Host "3. Construir imagen Docker" -ForegroundColor White
Write-Host "4. Abrir documentación Swagger" -ForegroundColor White
Write-Host "5. Salir" -ForegroundColor White
Write-Host ""

while ($true) {
    $choice = Read-Host "Selecciona una opción (1-5)"
    
    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "🚀 Iniciando servidor en puerto 8005..." -ForegroundColor Cyan
            Write-Host "📖 Swagger UI: http://localhost:8005/docs" -ForegroundColor Yellow
            Write-Host "🏥 Health Check: http://localhost:8005/api/v1/health" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
            Write-Host ""
            & "venv\Scripts\uvicorn.exe" src.main:app --reload --port 8005
            break
        }
        "2" {
            Write-Host ""
            Write-Host "🧪 Ejecutando tests..." -ForegroundColor Cyan
            & "venv\Scripts\pytest.exe" -v --cov=src --cov-report=term-missing
            Write-Host ""
            Write-Host "Presiona Enter para continuar..." -ForegroundColor Cyan
            Read-Host
        }
        "3" {
            Write-Host ""
            Write-Host "🐳 Construyendo imagen Docker..." -ForegroundColor Cyan
            docker build -t ms-analytics:latest .
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Imagen construida exitosamente" -ForegroundColor Green
                Write-Host ""
                Write-Host "Para ejecutar:" -ForegroundColor Yellow
                Write-Host "docker run -d --name ms-analytics -p 8005:8005 --env-file .env ms-analytics:latest" -ForegroundColor Cyan
            }
            Write-Host ""
            Write-Host "Presiona Enter para continuar..." -ForegroundColor Cyan
            Read-Host
        }
        "4" {
            Write-Host ""
            Write-Host "📖 Abriendo Swagger UI..." -ForegroundColor Cyan
            Start-Process "http://localhost:8005/docs"
            Write-Host "⚠️  Asegúrate de que el servidor esté corriendo (opción 1)" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Presiona Enter para continuar..." -ForegroundColor Cyan
            Read-Host
        }
        "5" {
            Write-Host ""
            Write-Host "👋 ¡Hasta luego!" -ForegroundColor Cyan
            exit 0
        }
        default {
            Write-Host "❌ Opción inválida. Selecciona 1-5" -ForegroundColor Red
        }
    }
}
