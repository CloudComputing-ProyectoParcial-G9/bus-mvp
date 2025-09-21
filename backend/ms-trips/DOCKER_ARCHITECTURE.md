# 🏗️ Arquitectura de Contenedores - ms-trips

## 📋 **Resumen de la Arquitectura**

El microservicio **ms-trips** está diseñado para funcionar en **3 modalidades diferentes** según el entorno:

### **1. 🔧 Desarrollo Local (Actual)**
```
┌─────────────────┐    ┌──────────────────┐
│   Node.js       │────│  MySQL           │
│   (localhost)   │    │  (Docker)        │
│   Port: 8002    │    │  Port: 3306      │
└─────────────────┘    └──────────────────┘
```
- **Node.js**: Ejecuta directamente en el host
- **MySQL**: En contenedor Docker local
- **Uso**: Desarrollo y pruebas rápidas

### **2. 🧪 Testing Completo (Contenedores)**
```
┌─────────────────┐    ┌──────────────────┐
│   ms-trips      │────│  mysql-trips     │
│   (Container)   │    │  (Container)     │
│   Port: 8002    │    │  Port: 3307      │
└─────────────────┘    └──────────────────┘
```
- **Ambos servicios**: En contenedores Docker
- **Red**: Aislada (`ms-trips-test`)
- **Uso**: Testing de integración y CI/CD

### **3. 🚀 Producción (Infraestructura Completa)**
```
                    ┌─────────────────┐
                    │ Load Balancer   │
                    │ (nginx)         │
                    │ Port: 8080      │
                    └─────────┬───────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
  ┌─────▼─────┐         ┌─────▼─────┐         ┌─────▼─────┐
  │ms-passengers│         │ ms-trips  │         │ms-tickets │
  │   :8001     │         │   :8002   │         │   :8003   │
  └─────┬─────┘         └─────┬─────┘         └─────┬─────┘
        │                     │                     │
  ┌─────▼─────┐         ┌─────▼─────┐         ┌─────▼─────┐
  │PostgreSQL │         │   MySQL   │         │ MongoDB   │
  │   :5432   │         │   :3306   │         │  :27017   │
  └───────────┘         └───────────┘         └───────────┘
```

## 🐳 **Dockerfile Explicado**

### **Multi-Stage Build**
```dockerfile
# STAGE 1: Build dependencies
FROM node:18-alpine AS dependencies
# - Instala herramientas de compilación (python3, make, g++)
# - Instala solo dependencias de producción
# - Optimiza para reutilización de cache

# STAGE 2: Production image  
FROM node:18-alpine AS production
# - Imagen limpia sin herramientas de build
# - Usuario no-root para seguridad
# - Health check integrado
# - Variables de entorno configuradas
```

### **Características de Seguridad**
- ✅ **Usuario no-root**: `trips:nodejs (1001:1001)`
- ✅ **Imagen minimal**: `node:18-alpine` (tamaño reducido)
- ✅ **Health check**: Verifica `/api/v1/health` cada 30s
- ✅ **.dockerignore**: Excluye archivos sensibles y temporales

### **Variables de Entorno**

El contenedor soporta **2 sets de variables** para máxima flexibilidad:

#### **Para docker-compose principal** (`infra/`)
```bash
SQL2_HOST=sql-db2        # Nombre del servicio MySQL
SQL2_PORT=3306           # Puerto interno
SQL2_DB=trips_db         # Base de datos
SQL2_USER=trips_user     # Usuario
SQL2_PASSWORD=password   # Contraseña
```

#### **Para desarrollo local** (compatibilidad)
```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=trips_db
MYSQL_USER=trips_user
MYSQL_PASSWORD=password
```

## 📂 **Archivos de Configuración**

### **1. `Dockerfile`**
- Multi-stage build optimizado
- Seguridad con usuario no-root
- Health check integrado
- Variables de entorno por defecto

### **2. `.dockerignore`**
- Excluye `node_modules/`, logs, archivos de config
- Reduce tamaño del contexto de build
- Mejora velocidad de construcción

### **3. `docker-compose.test.yml`**
- Configuración para testing completo
- MySQL + ms-trips en contenedores
- Red aislada para pruebas
- Health checks configurados

## 🔄 **Flujo de Integración con Infraestructura**

### **En el docker-compose principal** (`infra/docker-compose.yml`):

```yaml
ms-trips:
  build:
    context: ../backend/ms-trips
    dockerfile: Dockerfile
  container_name: bus-mvp-ms-trips
  environment:
    - SQL2_HOST=sql-db2     # Se conecta al MySQL de infra
    - SQL2_PORT=3306
    - SQL2_DB=${SQL2_DB}    # Variables desde .env
    - SQL2_USER=${SQL2_USER}
    - SQL2_PASSWORD=${SQL2_PASSWORD}
  depends_on:
    sql-db2:
      condition: service_healthy
  networks:
    - bus-mvp-network        # Red compartida con otros microservicios
```

### **Ventajas de esta Arquitectura:**

1. **🔄 Flexibilidad**: 3 modalidades según necesidades
2. **🛡️ Seguridad**: Usuario no-root, variables de entorno segregadas
3. **📊 Observabilidad**: Health checks en todos los niveles
4. **⚡ Performance**: Multi-stage build, cache optimizado
5. **🔗 Integración**: Compatible con docker-compose principal
6. **🧪 Testing**: Configuración aislada para pruebas

## 🚀 **Comandos de Uso**

### **Desarrollo Local (Actual)**
```bash
./quick_start.sh
```

### **Testing con Contenedores**
```bash
docker-compose -f docker-compose.test.yml up --build -d
```

### **Producción (Infraestructura Completa)**
```bash
cd ../../infra
cp .env.example .env  # Configurar variables
docker-compose up --build -d
```

### **Verificación**
```bash
# Health check directo
curl http://localhost:8002/api/v1/health

# A través del load balancer (producción)
curl http://localhost:8080/api/v1/trips/health
```

## 🔍 **Troubleshooting Contenedores**

### **Ver logs del contenedor**
```bash
docker-compose -f docker-compose.test.yml logs -f ms-trips
```

### **Inspeccionar contenedor**
```bash
docker exec -it ms-trips-test sh
```

### **Verificar conectividad a MySQL**
```bash
# Desde dentro del contenedor
docker exec -it ms-trips-test curl http://localhost:8002/api/v1/health
```

### **Rebuild forzado**
```bash
docker-compose -f docker-compose.test.yml up --build --force-recreate
```

Esta arquitectura garantiza que **ms-trips funcione perfectamente** tanto en desarrollo local como en la infraestructura completa de producción. 🎯