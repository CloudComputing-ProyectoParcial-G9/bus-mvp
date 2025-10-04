# 📚 Documentación API - Swagger/OpenAPI

## ✅ Estado de Implementación

Todos los microservicios backend cuentan con documentación Swagger/OpenAPI completamente funcional.

---

## 🎯 Microservicios Documentados

### 1. **ms-passengers** (Python/FastAPI)
- **Tecnología**: FastAPI (documentación automática)
- **URL Swagger UI**: http://localhost:8001/docs
- **URL ReDoc**: http://localhost:8001/redoc
- **URL OpenAPI JSON**: http://localhost:8001/openapi.json

**Endpoints documentados**:
- `GET /health` - Health check
- `POST /passengers` - Crear pasajero
- `GET /passengers` - Listar pasajeros
- `GET /passengers/{passenger_id}` - Obtener pasajero por ID
- `PUT /passengers/{passenger_id}` - Actualizar pasajero
- `DELETE /passengers/{passenger_id}` - Eliminar pasajero

**Características**:
- ✅ Validación automática con Pydantic
- ✅ Ejemplos de request/response
- ✅ Modelos de datos documentados
- ✅ Códigos de respuesta HTTP

---

### 2. **ms-trips** (Node.js/Express)
- **Tecnología**: swagger-jsdoc + swagger-ui-express
- **URL Swagger UI**: http://localhost:8002/api-docs
- **URL OpenAPI JSON**: http://localhost:8002/api-docs.json

**Endpoints documentados**:
- `GET /health` - Health check
- `GET /routes` - Listar rutas
- `GET /routes/:route_id` - Obtener ruta por ID
- `POST /routes` - Crear ruta
- `GET /trips` - Listar viajes
- `GET /trips/:trip_id` - Obtener viaje por ID
- `POST /trips` - Crear viaje
- `GET /trips/search` - Buscar viajes (con validación de campos)

**Características**:
- ✅ JSDoc comentarios en código
- ✅ Definiciones de schemas
- ✅ Validación de parámetros
- ✅ Mensajes de error amigables en español

---

### 3. **ms-tickets** (Java/Spring Boot)
- **Tecnología**: SpringDoc OpenAPI 2.2.0
- **URL Swagger UI**: http://localhost:8003/swagger-ui/index.html
- **URL OpenAPI JSON**: http://localhost:8003/v3/api-docs
- **URL OpenAPI YAML**: http://localhost:8003/v3/api-docs.yaml

**Endpoints documentados**:
- `GET /tickets/health` - Health check
- `POST /tickets` - Crear ticket (comprar boleto)
- `GET /tickets` - Listar tickets (paginado)
- `GET /tickets/{id}` - Obtener ticket por ID
- `PUT /tickets/{id}` - Actualizar ticket
- `POST /tickets/{id}/cancel` - Cancelar ticket
- `GET /tickets/passenger/{passenger_id}/history` - Historial del pasajero

**Características**:
- ✅ Anotaciones `@Operation`, `@ApiResponse`, `@Parameter`
- ✅ Configuración personalizada (OpenApiConfig.java)
- ✅ Información del equipo y licencia
- ✅ Múltiples servidores configurados
- ✅ Documentación completa de errores (400, 404, 409, 500)

**Configuración**:
```java
@Configuration
public class OpenApiConfig {
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("Bus MVP - Tickets Service API")
                .version("1.0.0")
                .description("API para gestión de boletos...")
                .contact(new Contact().name("Bus MVP Team"))
                .license(new License().name("MIT")))
            .servers(List.of(
                new Server().url("http://localhost:8003"),
                new Server().url("http://localhost:8080")
            ));
    }
}
```

---

### 4. **ms-history** (Go/Gin)
- **Tecnología**: swaggo/swag
- **URL Swagger UI**: http://localhost:8004/swagger/index.html
- **URL OpenAPI JSON**: http://localhost:8004/swagger/doc.json

**Endpoints documentados**:
- `GET /health` - Health check básico
- `GET /api/v1/health` - System health (estado de microservicios)
- `GET /api/v1/dashboard` - Dashboard con estadísticas generales
- `GET /api/v1/history/passengers/{passenger_id}` - Historial completo del pasajero

**Características**:
- ✅ Anotaciones en comentarios Go
- ✅ Generación automática con `swag init`
- ✅ Modelos complejos documentados
- ✅ Documentación de agregaciones
- ✅ Descripción de dependencias de servicios

**Anotaciones en main.go**:
```go
// @title Bus MVP - History Service API
// @version 1.0
// @description API de agregación para historial de pasajeros
// @contact.name Bus MVP Team
// @contact.email dev@busmvp.com
// @license.name MIT
// @host localhost:8004
// @BasePath /
```

**Configuración Docker**:
```dockerfile
# Instalar swag CLI para generar documentación
RUN go install github.com/swaggo/swag/cmd/swag@latest

# Generar documentación Swagger
RUN swag init -g src/main.go --output ./src/docs
```

---

## 🔧 Implementación Técnica

### Python/FastAPI (ms-passengers)
- **Dependencia**: `fastapi[all]` (incluido en requirements.txt)
- **Implementación**: Automática, no requiere configuración adicional
- **Ventajas**: Validación Pydantic, documentación en tiempo real

### Node.js/Express (ms-trips)
- **Dependencias**:
  - `swagger-jsdoc`: ^6.2.8
  - `swagger-ui-express`: ^5.0.0
- **Configuración**: `src/config/swagger.js`
- **Ventajas**: Flexible, integración con JSDoc existente

### Java/Spring Boot (ms-tickets)
- **Dependencia**: `springdoc-openapi-starter-webmvc-ui:2.2.0`
- **Configuración**: `config/OpenApiConfig.java`
- **Ventajas**: Anotaciones ricas, integración con Spring, múltiples formatos

### Go/Gin (ms-history)
- **Dependencias**:
  - `github.com/swaggo/swag`
  - `github.com/swaggo/gin-swagger`
  - `github.com/swaggo/files`
- **Generación**: `swag init -g src/main.go --output ./src/docs`
- **Ventajas**: Tipado fuerte, generación en build time

---

## 📊 Comparación de Herramientas

| Microservicio | Tecnología | Herramienta | Documentación | Validación | Complejidad |
|--------------|------------|-------------|--------------|-----------|-------------|
| ms-passengers | Python/FastAPI | FastAPI | ⭐⭐⭐⭐⭐ Automática | ✅ Pydantic | 🟢 Baja |
| ms-trips | Node.js/Express | swagger-jsdoc | ⭐⭐⭐⭐ JSDoc | ✅ Manual | 🟡 Media |
| ms-tickets | Java/Spring Boot | SpringDoc | ⭐⭐⭐⭐⭐ Anotaciones | ✅ Bean Validation | 🟡 Media |
| ms-history | Go/Gin | swaggo/swag | ⭐⭐⭐⭐ Comentarios | ✅ Structs | 🟠 Media-Alta |

---

## 🚀 Acceso Rápido

Una vez que todos los servicios están corriendo (`docker compose -f docker-compose.dev.yml up -d`):

```bash
# Passengers
open http://localhost:8001/docs

# Trips
open http://localhost:8002/api-docs

# Tickets
open http://localhost:8003/swagger-ui/index.html

# History
open http://localhost:8004/swagger/index.html
```

---

## 📝 Notas Adicionales

### Beneficios de la Documentación
1. **Desarrollo Frontend**: El equipo frontend puede consultar los contratos API sin necesidad de revisar el código backend
2. **Testing**: Swagger UI permite probar endpoints directamente desde el navegador
3. **Integración**: Clientes pueden generar código automáticamente con OpenAPI Generator
4. **Onboarding**: Nuevos desarrolladores comprenden rápidamente la API
5. **Versionado**: La documentación está sincronizada con el código

### Best Practices Implementadas
- ✅ Descripciones claras en español
- ✅ Ejemplos de request/response
- ✅ Códigos de estado HTTP documentados
- ✅ Validaciones explícitas
- ✅ Información de contacto y licencia
- ✅ Múltiples servidores (desarrollo, load balancer)
- ✅ Tags para organizar endpoints

### Comandos Útiles

**Regenerar documentación de ms-history**:
```bash
cd backend/ms-history
swag init -g src/main.go --output ./src/docs
```

**Ver logs de Swagger**:
```bash
docker compose -f docker-compose.dev.yml logs ms-tickets | grep -i swagger
```

**Validar OpenAPI spec**:
```bash
curl http://localhost:8003/v3/api-docs | jq .
```

---

## 🎓 Cumplimiento de Requisitos Académicos

✅ **Requisito**: Documentación OpenAPI/Swagger para todos los microservicios
✅ **Requisito**: Al menos 2 endpoints documentados por microservicio (todos tienen >3)
✅ **Requisito**: Uso de diferentes tecnologías (Python, Node.js, Java, Go)
✅ **Requisito**: Documentación accesible via navegador

---

## 🔗 Referencias

- [OpenAPI Specification](https://swagger.io/specification/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SpringDoc](https://springdoc.org/)
- [swaggo/swag](https://github.com/swaggo/swag)
- [swagger-jsdoc](https://github.com/Surnet/swagger-jsdoc)

---

**Última actualización**: 4 de octubre de 2025
**Autor**: Bus MVP Team
**Repositorio**: CloudComputing-ProyectoParcial-G9/bus-mvp
**Branch**: feat/integration/improvements
