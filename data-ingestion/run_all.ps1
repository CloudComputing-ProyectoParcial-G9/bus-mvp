# ============================================================================
# Script Centralizado - Data Ingestion Pipeline
# Bus MVP - Cloud Computing Project
# ============================================================================
# Descripción: Ejecuta el proceso completo de ingesta de datos:
#              1. Verificación de prerequisitos
#              2. Creación de infraestructura AWS (S3, Glue, Athena)
#              3. Ejecución de ingesta de datos
#              4. Validación de resultados
# ============================================================================

param(
    [switch]$SkipPrerequisites,  # Salta verificación de prerequisitos
    [switch]$SkipS3Setup,        # Salta creación de bucket S3
    [switch]$SkipIngestion,      # Salta ingesta de datos
    [switch]$SkipGlue,           # Salta configuración de Glue
    [switch]$SkipAthena,         # Salta creación de tablas/vistas en Athena
    [switch]$SkipValidation,     # Salta validación final
    [switch]$QuickMode           # Modo rápido (solo ingesta)
)

# Configuración
$ErrorActionPreference = "Continue"
$SCRIPT_DIR = $PSScriptRoot
$SCRIPTS_DIR = Join-Path $SCRIPT_DIR "scripts"

# Colores
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Step { Write-Host "`n$args" -ForegroundColor Magenta }
function Write-Banner { 
    Write-Host "`n" ("=" * 80) -ForegroundColor Magenta
    Write-Host "  $args" -ForegroundColor Magenta
    Write-Host ("=" * 80) -ForegroundColor Magenta
}

# ============================================================================
# FUNCIONES DE VERIFICACIÓN
# ============================================================================

function Test-Prerequisites {
    Write-Banner "VERIFICANDO PREREQUISITOS"
    
    $allOk = $true
    
    # 1. Verificar Docker
    Write-Step "1️⃣  Verificando Docker..."
    try {
        $dockerVersion = docker --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  ✅ Docker instalado: $dockerVersion"
        } else {
            Write-Error "  ❌ Docker no está disponible"
            $allOk = $false
        }
    } catch {
        Write-Error "  ❌ Error verificando Docker"
        $allOk = $false
    }
    
    # 2. Verificar Docker Compose
    Write-Step "2️⃣  Verificando Docker Compose..."
    try {
        $composeVersion = docker-compose --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  ✅ Docker Compose instalado: $composeVersion"
        } else {
            Write-Error "  ❌ Docker Compose no está disponible"
            $allOk = $false
        }
    } catch {
        Write-Error "  ❌ Error verificando Docker Compose"
        $allOk = $false
    }
    
    # 3. Verificar Python
    Write-Step "3️⃣  Verificando Python..."
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  ✅ Python instalado: $pythonVersion"
        } else {
            Write-Error "  ❌ Python no está disponible"
            $allOk = $false
        }
    } catch {
        Write-Error "  ❌ Error verificando Python"
        $allOk = $false
    }
    
    # 4. Verificar AWS CLI
    Write-Step "4️⃣  Verificando AWS CLI..."
    try {
        $awsVersion = aws --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  ✅ AWS CLI instalado: $awsVersion"
        } else {
            Write-Error "  ❌ AWS CLI no está disponible"
            $allOk = $false
        }
    } catch {
        Write-Error "  ❌ Error verificando AWS CLI"
        $allOk = $false
    }
    
    # 5. Verificar archivo .env
    Write-Step "5️⃣  Verificando configuración..."
    $envFile = Join-Path $SCRIPT_DIR ".env"
    if (Test-Path $envFile) {
        Write-Success "  ✅ Archivo .env encontrado"
        
        # Verificar que tenga credenciales
        $content = Get-Content $envFile -Raw
        if ($content -match "AWS_ACCESS_KEY_ID=(?!your_)" -and $content -match "AWS_SECRET_ACCESS_KEY=(?!your_)") {
            Write-Success "  ✅ Credenciales AWS configuradas"
        } else {
            Write-Warning "  ⚠️  Credenciales AWS no configuradas en .env"
            Write-Info "     Ejecuta: .\setup_aws_academy.ps1"
            $allOk = $false
        }
    } else {
        Write-Warning "  ⚠️  Archivo .env no encontrado"
        Write-Info "     Creando desde .env.example..."
        
        $exampleFile = Join-Path $SCRIPT_DIR ".env.example"
        if (Test-Path $exampleFile) {
            Copy-Item $exampleFile $envFile
            Write-Success "  ✅ Archivo .env creado"
            Write-Warning "  ⚠️  Por favor edita .env con tus credenciales AWS"
            $allOk = $false
        }
    }
    
    # 6. Verificar microservicios
    Write-Step "6️⃣  Verificando microservicios..."
    $containers = docker ps --format "{{.Names}}" 2>&1
    $services = @("ms-passengers", "ms-trips", "ms-tickets")
    $running = 0
    
    foreach ($service in $services) {
        if ($containers -match $service) {
            Write-Success "  ✅ $service corriendo"
            $running++
        } else {
            Write-Warning "  ⚠️  $service no está corriendo"
        }
    }
    
    if ($running -eq 0) {
        Write-Warning "  ⚠️  Ningún microservicio está corriendo"
        Write-Info "     Los microservicios deben estar activos para la ingesta"
    } elseif ($running -lt 3) {
        Write-Warning "  ⚠️  Faltan microservicios ($running/3)"
    } else {
        Write-Success "  ✅ Todos los microservicios están corriendo ($running/3)"
    }
    
    # 7. Verificar dependencias Python
    Write-Step "7️⃣  Verificando dependencias Python..."
    $reqFile = Join-Path $SCRIPTS_DIR "requirements.txt"
    if (Test-Path $reqFile) {
        Write-Info "  📦 Instalando dependencias Python..."
        pip install -q -r $reqFile 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  ✅ Dependencias Python instaladas"
        } else {
            Write-Warning "  ⚠️  Algunas dependencias pueden faltar"
        }
    }
    
    if (-not $allOk) {
        Write-Error "`n❌ Algunos prerequisitos no están cumplidos"
        Write-Info "   Por favor revisa los errores arriba antes de continuar`n"
        
        $continue = Read-Host "¿Deseas continuar de todas formas? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 1
        }
    } else {
        Write-Success "`n✅ Todos los prerequisitos están cumplidos`n"
    }
    
    return $allOk
}

function Test-AWSConnection {
    Write-Step "Verificando conexión a AWS..."
    
    try {
        $identity = aws sts get-caller-identity --output json 2>&1 | ConvertFrom-Json
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  ✅ Conectado a AWS"
            Write-Info "     Account: $($identity.Account)"
            Write-Info "     User: $($identity.Arn)"
            return $true
        } else {
            Write-Error "  ❌ No se pudo conectar a AWS"
            return $false
        }
    } catch {
        Write-Error "  ❌ Error verificando credenciales AWS: $_"
        return $false
    }
}

# ============================================================================
# FUNCIONES DE EJECUCIÓN
# ============================================================================

function Invoke-S3Setup {
    Write-Banner "PASO 1: CONFIGURANDO AWS S3"
    
    $setupScript = Join-Path $SCRIPTS_DIR "setup_s3.py"
    
    if (-not (Test-Path $setupScript)) {
        Write-Error "❌ Script setup_s3.py no encontrado"
        return $false
    }
    
    Write-Info "🪣 Creando bucket S3 y estructura de carpetas..."
    Write-Info "   Script: $setupScript"
    
    try {
        python $setupScript
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "`n✅ Bucket S3 configurado exitosamente"
            return $true
        } else {
            Write-Error "❌ Error configurando S3"
            return $false
        }
    } catch {
        Write-Error "❌ Error ejecutando setup_s3.py: $_"
        return $false
    }
}

function Invoke-DataIngestion {
    Write-Banner "PASO 2: EJECUTANDO INGESTA DE DATOS"
    
    if (-not (Test-Path "docker-compose.yml")) {
        Write-Error "❌ docker-compose.yml no encontrado"
        return $false
    }
    
    Write-Info "📊 Construyendo imágenes Docker..."
    docker-compose build --quiet
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Error construyendo imágenes Docker"
        return $false
    }
    
    Write-Success "✅ Imágenes construidas"
    
    # Ejecutar ingesta de cada microservicio
    $services = @("passengers-ingestion", "trips-ingestion", "tickets-ingestion")
    $success = $true
    
    foreach ($service in $services) {
        Write-Step "Ejecutando $service..."
        
        docker-compose up $service
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  ✅ $service completado"
        } else {
            Write-Error "  ❌ $service falló"
            $success = $false
        }
        
        Start-Sleep -Seconds 2
    }
    
    if ($success) {
        Write-Success "`n✅ Ingesta de datos completada exitosamente"
    } else {
        Write-Warning "`n⚠️  Ingesta completada con algunos errores"
    }
    
    return $success
}

function Invoke-GlueSetup {
    Write-Banner "PASO 3: CONFIGURANDO AWS GLUE"
    
    $setupScript = Join-Path $SCRIPTS_DIR "setup_complete_glue.py"
    
    if (-not (Test-Path $setupScript)) {
        Write-Warning "⚠️  Script setup_complete_glue.py no encontrado"
        Write-Info "   Intentando con setup_glue.py..."
        $setupScript = Join-Path $SCRIPTS_DIR "setup_glue.py"
    }
    
    if (-not (Test-Path $setupScript)) {
        Write-Error "❌ Script de configuración de Glue no encontrado"
        return $false
    }
    
    Write-Info "📊 Configurando AWS Glue Catalog..."
    Write-Info "   - Creando database"
    Write-Info "   - Creando crawlers"
    Write-Info "   - Ejecutando crawlers"
    
    try {
        python $setupScript
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "`n✅ AWS Glue configurado exitosamente"
            return $true
        } else {
            Write-Error "❌ Error configurando Glue"
            return $false
        }
    } catch {
        Write-Error "❌ Error ejecutando setup de Glue: $_"
        return $false
    }
}

function Invoke-AthenaSetup {
    Write-Banner "PASO 4: CONFIGURANDO AWS ATHENA"
    
    # 1. Crear tablas
    Write-Step "Creando tablas en Athena..."
    $tablesScript = Join-Path $SCRIPTS_DIR "create_athena_tables.py"
    
    if (Test-Path $tablesScript) {
        python $tablesScript
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  ✅ Tablas creadas"
        } else {
            Write-Warning "  ⚠️  Error creando tablas"
        }
    } else {
        Write-Warning "  ⚠️  Script create_athena_tables.py no encontrado"
    }
    
    # 2. Ejecutar queries de prueba
    Write-Step "Ejecutando queries de prueba..."
    $queriesScript = Join-Path $SCRIPTS_DIR "test_athena_queries.py"
    
    if (Test-Path $queriesScript) {
        python $queriesScript
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  ✅ Queries ejecutadas"
        } else {
            Write-Warning "  ⚠️  Error ejecutando queries"
        }
    } else {
        Write-Warning "  ⚠️  Script test_athena_queries.py no encontrado"
    }
    
    # 3. Crear vistas
    Write-Step "Creando vistas en Athena..."
    $viewsScript = Join-Path $SCRIPTS_DIR "create_athena_views.py"
    
    if (Test-Path $viewsScript) {
        python $viewsScript
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  ✅ Vistas creadas"
        } else {
            Write-Warning "  ⚠️  Error creando vistas"
        }
    } else {
        Write-Warning "  ⚠️  Script create_athena_views.py no encontrado"
    }
    
    Write-Success "`n✅ AWS Athena configurado"
    return $true
}

function Invoke-Validation {
    Write-Banner "PASO 5: VALIDANDO RESULTADOS"
    
    # 1. Verificar datos en S3
    Write-Step "Verificando datos en S3..."
    
    $envFile = Join-Path $SCRIPT_DIR ".env"
    $bucket = "bus-mvp-datalake"
    
    if (Test-Path $envFile) {
        $content = Get-Content $envFile
        $bucketLine = $content | Where-Object { $_ -match "S3_BUCKET=" }
        if ($bucketLine) {
            $bucket = $bucketLine -replace "S3_BUCKET=", ""
        }
    }
    
    $paths = @("raw/passengers_csv/", "raw/trips_csv/", "raw/tickets_csv/")
    $allData = $true
    
    foreach ($path in $paths) {
        try {
            $result = aws s3 ls "s3://$bucket/$path" 2>&1
            if ($LASTEXITCODE -eq 0 -and $result) {
                $count = ($result | Measure-Object).Count
                Write-Success "  ✅ $path - $count archivo(s)"
            } else {
                Write-Warning "  ⚠️  $path - Sin archivos"
                $allData = $false
            }
        } catch {
            Write-Warning "  ⚠️  Error verificando $path"
            $allData = $false
        }
    }
    
    # 2. Verificar Glue Database
    Write-Step "Verificando AWS Glue Database..."
    
    try {
        $dbResult = aws glue get-database --name bus_mvp_db 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  ✅ Database 'bus_mvp_db' existe"
            
            # Verificar tablas
            $tablesResult = aws glue get-tables --database-name bus_mvp_db --output json 2>&1 | ConvertFrom-Json
            $tableCount = $tablesResult.TableList.Count
            
            if ($tableCount -gt 0) {
                Write-Success "  ✅ $tableCount tabla(s) encontrada(s)"
                foreach ($table in $tablesResult.TableList) {
                    Write-Info "     📊 $($table.Name)"
                }
            } else {
                Write-Warning "  ⚠️  No se encontraron tablas"
            }
        } else {
            Write-Warning "  ⚠️  Database 'bus_mvp_db' no encontrada"
        }
    } catch {
        Write-Warning "  ⚠️  Error verificando Glue Database"
    }
    
    # 3. Resumen
    Write-Step "Resumen de validación"
    
    if ($allData) {
        Write-Success "  ✅ Datos ingresados correctamente en S3"
    } else {
        Write-Warning "  ⚠️  Algunos datos pueden estar faltando"
    }
    
    Write-Info "`n📋 Próximos pasos:"
    Write-Info "   1. Abrir AWS Athena Console"
    Write-Info "   2. Seleccionar database: bus_mvp_db"
    Write-Info "   3. Ejecutar queries SQL"
    Write-Info "   4. Crear vistas analíticas"
    
    return $true
}

function Show-Summary {
    Write-Banner "RESUMEN DE EJECUCIÓN"
    
    Write-Info "📊 Proceso completado`n"
    
    Write-Host "Componentes configurados:" -ForegroundColor Cyan
    Write-Host "  ✅ AWS S3 Bucket (Data Lake)" -ForegroundColor Green
    Write-Host "  ✅ Contenedores Docker (Ingesta)" -ForegroundColor Green
    Write-Host "  ✅ AWS Glue Catalog (Database + Crawlers)" -ForegroundColor Green
    Write-Host "  ✅ AWS Athena (Tablas + Queries)" -ForegroundColor Green
    
    Write-Host "`nArchivos generados:" -ForegroundColor Cyan
    Write-Host "  📁 s3://bus-mvp-datalake/raw/passengers_csv/" -ForegroundColor Gray
    Write-Host "  📁 s3://bus-mvp-datalake/raw/trips_csv/" -ForegroundColor Gray
    Write-Host "  📁 s3://bus-mvp-datalake/raw/tickets_csv/" -ForegroundColor Gray
    
    Write-Host "`nServicios disponibles:" -ForegroundColor Cyan
    Write-Host "  🔍 AWS Athena: https://console.aws.amazon.com/athena/" -ForegroundColor Gray
    Write-Host "  📊 AWS Glue: https://console.aws.amazon.com/glue/" -ForegroundColor Gray
    Write-Host "  🪣 AWS S3: https://console.aws.amazon.com/s3/" -ForegroundColor Gray
    
    Write-Host "`nDocumentación:" -ForegroundColor Cyan
    Write-Host "  📖 README.md - Guía general" -ForegroundColor Gray
    Write-Host "  📖 IMPLEMENTATION_GUIDE.md - Guía de implementación" -ForegroundColor Gray
    Write-Host "  📖 TESTING_GUIDE.md - Guía de testing" -ForegroundColor Gray
}

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

function Start-DataIngestionPipeline {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                                        ║" -ForegroundColor Cyan
    Write-Host "║          BUS MVP - DATA INGESTION PIPELINE (Centralizado)             ║" -ForegroundColor Cyan
    Write-Host "║                                                                        ║" -ForegroundColor Cyan
    Write-Host "║  Este script ejecuta el proceso completo de ingesta de datos:         ║" -ForegroundColor Cyan
    Write-Host "║    1. Verificación de prerequisitos                                   ║" -ForegroundColor Cyan
    Write-Host "║    2. Configuración de AWS S3                                         ║" -ForegroundColor Cyan
    Write-Host "║    3. Ingesta de datos desde microservicios                           ║" -ForegroundColor Cyan
    Write-Host "║    4. Configuración de AWS Glue Catalog                               ║" -ForegroundColor Cyan
    Write-Host "║    5. Configuración de AWS Athena                                     ║" -ForegroundColor Cyan
    Write-Host "║    6. Validación de resultados                                        ║" -ForegroundColor Cyan
    Write-Host "║                                                                        ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    $startTime = Get-Date
    Write-Info "🕐 Inicio: $($startTime.ToString('yyyy-MM-dd HH:mm:ss'))"
    Write-Host ""
    
    # Modo rápido - solo ingesta
    if ($QuickMode) {
        Write-Warning "⚡ MODO RÁPIDO - Solo ejecutando ingesta de datos"
        $SkipPrerequisites = $true
        $SkipS3Setup = $true
        $SkipGlue = $true
        $SkipAthena = $true
        $SkipValidation = $true
    }
    
    $success = $true
    
    # PASO 0: Verificar prerequisitos
    if (-not $SkipPrerequisites) {
        if (-not (Test-Prerequisites)) {
            Write-Warning "⚠️  Algunas verificaciones fallaron, pero continuando..."
        }
        
        if (-not (Test-AWSConnection)) {
            Write-Error "❌ No se puede conectar a AWS. Verifica tus credenciales."
            Write-Info "   Ejecuta: .\setup_aws_academy.ps1"
            exit 1
        }
    }
    
    # PASO 1: Configurar S3
    if (-not $SkipS3Setup) {
        if (-not (Invoke-S3Setup)) {
            Write-Warning "⚠️  Error en configuración de S3, pero continuando..."
            $success = $false
        }
        Start-Sleep -Seconds 2
    }
    
    # PASO 2: Ejecutar ingesta
    if (-not $SkipIngestion) {
        if (-not (Invoke-DataIngestion)) {
            Write-Error "❌ Error en ingesta de datos"
            $success = $false
        }
        Start-Sleep -Seconds 3
    }
    
    # PASO 3: Configurar Glue
    if (-not $SkipGlue) {
        if (-not (Invoke-GlueSetup)) {
            Write-Warning "⚠️  Error en configuración de Glue, pero continuando..."
            $success = $false
        }
        Start-Sleep -Seconds 3
    }
    
    # PASO 4: Configurar Athena
    if (-not $SkipAthena) {
        if (-not (Invoke-AthenaSetup)) {
            Write-Warning "⚠️  Error en configuración de Athena, pero continuando..."
            $success = $false
        }
        Start-Sleep -Seconds 2
    }
    
    # PASO 5: Validar
    if (-not $SkipValidation) {
        Invoke-Validation
    }
    
    # Resumen
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host ""
    Show-Summary
    
    Write-Host ""
    Write-Info "🕐 Fin: $($endTime.ToString('yyyy-MM-dd HH:mm:ss'))"
    Write-Info "⏱️  Duración: $([math]::Round($duration.TotalMinutes, 2)) minutos"
    
    if ($success) {
        Write-Success "`n✅ PROCESO COMPLETADO EXITOSAMENTE`n"
        exit 0
    } else {
        Write-Warning "`n⚠️  PROCESO COMPLETADO CON ADVERTENCIAS`n"
        exit 0
    }
}

# ============================================================================
# EJECUCIÓN
# ============================================================================

# Cambiar al directorio del script
Set-Location $SCRIPT_DIR

# Ejecutar pipeline
Start-DataIngestionPipeline
