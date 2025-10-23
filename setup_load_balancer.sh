#!/bin/bash

# ============================================
# Script de Configuración del Load Balancer
# ============================================
# Este script configura automáticamente:
# - Security Groups
# - Target Groups para cada microservicio
# - Listeners en el Load Balancer
# - Registro de instancias en los Target Groups
# ============================================

set -e  # Exit on error

echo "============================================"
echo "🚀 CONFIGURACIÓN DEL LOAD BALANCER AWS"
echo "============================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mensajes
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Verificar AWS CLI
if ! command -v aws &> /dev/null; then
    log_error "AWS CLI no está instalado"
    exit 1
fi

log_success "AWS CLI instalado"

# Verificar credenciales
log_info "Verificando credenciales AWS..."
if ! aws sts get-caller-identity &> /dev/null; then
    log_error "Credenciales AWS inválidas o expiradas"
    log_warning "Ejecuta: cd /root/bus-mvp/data-ingestion && ./setup_aws_academy.sh"
    exit 1
fi

log_success "Credenciales AWS válidas"

# Variables de configuración
REGION="us-east-1"
LB_DNS="LB-Prod-308585431.us-east-1.elb.amazonaws.com"
INSTANCE_1_IP="54.161.1.30"
INSTANCE_2_IP="52.200.140.111"

echo ""
log_info "Configuración:"
echo "  - Región: $REGION"
echo "  - Load Balancer: $LB_DNS"
echo "  - Instancia 1: $INSTANCE_1_IP"
echo "  - Instancia 2: $INSTANCE_2_IP"
echo ""

# 1. Obtener información del Load Balancer
log_info "[1/8] Obteniendo información del Load Balancer..."

LB_ARN=$(aws elbv2 describe-load-balancers \
  --region $REGION \
  --query "LoadBalancers[?DNSName=='$LB_DNS'].LoadBalancerArn" \
  --output text 2>/dev/null || echo "")

if [ -z "$LB_ARN" ]; then
    log_error "No se encontró el Load Balancer con DNS: $LB_DNS"
    log_warning "Verifica que el Load Balancer existe en AWS"
    exit 1
fi

log_success "Load Balancer ARN: ${LB_ARN:0:50}..."

# Obtener Security Group del LB
LB_SG_ID=$(aws elbv2 describe-load-balancers \
  --load-balancer-arns $LB_ARN \
  --region $REGION \
  --query "LoadBalancers[0].SecurityGroups[0]" \
  --output text)

log_success "Security Group del LB: $LB_SG_ID"

# 2. Configurar Security Groups
log_info "[2/8] Configurando Security Groups del Load Balancer..."

for PORT in 8001 8002 8003 8004 8005; do
    # Verificar si la regla ya existe
    RULE_EXISTS=$(aws ec2 describe-security-groups \
      --group-ids $LB_SG_ID \
      --region $REGION \
      --query "SecurityGroups[0].IpPermissions[?FromPort==\`$PORT\`]" \
      --output text)

    if [ -z "$RULE_EXISTS" ]; then
        log_info "Agregando regla para puerto $PORT..."
        aws ec2 authorize-security-group-ingress \
          --group-id $LB_SG_ID \
          --protocol tcp \
          --port $PORT \
          --cidr 0.0.0.0/0 \
          --region $REGION 2>/dev/null && log_success "Puerto $PORT configurado" || log_warning "Puerto $PORT ya existe o error"
    else
        log_success "Puerto $PORT ya configurado"
    fi
done

# 3. Obtener VPC ID
log_info "[3/8] Obteniendo VPC ID..."

VPC_ID=$(aws elbv2 describe-load-balancers \
  --load-balancer-arns $LB_ARN \
  --region $REGION \
  --query "LoadBalancers[0].VpcId" \
  --output text)

log_success "VPC ID: $VPC_ID"

# 4. Obtener IDs de instancias
log_info "[4/8] Obteniendo IDs de instancias..."

INSTANCE_1=$(aws ec2 describe-instances \
  --filters "Name=ip-address,Values=$INSTANCE_1_IP" \
  --region $REGION \
  --query "Reservations[0].Instances[0].InstanceId" \
  --output text 2>/dev/null || echo "")

INSTANCE_2=$(aws ec2 describe-instances \
  --filters "Name=ip-address,Values=$INSTANCE_2_IP" \
  --region $REGION \
  --query "Reservations[0].Instances[0].InstanceId" \
  --output text 2>/dev/null || echo "")

if [ "$INSTANCE_1" != "None" ] && [ ! -z "$INSTANCE_1" ]; then
    log_success "Instancia 1: $INSTANCE_1"
else
    log_warning "Instancia 1 no encontrada ($INSTANCE_1_IP)"
    INSTANCE_1=""
fi

if [ "$INSTANCE_2" != "None" ] && [ ! -z "$INSTANCE_2" ]; then
    log_success "Instancia 2: $INSTANCE_2"
else
    log_warning "Instancia 2 no encontrada ($INSTANCE_2_IP)"
    INSTANCE_2=""
fi

if [ -z "$INSTANCE_1" ] && [ -z "$INSTANCE_2" ]; then
    log_error "No se encontraron instancias. Verifica las IPs."
    exit 1
fi

# 5. Crear Target Groups
log_info "[5/8] Creando/verificando Target Groups..."

declare -A SERVICES=(
    ["passengers"]="8001:/api/v1/passengers"
    ["trips"]="8002:/api/v1/trips"
    ["tickets"]="8003:/actuator/health"
    ["history"]="8004:/health"
    ["analytics"]="8005:/api/v1/analytics"
)

declare -A TG_ARNS

for SERVICE in "${!SERVICES[@]}"; do
    IFS=':' read -r PORT HEALTH_PATH <<< "${SERVICES[$SERVICE]}"
    TG_NAME="tg-$SERVICE"

    # Verificar si el Target Group ya existe
    TG_ARN=$(aws elbv2 describe-target-groups \
      --names $TG_NAME \
      --region $REGION \
      --query "TargetGroups[0].TargetGroupArn" \
      --output text 2>/dev/null || echo "")

    if [ "$TG_ARN" == "None" ] || [ -z "$TG_ARN" ]; then
        log_info "Creando Target Group para $SERVICE..."
        TG_ARN=$(aws elbv2 create-target-group \
          --name $TG_NAME \
          --protocol HTTP \
          --port $PORT \
          --vpc-id $VPC_ID \
          --health-check-enabled \
          --health-check-path $HEALTH_PATH \
          --health-check-interval-seconds 30 \
          --health-check-timeout-seconds 10 \
          --healthy-threshold-count 2 \
          --unhealthy-threshold-count 3 \
          --region $REGION \
          --query "TargetGroups[0].TargetGroupArn" \
          --output text 2>/dev/null || echo "")

        if [ ! -z "$TG_ARN" ] && [ "$TG_ARN" != "None" ]; then
            log_success "Target Group creado para $SERVICE"
        else
            log_error "Error creando Target Group para $SERVICE"
            continue
        fi
    else
        log_success "Target Group existe para $SERVICE"
    fi

    TG_ARNS[$SERVICE]=$TG_ARN
done

# 6. Registrar instancias en Target Groups
log_info "[6/8] Registrando instancias en Target Groups..."

for SERVICE in "${!TG_ARNS[@]}"; do
    TG_ARN=${TG_ARNS[$SERVICE]}

    if [ ! -z "$TG_ARN" ] && [ "$TG_ARN" != "None" ]; then
        log_info "Registrando instancias en tg-$SERVICE..."

        # Preparar lista de targets
        TARGETS=""
        if [ ! -z "$INSTANCE_1" ]; then
            TARGETS="Id=$INSTANCE_1"
        fi
        if [ ! -z "$INSTANCE_2" ]; then
            if [ ! -z "$TARGETS" ]; then
                TARGETS="$TARGETS Id=$INSTANCE_2"
            else
                TARGETS="Id=$INSTANCE_2"
            fi
        fi

        if [ ! -z "$TARGETS" ]; then
            aws elbv2 register-targets \
              --target-group-arn $TG_ARN \
              --targets $TARGETS \
              --region $REGION 2>/dev/null && log_success "Instancias registradas en tg-$SERVICE" || log_warning "Error registrando instancias (pueden ya estar registradas)"
        fi
    fi
done

# 7. Crear Listeners
log_info "[7/8] Creando/verificando Listeners..."

for SERVICE in "${!SERVICES[@]}"; do
    IFS=':' read -r PORT HEALTH_PATH <<< "${SERVICES[$SERVICE]}"
    TG_ARN=${TG_ARNS[$SERVICE]}

    if [ ! -z "$TG_ARN" ] && [ "$TG_ARN" != "None" ]; then
        # Verificar si el listener ya existe
        LISTENER_EXISTS=$(aws elbv2 describe-listeners \
          --load-balancer-arn $LB_ARN \
          --region $REGION \
          --query "Listeners[?Port==\`$PORT\`]" \
          --output text 2>/dev/null || echo "")

        if [ -z "$LISTENER_EXISTS" ]; then
            log_info "Creando Listener para puerto $PORT ($SERVICE)..."
            aws elbv2 create-listener \
              --load-balancer-arn $LB_ARN \
              --protocol HTTP \
              --port $PORT \
              --default-actions Type=forward,TargetGroupArn=$TG_ARN \
              --region $REGION &>/dev/null && log_success "Listener creado para puerto $PORT" || log_error "Error creando Listener para puerto $PORT"
        else
            log_success "Listener ya existe para puerto $PORT"
        fi
    fi
done

# 8. Configurar Security Groups de las instancias
log_info "[8/8] Configurando Security Groups de las instancias..."

# Obtener Security Group de las instancias
if [ ! -z "$INSTANCE_1" ]; then
    INSTANCE_SG=$(aws ec2 describe-instances \
      --instance-ids $INSTANCE_1 \
      --region $REGION \
      --query "Reservations[0].Instances[0].SecurityGroups[0].GroupId" \
      --output text)

    log_info "Security Group de instancias: $INSTANCE_SG"

    # Permitir tráfico desde el Load Balancer
    for PORT in 8001 8002 8003 8004 8005; do
        aws ec2 authorize-security-group-ingress \
          --group-id $INSTANCE_SG \
          --protocol tcp \
          --port $PORT \
          --source-group $LB_SG_ID \
          --region $REGION 2>/dev/null && log_success "Regla agregada para puerto $PORT desde LB" || log_warning "Regla ya existe para puerto $PORT"
    done
fi

echo ""
echo "============================================"
log_success "CONFIGURACIÓN COMPLETADA"
echo "============================================"
echo ""

# Verificar health de targets
log_info "Verificando salud de targets (esto puede tomar unos segundos)..."
echo ""

sleep 5

for SERVICE in "${!TG_ARNS[@]}"; do
    TG_ARN=${TG_ARNS[$SERVICE]}

    if [ ! -z "$TG_ARN" ] && [ "$TG_ARN" != "None" ]; then
        echo "Target Group: tg-$SERVICE"
        aws elbv2 describe-target-health \
          --target-group-arn $TG_ARN \
          --region $REGION \
          --query "TargetHealthDescriptions[*].{Target:Target.Id,Health:TargetHealth.State,Reason:TargetHealth.Reason}" \
          --output table 2>/dev/null || echo "  No se pudo verificar salud"
        echo ""
    fi
done

echo "============================================"
echo "📋 RESUMEN"
echo "============================================"
echo ""
log_info "Load Balancer: $LB_DNS"
log_info "Endpoints disponibles:"
echo "  - http://$LB_DNS:8001/api/v1/passengers"
echo "  - http://$LB_DNS:8002/api/v1/trips"
echo "  - http://$LB_DNS:8003/actuator/health"
echo "  - http://$LB_DNS:8004/health"
echo "  - http://$LB_DNS:8005/api/v1/analytics"
echo ""

log_warning "NOTA: Puede tomar 1-2 minutos para que los health checks pasen a 'healthy'"
echo ""

log_info "Para verificar manualmente:"
echo "  curl http://$LB_DNS:8001/api/v1/passengers"
echo ""

echo "============================================"
