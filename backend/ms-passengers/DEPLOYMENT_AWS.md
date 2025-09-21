# Despliegue en AWS EC2 (guía práctica)

Esta guía explica los pasos para dejar `ms-passengers` listo para ejecutarse en una máquina virtual EC2 con Docker Compose, usando imágenes almacenadas en Amazon ECR.

Resumen rápido
- Construir y probar la imagen localmente o por CI.
- Publicar la imagen en Amazon ECR.
- Preparar una EC2 con Docker y Docker Compose.
- Subir un `infra/.env.production` con variables de entorno (o usar Secrets Manager/SSM).
- Ejecutar `docker compose -f docker-compose.prod.yml up -d` en la VM.

Requisitos previos
- Cuenta AWS con permisos para ECR, EC2 y (opcional) RDS / Secrets Manager.
- AWS CLI instalado y configurado (credenciales con permisos ECR).
- EC2 (Amazon Linux 2, Ubuntu 22.04 u otra) con acceso SSH y security group que permita los puertos que necesites (22, 8001, 8088, 5432 si usas DB local, etc.).

Decisiones de arquitectura recomendadas
- Producción: usar RDS (Postgres) en lugar de ejecutar Postgres en la misma VM. RDS ofrece backups, alta disponibilidad y seguridad.
- Para un deploy rápido de prueba, puedes levantar Postgres en un contenedor en la misma VM (no recomendado para producción).
- Guardar secretos en AWS Secrets Manager o SSM Parameter Store (evitar `.env` con credenciales en el repo).

Paso A — Preparar y publicar la imagen en ECR
1. Crea el repositorio (una vez):

```powershell
# Reemplaza REGION y ACCOUNT_ID
aws ecr create-repository --repository-name bus-mvp-ms-passengers --region REGION
```

2. Login en ECR y push (ejemplo):

```powershell
$REGION = "us-east-1"
$ACCOUNT_ID = "<tu-account-id>"
$REPO = "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/bus-mvp-ms-passengers"

# Login
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build local (desde la raíz del repo)
docker build -t ms-passengers:latest -f backend/ms-passengers/Dockerfile backend/ms-passengers

docker tag ms-passengers:latest $REPO:latest

docker push $REPO:latest
```

Sugerencia: haz esto en CI (GitHub Actions/GitLab CI) para que cada merge/deployment publique automáticamente la imagen.

Paso B — Preparar EC2 (máquina virtual)
1. Provisiona una EC2 (Ubuntu o Amazon Linux 2), configura Security Group (puertos 22, 8001, 8088, 5432 si usas DB local).
2. Conéctate por SSH y instala Docker + Docker Compose plugin:

```bash
# Ubuntu (ejemplo)
sudo apt update && sudo apt install -y ca-certificates curl gnupg lsb-release
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Instalar plugin docker compose (opcional)
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. Configura credenciales AWS en la VM o utiliza roles de instancia (mejor):
- Usar IAM Role con permiso ECR (AmazonEC2ContainerRegistryReadOnly) evita almacenar credenciales.

Paso C — Configurar `.env` en la VM
- Opción 1 (rápida): crear `infra/.env.production` local en la VM con las variables necesarias (ejemplo en `infra/.env.production.example`).
- Opción 2 (recomendada): almacenar secretos en AWS Secrets Manager o SSM y leerlos desde un script que genere `/home/ubuntu/infra/.env.production` en el arranque.

Paso D — Ejecutar en la VM (usar imágenes ECR)
1. Pull de imágenes y levantar:

```bash
# En la VM
export ECR_REGISTRY="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
# Opcional: login con aws cli si no usas IAM Role
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Clona repo o sube solo el docker-compose.prod.yml y .env.production
cd /home/ubuntu/bus-mvp/infra
# Edita .env.production con variables (o genera desde Secrets Manager)

# Levantar (usa la versión de compose apropiada)
docker compose -f docker-compose.prod.yml up -d
```

Paso E — Migrations y esquemas
- Recomendado: integrar Alembic para gestionar migraciones de esquema. Pasos básicos si Alembic existe:
  - `docker run --rm -e DATABASE_URL="$DATABASE_URL" $REPO alembic upgrade head`
- Si no hay migraciones, la app actualmente hace `create_all()`; en producción esto puede estar bien para pruebas, pero Alembic es la práctica recomendada.

Paso F — Logs, monitor y backups
- Logs: configurar CloudWatch Logs (driver awslogs en Compose) o montar volúmenes y enviar a un colector.
- Backups DB: si usas RDS, habilita snapshots automáticos. Si usas contenedor Postgres, programa `pg_dump` a S3.

Paso G — Seguridad y HTTPS
- Para exponer tu servicio públicamente, usa un ALB (Application Load Balancer) con certificado ACM (HTTPS) en lugar de exponer puertos directamente.
- Alternativa: instalar nginx y certbot en la VM para TLS (no recomendado si usas ALB).

Paso H — CI/CD (ejemplo GitHub Actions)
- Workflows típicos:
  1. Build + test
  2. Build Docker image + push to ECR
  3. SSH to EC2 and `docker compose pull && docker compose up -d` (o usar SSM Run Command)

Ejemplo simplificado (pseudocódigo):
```yaml
# .github/workflows/deploy.yml (simplified)
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-region: ${{ secrets.AWS_REGION }}
          role-to-assume: arn:aws:iam::ACCOUNT:role/CI-Deploy-Role
      - name: Login to ECR
        run: |
          aws ecr get-login-password --region ${{ env.AWS_REGION }} | docker login --username AWS --password-stdin ${{ env.AWS_ACCOUNT_ID }}.dkr.ecr.${{ env.AWS_REGION }}.amazonaws.com
      - name: Build and push image
        run: |
          docker build -t $REPO:latest -f backend/ms-passengers/Dockerfile backend/ms-passengers
          docker tag $REPO:latest $REPO:latest
          docker push $REPO:latest
      - name: Deploy to EC2
        run: |
          ssh -i key.pem ubuntu@EC2_IP 'cd /home/ubuntu/bus-mvp/infra && docker compose pull && docker compose up -d'
```

Verificación post-deploy
- Ping health endpoint:
```bash
curl -f http://<EC2_PUBLIC_IP>:8001/health
```
- Revisar logs:
```bash
docker compose -f docker-compose.prod.yml logs -f ms-passengers
```

Notas finales
- Para producción considera: RDS para DB, ALB+ACM para HTTPS, Secrets Manager para credenciales, CloudWatch para logs y métricas, y Auto Scaling Groups / ECS / EKS para mejor escalabilidad (si el proyecto crece, migrar a ECS/EKS es recomendable).

---

Si quieres, puedo:
- crear `infra/docker-compose.prod.yml` (plantilla) y `infra/.env.production.example` ahora en el repo, con instrucciones concretas; o
- crear un workflow de GitHub Actions que construya y publique la imagen en ECR y haga el deploy.

Dime cuál prefieres y lo agrego automáticamente.