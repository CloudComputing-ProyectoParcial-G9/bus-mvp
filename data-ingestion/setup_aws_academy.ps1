# AWS Academy Lab - Quick Setup Script
# Para Windows PowerShell

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "AWS Academy Lab - Credentials Setup" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Este script te ayudara a configurar las credenciales de AWS Academy Lab" -ForegroundColor Yellow
Write-Host ""
Write-Host "Pasos:" -ForegroundColor Blue
Write-Host "1. Ve a AWS Academy - Learner Lab"
Write-Host "2. Click en AWS Details (arriba a la derecha)"
Write-Host "3. Click en Show junto a AWS CLI"
Write-Host "4. Copia las credenciales"
Write-Host ""

if (Test-Path ".env") {
    Write-Host "El archivo .env ya existe." -ForegroundColor Yellow
    $overwrite = Read-Host "Quieres sobrescribirlo? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Cancelado." -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "Ahora ingresa las credenciales de AWS Academy:" -ForegroundColor Blue
Write-Host ""

Write-Host "AWS Access Key ID:" -ForegroundColor Yellow
$access_key = Read-Host
Write-Host ""

Write-Host "AWS Secret Access Key:" -ForegroundColor Yellow
$secret_key = Read-Host
Write-Host ""

Write-Host "AWS Session Token (el mas largo):" -ForegroundColor Yellow
$session_token = Read-Host
Write-Host ""

if ($access_key -and $secret_key -and $session_token) {
    # Primero configurar las credenciales para obtener el Account ID
    $env:AWS_ACCESS_KEY_ID = $access_key
    $env:AWS_SECRET_ACCESS_KEY = $secret_key
    $env:AWS_SESSION_TOKEN = $session_token
    $env:AWS_DEFAULT_REGION = "us-east-1"
    
    Write-Host "Verificando credenciales..." -ForegroundColor Blue
    
    try {
        $identity = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" sts get-caller-identity 2>$null | ConvertFrom-Json
        
        Write-Host "Credenciales validas" -ForegroundColor Green
        Write-Host ""
        Write-Host "Account ID: $($identity.Account)" -ForegroundColor Green
        Write-Host "User ARN: $($identity.Arn)" -ForegroundColor Green
        Write-Host ""
        
        $accountId = $identity.Account
        
        # Crear archivo .env con Account ID incluido
        $envContent = @"
# AWS Credentials - AWS Academy Lab
AWS_ACCESS_KEY_ID=$access_key
AWS_SECRET_ACCESS_KEY=$secret_key
AWS_SESSION_TOKEN=$session_token
AWS_DEFAULT_REGION=us-east-1
AWS_ACCOUNT_ID=$accountId

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

# Ingestion Schedule (optional)
INGESTION_INTERVAL=3600
"@

        Set-Content -Path ".env" -Value $envContent
        
        Write-Host "Credenciales configuradas exitosamente" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "IMPORTANTE: Actualiza el script setup_glue.py" -ForegroundColor Yellow
        Write-Host "Edita: scripts\setup_glue.py"
        Write-Host "Reemplaza: YOUR_ACCOUNT_ID con: $accountId"
        Write-Host ""
        
        Write-Host "==============================================" -ForegroundColor Green
        Write-Host "Setup completado!" -ForegroundColor Green
        Write-Host "==============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Proximos pasos:"
        Write-Host "1. El Account ID ($accountId) ya fue agregado al archivo .env" -ForegroundColor Green
        Write-Host "2. Crear bucket S3: python scripts\setup_s3.py"
        Write-Host "3. Configurar Glue: python scripts\setup_glue.py"
        Write-Host "4. Ejecutar ingesta: docker-compose up"
        Write-Host ""
        Write-Host "RECORDATORIO: Las credenciales expiran en 4 horas" -ForegroundColor Yellow
        Write-Host ""
        
    } catch {
        Write-Host "Error: Credenciales invalidas" -ForegroundColor Red
        Write-Host "Por favor verifica que copiaste correctamente desde AWS Academy"
        exit 1
    }
    
} else {
    Write-Host "Error: No se ingresaron todas las credenciales" -ForegroundColor Red
    exit 1
}
