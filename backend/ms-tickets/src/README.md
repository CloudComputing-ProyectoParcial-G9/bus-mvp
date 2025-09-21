# ms-tickets — Microservicio de Boletos

Este documento describe el estado actual de `ms-tickets` después de los cambios realizados en la rama. Contiene instrucciones de uso, endpoints implementados, detalles de la migración a MongoDB y notas operativas.

Resumen de cambios principales
- Migración de persistencia: Redis -> MongoDB (Spring Data MongoDB).
- Endpoints principales implementados y probados: creación de ticket, listado paginado, obtención por id, actualización, cancelación y historial por pasajero.
- Manejo de errores mejorado en `GlobalExceptionHandler` para mapear correctamente 404 vs 5xx/timeout de servicios externos.
- Postman collection actualizada para pruebas E2E.

Stack y artefactos
- Lenguaje / Framework: Java 17, Spring Boot 3.x
- Persistencia: MongoDB (colección `tickets` en base `tickets_db`)
- Build: Maven (ejecutado dentro del contenedor en CI/Compose)
- Docker images: construidas con el Dockerfile del servicio y orquestadas por `infra/docker-compose.yml`.

Endpoints implementados (resumen)
- POST /tickets — Crear un nuevo boleto. Valida existencia de pasajero y viaje (llamadas a `ms-passengers` y `ms-trips`).
- GET /tickets — Listado paginado de boletos (query params: `page`, `size`).
- GET /tickets/{id} — Obtener boleto por su id.
- PUT /tickets/{id} — Actualizar algunos campos del boleto (p. ej. `seat_number`, `metadata`).
- POST /tickets/{id}/cancel — Cancelar un boleto.
- GET /tickets/passenger/{passenger_id}/history — Historial de boletos por pasajero (paginado).

Contrato: crear ticket (ejemplo)
Request mínimo (JSON):
```json
{
  "passenger_id": "<uuid>",
  "trip_id": "<trip-id>",
  "seat_number": "12A"
}
```

Respuesta exitosa (201):
```json
{
  "ticket_id": "ticket_<uuid>",
  "passenger_id": "<uuid>",
  "trip_id": "<trip-id>",
  "booking_status": "confirmed",
  "created_at": "2025-09-20T12:34:56Z"
}
```

Variables de entorno principales
- SPRING_DATA_MONGODB_URI: URI de conexión a MongoDB. Ejemplo (usado en `infra/docker-compose.yml`):
  mongodb://nosql-db:27017/tickets_db
- MS_TICKETS_PORT (opcional): puerto del servicio (por defecto 8003)
- MS_PASSENGERS_URL, MS_TRIPS_URL: URLs de los microservicios dependientes para validaciones.

Variables de entorno (ejemplo: `infra/.env`)
-----------------------------------------
Recomendamos mantener un archivo `infra/.env` con las variables locales para desarrollo. Un ejemplo mínimo (ajustado a tu `.env` actual):

```properties
# Local env for infra (auto-created by assistant)
SQL1_HOST=sql-db1
SQL1_PORT=5432
SQL1_DB=passengers_db
SQL1_USER=passengers_user
SQL1_PASSWORD=test_sql1_pw

SQL2_HOST=sql-db2
SQL2_PORT=3306
SQL2_DB=trips_db
SQL2_USER=trips_user
SQL2_PASSWORD=test_sql2_pw

NOSQL_URL=mongodb://nosql-db:27017
NOSQL_DB=tickets_db
NOSQL_USER=tickets_user
NOSQL_PASSWORD=test_nosql_pw

MS_PASSENGERS_PORT=8001
MS_TRIPS_PORT=8002
MS_TICKETS_PORT=8003
MS_HISTORY_PORT=8004
MS_ANALYTICS_PORT=8010

LB_PORT=8088

NODE_ENV=development
LOG_LEVEL=info
HTTP_TIMEOUT_MS=5000
MAX_RETRIES=3
RETRY_DELAY_MS=1000
```

Notas sobre mapeos y uso
- En este repo algunos servicios leen directamente `SPRING_DATA_MONGODB_URI` (variable de Spring). En `infra/docker-compose.yml` se construye o se pasa la URI directamente; si usas `NOSQL_URL` + `NOSQL_DB`, asegúrate de que tu Compose exporte `SPRING_DATA_MONGODB_URI=${NOSQL_URL}/${NOSQL_DB}` para evitar inconsistencias.
- Para la mayoría de servicios, `MS_*_PORT` define el puerto expuesto en desarrollo. Asegúrate de no solaparlos.
- No comitees contraseñas en el repositorio. Usa un `.env` local excluido por `.gitignore`, Docker secrets o un vault para producción.

Cómo ejecutar localmente (desde la raíz del repo)
1) Levantar infra y servicios relevantes con Docker Compose:

```powershell
docker compose -f infra/docker-compose.yml --env-file infra/.env up -d ms-tickets ms-passengers nosql-db
```

2) Forzar rebuild si hizo cambios en Java:

```powershell
docker compose -f infra/docker-compose.yml --env-file infra/.env up -d --build ms-tickets
```

3) Revisar logs (ejemplo para PowerShell):

```powershell
docker compose -f infra/docker-compose.yml --env-file infra/.env logs --tail 200 ms-tickets
```

Comandos curl (PowerShell) — ejemplos rápidos

# Crear pasajero (ms-passengers)
```powershell
curl -X POST http://localhost:8001/passengers -H "Content-Type: application/json" -d '{"full_name":"Juan Pérez"}' -UseBasicParsing
```

# Crear ticket (ms-tickets) — reemplaza PASSENGER_ID y TRIP_ID
```powershell
curl -X POST http://localhost:8003/tickets -H "Content-Type: application/json" -d '{"passenger_id":"PASSENGER_ID","trip_id":"TRIP_ID","seat_number":"12A"}' -UseBasicParsing
```

# Listar boletos (paginado)
```powershell
curl "http://localhost:8003/tickets?page=0&size=10" -UseBasicParsing
```

Postman
- La colección Postman para `ms-tickets` fue actualizada y se encuentra en `backend/ms-tickets/postman/ms-tickets.postman_collection.json`.
- Si quieres, puedo ejecutar la colección automáticamente con Newman desde este entorno y reportar los resultados.

MongoDB: esquema y ejemplo de documento
- Colección: `tickets` en `tickets_db`.

Ejemplo de documento (simplificado):
```json
{
  "_id": "ticket_001",
  "passenger_id": "pass_001",
  "trip_id": "trip_001",
  "seat_number": "12A",
  "total_price": 45.5,
  "currency": "EUR",
  "booking_status": "confirmed",
  "created_at": "2025-09-20T12:34:56Z"
}
```

Índices recomendados
- db.tickets.createIndex({ passenger_id: 1 })
- db.tickets.createIndex({ trip_id: 1 })
- db.tickets.createIndex({ booking_status: 1 })

Notas operativas y pendientes importantes
- ms-trips: en sesiones anteriores el contenedor `ms-trips` se reportó como `unhealthy`. Si vas a ejecutar E2E completas, confirma su estado o deja que yo lo revise antes.
- Distinción de errores externos: el service ahora mapea 404 (entidad no encontrada) y 5xx/timeouts (servicio indisponible) a códigos HTTP distintos; aún se puede mejorar usando `WebClient` + timeouts/Resilience4j.
- Reserva atómica: la migración a Mongo aún no implementa una solución atómica equivalente a la lógica previa en Redis. Recomendado: transacciones Mongo (si se usan réplicas) o un patrón de reserva con update condicional.

Pruebas y verificación (qué hice y qué deberías verificar)
- He probado manualmente el flujo crear pasajero → crear ticket con Postman y los endpoints respondieron correctamente.
- Verifiqué que `ms-tickets` se conecta a Mongo y los documentos se persisten en `tickets_db.tickets`.

Próximos pasos sugeridos (puedo ejecutar cualquiera de estos ahora)
1) Ejecutar la colección Postman automáticamente y generar un reporte.
2) Añadir idempotencia (TTL + almacenamiento de claves de idempotencia) para el endpoint de compra.
3) Implementar mecanismo de reserva atómica en Mongo.
4) Mejorar los clientes HTTP a `WebClient` con timeouts y circuit-breaker.

Contacto / ownership
- Responsable actual: Backend team — revisa la rama `feat/ms-trips` para cambios relacionados.

Si quieres que incorpore ejemplos adicionales (curl con headers de idempotencia, pruebas Newman o logs de verificación en Mongo), dime cuál de los "Próximos pasos" ejecutar y lo hago ahora.

---

Cómo usar este repositorio desde cero (clonar y ejecutar)

1) Clona el repositorio:

```powershell
git clone https://github.com/CloudComputing-ProyectoParcial-G9/bus-mvp.git
cd bus-mvp
```

2) Variables de entorno mínimas

El proyecto usa `infra/.env` para pasar variables a Docker Compose. Crea (o revisa) `infra/.env` y define al menos:

```properties
SPRING_DATA_MONGODB_URI=mongodb://nosql-db:27017/tickets_db
MS_TICKETS_PORT=8003
MS_TRIPS_URL=http://ms-trips:8002
MS_PASSENGERS_URL=http://ms-passengers:8001
```

3) Levantar los servicios (Docker Compose)

```powershell
docker compose -f infra/docker-compose.yml --env-file infra/.env up -d --build ms-tickets ms-passengers nosql-db
```

Notas:
- Si no quieres levantar `ms-passengers` o `nosql-db` por separado, puedes iniciar todo el stack sin filtrar servicios.
- Si tu entorno no tiene Docker, compila el JAR con Maven y ejecútalo localmente (ver sección "Build manual").

4) Acceder a los endpoints

Por defecto el servicio `ms-tickets` escucha en `http://localhost:8003` (según la configuración en `infra/.env`).

Documentación detallada de endpoints para frontend
-------------------------------------------------
A continuación detallo cada endpoint con método, URL, payload, respuestas esperadas, y ejemplos. Esto sirve como contrato para frontend.

1) Crear pasajero (ms-passengers) — usado por pruebas
- Método: POST
- URL: http://localhost:8001/passengers
- Payload:
```json
{
  "full_name": "Juan Pérez"
}
```
- Respuestas:
  - 201 Created: retorna el objeto de pasajero con campo `id`.
  - 400 Bad Request: payload inválido.

Ejemplo PowerShell:
```powershell
curl -X POST http://localhost:8001/passengers -H "Content-Type: application/json" -d '{"full_name":"Juan Pérez"}' -UseBasicParsing
```

2) Crear ticket
- Método: POST
- URL: http://localhost:8003/tickets
- Payload (obligatorio mínimo):
```json
{
  "passenger_id": "<PASSENGER_ID>",
  "trip_id": "<TRIP_ID>",
  "seat_number": "12A"          // opcional
}
```
- Respuestas:
  - 201 Created: ticket creado exitosamente. Devuelve el `ticket_id` y datos principales.
  - 400 Bad Request: campos obligatorios faltantes o formato inválido.
  - 404 Not Found: si `passenger_id` o `trip_id` no existen (dependiendo de la validación de ms-passengers/ms-trips).
  - 409 Conflict: si el asiento ya está reservado (implementación pendiente refinamiento).
  - 503 Service Unavailable: si ms-passengers o ms-trips no están disponibles (timeout/error de red).

Ejemplo PowerShell (reemplazar IDs):
```powershell
curl -X POST http://localhost:8003/tickets -H "Content-Type: application/json" -d '{"passenger_id":"pass_001","trip_id":"trip_001","seat_number":"12A"}' -UseBasicParsing
```

3) Listar tickets (paginado)
- Método: GET
- URL: http://localhost:8003/tickets
- Query params opcionales:
  - page (int, default 0)
  - size (int, default 10)
- Respuesta:
  - 200 OK: devuelve un objeto con lista de tickets y metadata de paginación.

Ejemplo:
```powershell
curl "http://localhost:8003/tickets?page=0&size=10" -UseBasicParsing
```

Respuesta esperada (ejemplo):
```json
{
  "content": [ { "ticket_id": "...", "passenger_id": "...", "trip_id": "..." } ],
  "page": 0,
  "size": 10,
  "totalElements": 123,
  "totalPages": 13
}
```

4) Obtener ticket por id
- Método: GET
- URL: http://localhost:8003/tickets/{id}
- Respuestas:
  - 200 OK: devuelve el documento del ticket.
  - 404 Not Found: si no existe.

Ejemplo:
```powershell
curl http://localhost:8003/tickets/ticket_001 -UseBasicParsing
```

5) Actualizar ticket
- Método: PUT
- URL: http://localhost:8003/tickets/{id}
- Payload: JSON con los campos permitidos para actualizar, p. ej. `seat_number`, `metadata`.
- Respuestas:
  - 200 OK: ticket actualizado.
  - 400 Bad Request: payload inválido.
  - 404 Not Found: si no existe.

Ejemplo:
```powershell
curl -X PUT http://localhost:8003/tickets/ticket_001 -H "Content-Type: application/json" -d '{"seat_number":"14B"}' -UseBasicParsing
```

6) Cancelar ticket
- Método: POST
- URL: http://localhost:8003/tickets/{id}/cancel
- Payload: opcional (motivo)
- Respuestas:
  - 200 OK: ticket cancelado y estado actualizado.
  - 404 Not Found: si no existe.
  - 409 Conflict: si no aplicable (p. ej. ya refund procesado).

Ejemplo:
```powershell
curl -X POST http://localhost:8003/tickets/ticket_001/cancel -H "Content-Type: application/json" -d '{"reason":"Cambio de planes"}' -UseBasicParsing
```

7) Historial por pasajero
- Método: GET
- URL: http://localhost:8003/tickets/passenger/{passenger_id}/history
- Query params: page, size
- Respuestas:
  - 200 OK: lista paginada de boletos del pasajero.
  - 404 Not Found: si el pasajero no existe (según validación).

Ejemplo:
```powershell
curl "http://localhost:8003/tickets/passenger/pass_001/history?page=0&size=10" -UseBasicParsing
```

Errores y códigos HTTP (resumen para frontend)
- 200 OK: éxito en GET/PUT/POST-cancel donde aplique.
- 201 Created: recurso creado (POST /tickets).
- 400 Bad Request: payload inválido.
- 404 Not Found: entidad relacionada no encontrada (passenger/trip/ticket).
- 409 Conflict: conflicto de negocio (asiento no disponible, etc.).
- 422 Unprocessable Entity: se usa internamente para validar integración con otros servicios cuando aplica.
- 503 Service Unavailable: servicio dependiente caído o timeout.

Notas para el frontend
- Siempre validar antes de enviar: `passenger_id` y `trip_id` deben existir (el backend hará comprobación adicional). El frontend puede mostrar errores amigables según los códigos HTTP.
- Para la compra, opcionalmente añade un header `Idempotency-Key` (si implementamos idempotencia) para prevenir doble cobro en reintentos.
- Usa paginación en listados para evitar cargas grandes.

Sección: Build manual (sin Docker)
Si no quieres usar Docker, compila y ejecuta localmente (necesitas Java 17 y Maven):

```powershell
cd backend/ms-tickets
mvn clean package -DskipTests
java -jar target/*.jar
```

Fin de la actualización del README.

