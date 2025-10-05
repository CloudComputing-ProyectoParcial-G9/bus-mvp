# ============================================================================
# Script de Verificación y Ejecución Completa - Bus MVP Data Analytics
# ============================================================================
# Propósito: Automatizar l    finally {
        Pop-Location
    }
}

function Start-AthenaTablesCreation {
    Write-Banner "CREANDO TABLAS EN ATHENA"
    
    Push-Location $DATA_INGESTION_DIR
    
    try {
        $setupScript = Join-Path "scripts" "create_athena_tables.py"
        if (-not (Test-Path $setupScript)) {
            Write-Error "❌ Script create_athena_tables.py no encontrado"
            return
        }
        
        Write-Info "🚀 Creando tablas en Athena..."
        python $setupScript
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Tablas creadas en Athena"
        } else {
            Write-Error "❌ Error creando tablas"
        }
    } catch {
        Write-Error "❌ Error ejecutando script: $_"
    } finally {
        Pop-Location
    }
}

function Start-AthenaQueries {
    Write-Banner "EJECUTANDO 4 CONSULTAS SQL EN ATHENA"
    
    Push-Location $DATA_INGESTION_DIR
    
    try {
        $setupScript = Join-Path "scripts" "run_athena_queries.py"
        if (-not (Test-Path $setupScript)) {
            Write-Error "❌ Script run_athena_queries.py no encontrado"
            return
        }
        
        Write-Info "🚀 Ejecutando consultas SQL..."
        python $setupScript
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Consultas ejecutadas exitosamente"
            Write-Info "📦 Resultados guardados en: s3://bus-mvp-datalake/athena-results/"
        } else {
            Write-Error "❌ Error ejecutando consultas"
        }
    } catch {
        Write-Error "❌ Error ejecutando script: $_"
    } finally {
        Pop-Location
    }
}

function Start-AthenaViews {
    Write-Banner "CREANDO 2 VISTAS EN ATHENA"
    
    Push-Location $DATA_INGESTION_DIR
    
    try {
        $setupScript = Join-Path "scripts" "create_athena_views.py"
        if (-not (Test-Path $setupScript)) {
            Write-Error "❌ Script create_athena_views.py no encontrado"
            return
        }
        
        Write-Info "🚀 Creando vistas en Athena..."
        python $setupScript
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Vistas creadas exitosamente"
            Write-Info "📊 Vistas disponibles: passenger_sales_summary, trip_occupancy_revenue"
        } else {
            Write-Error "❌ Error creando vistas"
        }
    } catch {
        Write-Error "❌ Error ejecutando script: $_"
    } finally {
        Pop-Location
    }
}

function Show-NextSteps {ficación y ejecución de todos los requisitos
# Plataforma: Windows PowerShell
# ============================================================================

param(
    [switch]$CheckOnly,
    [switch]$SkipIngestion,
    [switch]$SkipGlue
)

# Configuración
$ErrorActionPreference = "Continue"
$PROJECT_ROOT = "C:\Users\luisf\CS\cloudcomputing\bus-mvp"
$DATA_INGESTION_DIR = Join-Path $PROJECT_ROOT "data-ingestion"

# Colores para output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Banner { 
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Magenta
    Write-Host $args -ForegroundColor Magenta
    Write-Host ("=" * 70) -ForegroundColor Magenta
    Write-Host ""
}

# ============================================================================
# FUNCIONES DE VERIFICACIÓN
# ============================================================================

function Test-DockerRunning {
    Write-Info "🔍 Verificando Docker..."
    try {
        $dockerInfo = docker info 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Docker está corriendo"
            return $true
        }
    } catch {
        Write-Error "❌ Docker no está disponible"
        return $false
    }
    return $false
}

function Test-AWSCredentials {
    Write-Info "🔍 Verificando credenciales AWS..."
    
    $envFile = Join-Path $DATA_INGESTION_DIR ".env"
    if (-not (Test-Path $envFile)) {
        Write-Warning "⚠️  Archivo .env no encontrado"
        Write-Info "📝 Creando .env desde .env.example..."
        
        $exampleFile = Join-Path $DATA_INGESTION_DIR ".env.example"
        if (Test-Path $exampleFile) {
            Copy-Item $exampleFile $envFile
            Write-Warning "⚠️  Por favor edita $envFile con tus credenciales AWS"
            return $false
        } else {
            Write-Error "❌ No se encontró .env.example"
            return $false
        }
    }
    
    # Verificar que tenga las credenciales necesarias
    $content = Get-Content $envFile -Raw
    $hasAccessKey = $content -match "AWS_ACCESS_KEY_ID=.+"
    $hasSecretKey = $content -match "AWS_SECRET_ACCESS_KEY=.+"
    
    if ($hasAccessKey -and $hasSecretKey) {
        Write-Success "✅ Credenciales AWS configuradas en .env"
        return $true
    } else {
        Write-Warning "⚠️  Credenciales AWS incompletas en .env"
        return $false
    }
}

function Test-MicroservicesRunning {
    Write-Info "🔍 Verificando microservicios..."
    
    $containers = docker ps --format "{{.Names}}" 2>&1
    $required = @("ms-passengers", "ms-trips", "ms-tickets")
    $running = @()
    
    foreach ($service in $required) {
        if ($containers -match $service) {
            Write-Success "  ✅ $service está corriendo"
            $running += $service
        } else {
            Write-Warning "  ⚠️  $service no está corriendo"
        }
    }
    
    if ($running.Count -eq $required.Count) {
        Write-Success "✅ Todos los microservicios están corriendo"
        return $true
    } else {
        Write-Warning "⚠️  Faltan microservicios por iniciar"
        Write-Info "💡 Ejecuta: docker-compose up -d en el directorio raíz"
        return $false
    }
}

function Test-S3Bucket {
    Write-Info "🔍 Verificando bucket S3..."
    
    try {
        $bucketName = (Get-Content (Join-Path $DATA_INGESTION_DIR ".env") | 
                      Where-Object { $_ -match "S3_BUCKET=" }) -replace "S3_BUCKET=", ""
        
        if (-not $bucketName) {
            Write-Warning "⚠️  Variable S3_BUCKET no configurada"
            return $false
        }
        
        $result = aws s3 ls "s3://$bucketName" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Bucket S3 accesible: $bucketName"
            return $true
        } else {
            Write-Warning "⚠️  No se puede acceder al bucket: $bucketName"
            return $false
        }
    } catch {
        Write-Error "❌ Error verificando S3: $_"
        return $false
    }
}

function Test-DataInS3 {
    Write-Info "🔍 Verificando datos en S3..."
    
    $bucketName = (Get-Content (Join-Path $DATA_INGESTION_DIR ".env") | 
                  Where-Object { $_ -match "S3_BUCKET=" }) -replace "S3_BUCKET=", ""
    
    $paths = @("raw/passengers_csv/", "raw/trips_csv/", "raw/tickets_csv/")
    $allGood = $true
    
    foreach ($path in $paths) {
        $result = aws s3 ls "s3://$bucketName/$path" 2>&1
        if ($LASTEXITCODE -eq 0 -and $result) {
            $count = ($result | Measure-Object).Count
            Write-Success "  ✅ $path : $count archivo(s)"
        } else {
            Write-Warning "  ⚠️  $path : Sin archivos"
            $allGood = $false
        }
    }
    
    return $allGood
}

function Test-GlueDatabase {
    Write-Info "🔍 Verificando AWS Glue Database..."
    
    $dbName = (Get-Content (Join-Path $DATA_INGESTION_DIR ".env") | 
              Where-Object { $_ -match "GLUE_DATABASE=" }) -replace "GLUE_DATABASE=", ""
    
    if (-not $dbName) {
        $dbName = "bus_mvp_db"
    }
    
    try {
        $result = aws glue get-database --name $dbName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Database Glue existe: $dbName"
            return $true
        } else {
            Write-Warning "⚠️  Database Glue no encontrada: $dbName"
            return $false
        }
    } catch {
        Write-Warning "⚠️  No se pudo verificar Glue Database"
        return $false
    }
}

function Test-GlueTables {
    Write-Info "🔍 Verificando tablas en Glue Catalog..."
    
    $dbName = "bus_mvp_db"
    
    try {
        $result = aws glue get-tables --database-name $dbName --output json 2>&1 | ConvertFrom-Json
        $tables = $result.TableList
        
        if ($tables.Count -gt 0) {
            Write-Success "✅ Tablas encontradas: $($tables.Count)"
            foreach ($table in $tables) {
                Write-Info "  📊 $($table.Name)"
            }
            return $true
        } else {
            Write-Warning "⚠️  No se encontraron tablas en el catálogo"
            return $false
        }
    } catch {
        Write-Warning "⚠️  No se pudieron listar las tablas"
        return $false
    }
}

# ============================================================================
# FUNCIONES DE EJECUCIÓN
# ============================================================================

function Start-DataIngestion {
    Write-Banner "EJECUTANDO INGESTA DE DATOS"
    
    Push-Location $DATA_INGESTION_DIR
    
    try {
        Write-Info "🚀 Iniciando contenedor passengers-ingestion..."
        docker-compose up passengers-ingestion
        
        Write-Info "🚀 Iniciando contenedor trips-ingestion..."
        docker-compose up trips-ingestion
        
        Write-Info "🚀 Iniciando contenedor tickets-ingestion..."
        docker-compose up tickets-ingestion
        
        Write-Success "✅ Ingesta completada"
    } catch {
        Write-Error "❌ Error durante la ingesta: $_"
    } finally {
        Pop-Location
    }
}

function Start-GlueSetup {
    Write-Banner "CONFIGURANDO AWS GLUE"
    
    Push-Location $DATA_INGESTION_DIR
    
    try {
        # Verificar que exista el script
        $setupScript = Join-Path "scripts" "setup_complete_glue.py"
        if (-not (Test-Path $setupScript)) {
            Write-Error "❌ Script setup_complete_glue.py no encontrado"
            return
        }
        
        Write-Info "🚀 Ejecutando setup de Glue..."
        python $setupScript
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Setup de Glue completado"
        } else {
            Write-Error "❌ Error en setup de Glue"
        }
    } catch {
        Write-Error "❌ Error ejecutando Glue setup: $_"
    } finally {
        Pop-Location
    }
}

function Show-NextSteps {
    Write-Banner "PRÓXIMOS PASOS"
    
    Write-Info "📋 Para completar todos los requisitos, ejecuta:"
    Write-Host ""
    Write-Host "1. Ejecutar Consultas SQL en Athena:" -ForegroundColor Yellow
    Write-Host "   - Abre: https://console.aws.amazon.com/athena/" -ForegroundColor Gray
    Write-Host "   - Selecciona Database: bus_mvp_db" -ForegroundColor Gray
    Write-Host "   - Ejecuta queries de: docs/analytics/athena_queries.sql" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Crear Vistas en Athena:" -ForegroundColor Yellow
    Write-Host "   - Ejecuta CREATE VIEW de: docs/analytics/athena_views.sql" -ForegroundColor Gray
    Write-Host "   - Verifica con: SHOW VIEWS;" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Generar Evidencias:" -ForegroundColor Yellow
    Write-Host "   - Captura screenshots de cada paso" -ForegroundColor Gray
    Write-Host "   - Exporta diagrama ER a imagen" -ForegroundColor Gray
    Write-Host "   - Organiza en carpeta evidencias/" -ForegroundColor Gray
    Write-Host ""
}

function Show-ComplianceSummary {
    Write-Banner "RESUMEN DE CUMPLIMIENTO"
    
    $checks = @(
        @{ Name = "MV ingesta (Docker)"; Status = (Test-DockerRunning) },
        @{ Name = "Bucket S3"; Status = (Test-S3Bucket) },
        @{ Name = "Datos en S3"; Status = (Test-DataInS3) },
        @{ Name = "Glue Database"; Status = (Test-GlueDatabase) },
        @{ Name = "Glue Tables"; Status = (Test-GlueTables) }
    )
    
    $completed = 0
    foreach ($check in $checks) {
        $status = if ($check.Status) { "✅"; $completed++ } else { "❌" }
        Write-Host "$status $($check.Name)" -ForegroundColor $(if ($check.Status) { "Green" } else { "Red" })
    }
    
    Write-Host ""
    Write-Host "Completado: $completed/$($checks.Count)" -ForegroundColor $(if ($completed -eq $checks.Count) { "Green" } else { "Yellow" })
    Write-Host ""
    
    Write-Info "📄 Archivos creados:"
    Write-Host "  ✅ docs/analytics/data_catalog_er.md (Diagrama ER)" -ForegroundColor Green
    Write-Host "  ✅ docs/analytics/athena_queries.sql (4 Consultas)" -ForegroundColor Green
    Write-Host "  ✅ docs/analytics/athena_views.sql (2 Vistas)" -ForegroundColor Green
    Write-Host "  ✅ data-ingestion/scripts/setup_complete_glue.py" -ForegroundColor Green
    Write-Host "  ✅ GUIA_VERIFICACION_REQUISITOS.md" -ForegroundColor Green
    Write-Host ""
}

# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║           BUS MVP - DATA ANALYTICS SETUP & VERIFICATION            ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  1. Verificar Requisitos (Check Only)" -ForegroundColor Cyan
    Write-Host "  2. Ejecutar Ingesta de Datos" -ForegroundColor Cyan
    Write-Host "  3. Configurar AWS Glue (Database + Crawlers)" -ForegroundColor Cyan
    Write-Host "  4. Crear Tablas en Athena" -ForegroundColor Cyan
    Write-Host "  5. Ejecutar 4 Consultas SQL en Athena" -ForegroundColor Yellow
    Write-Host "  6. Crear 2 Vistas en Athena" -ForegroundColor Yellow
    Write-Host "  7. Ejecutar TODO (Ingesta + Glue + Athena)" -ForegroundColor Green
    Write-Host "  8. Ver Resumen de Cumplimiento" -ForegroundColor Cyan
    Write-Host "  9. Abrir Guía de Verificación" -ForegroundColor Cyan
    Write-Host "  0. Salir" -ForegroundColor Gray
    Write-Host ""
    
    $choice = Read-Host "Selecciona una opción"
    return $choice
}

# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if ($CheckOnly) {
    Show-ComplianceSummary
    Show-NextSteps
    exit
}

# Modo interactivo
while ($true) {
    $choice = Show-Menu
    
    switch ($choice) {
        "1" {
            Write-Banner "VERIFICANDO REQUISITOS"
            Test-DockerRunning
            Test-AWSCredentials
            Test-MicroservicesRunning
            Test-S3Bucket
            Test-DataInS3
            Test-GlueDatabase
            Test-GlueTables
            Write-Host ""
            Read-Host "Presiona Enter para continuar"
        }
        "2" {
            if (-not $SkipIngestion) {
                if (Test-MicroservicesRunning -and Test-AWSCredentials) {
                    Start-DataIngestion
                    Test-DataInS3
                } else {
                    Write-Warning "⚠️  Prerequisitos no cumplidos"
                }
            }
            Read-Host "Presiona Enter para continuar"
        }
        "3" {
            if (-not $SkipGlue) {
                if (Test-DataInS3) {
                    Start-GlueSetup
                    Test-GlueDatabase
                    Test-GlueTables
                } else {
                    Write-Warning "⚠️  Primero ejecuta la ingesta de datos"
                }
            }
            Read-Host "Presiona Enter para continuar"
        }
        "4" {
            if (Test-DataInS3) {
                Start-AthenaTablesCreation
            } else {
                Write-Warning "⚠️  Primero ejecuta la ingesta de datos"
            }
            Read-Host "Presiona Enter para continuar"
        }
        "5" {
            if (Test-GlueTables) {
                Start-AthenaQueries
            } else {
                Write-Warning "⚠️  Primero crea las tablas en Athena (opción 3 o 4)"
            }
            Read-Host "Presiona Enter para continuar"
        }
        "6" {
            if (Test-GlueTables) {
                Start-AthenaViews
            } else {
                Write-Warning "⚠️  Primero crea las tablas en Athena (opción 3 o 4)"
            }
            Read-Host "Presiona Enter para continuar"
        }
        "7" {
            Write-Banner "EJECUCIÓN COMPLETA"
            
            if (Test-MicroservicesRunning -and Test-AWSCredentials) {
                Start-DataIngestion
                Start-Sleep -Seconds 5
                
                if (Test-DataInS3) {
                    Start-GlueSetup
                    Start-Sleep -Seconds 5
                    
                    if (Test-GlueDatabase) {
                        Start-AthenaTablesCreation
                        Start-Sleep -Seconds 3
                        
                        Start-AthenaQueries
                        Start-Sleep -Seconds 3
                        
                        Start-AthenaViews
                    }
                }
            }
            
            Show-ComplianceSummary
            Show-NextSteps
            Read-Host "Presiona Enter para continuar"
        }
        "8" {
            Write-Banner "EJECUCIÓN COMPLETA"
            
            if (Test-MicroservicesRunning -and Test-AWSCredentials) {
                Start-DataIngestion
                Start-Sleep -Seconds 5
                
                if (Test-DataInS3) {
                    Start-GlueSetup
                }
            }
            
            Show-ComplianceSummary
            Show-NextSteps
            Read-Host "Presiona Enter para continuar"
        }
        "8" {
            Show-ComplianceSummary
            Show-NextSteps
            Read-Host "Presiona Enter para continuar"
        }
        "9" {
            $guideFile = Join-Path $PROJECT_ROOT "GUIA_VERIFICACION_REQUISITOS.md"
            if (Test-Path $guideFile) {
                Start-Process $guideFile
                Write-Success "✅ Abriendo guía de verificación..."
            } else {
                Write-Error "❌ Guía no encontrada"
            }
            Read-Host "Presiona Enter para continuar"
        }
        "0" {
            Write-Info "👋 ¡Hasta luego!"
            exit
        }
        default {
            Write-Warning "⚠️  Opción inválida"
            Start-Sleep -Seconds 1
        }
    }
}
