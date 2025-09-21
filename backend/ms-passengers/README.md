# ms-passengers — Microservicio de Pasajeros

Descripción
-----------
`ms-passengers` es el microservicio responsable de la gestión de pasajeros: creación, consulta y listado. Está diseñado para ser sencillo y servir como dependencia para otros servicios (por ejemplo `ms-tickets`).

Stack técnico
-------------
- Lenguaje: Python 3.11+
- Framework: FastAPI
- Servidor ASGI: Uvicorn
- Dependencias: listadas en `requirements.txt` (FastAPI, Pydantic, Uvicorn, etc.)
- Contenerización: Docker

Qué incluye este README
- Instrucciones para clonar y ejecutar desde cero.
- Variables de entorno necesarias.
- Cómo ejecutar con Docker Compose y localmente.
- Documentación de endpoints con ejemplos para frontend.

Clonar el repositorio
---------------------

```powershell
git clone https://github.com/CloudComputing-ProyectoParcial-G9/bus-mvp.git
cd bus-mvp
```

Variables de entorno mínimas
---------------------------

ms-passengers no requiere muchas variables, pero el stack usa `infra/.env` para variables globales. Asegúrate de que `infra/.env` contiene al menos las URLs base para los servicios si vas a levantar el stack completo.

Ejemplo mínimo para `infra/.env`:

```properties
MS_PASSENGERS_PORT=8001
```

Ejecutar con Docker Compose (recomendado)
---------------------------------------

Desde la raíz del repo:

```powershell
docker compose -f infra/docker-compose.yml --env-file infra/.env up -d ms-passengers
```

Para rebuild (si hiciste cambios en el código):

```powershell
docker compose -f infra/docker-compose.yml --env-file infra/.env up -d --build ms-passengers
```

Ejecutar localmente sin Docker
-----------------------------

1) Crear y activar un virtualenv (opcional):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependencias:

```powershell
pip install -r backend/ms-passengers/requirements.txt
```

3) Ejecutar la app en modo desarrollo:

```powershell
cd backend/ms-passengers
uvicorn run:app --host 0.0.0.0 --port 8001 --reload
```

Endpoints (contrato para frontend)
---------------------------------

Base URL por defecto: `http://localhost:8001`

1) Crear pasajero
- Método: POST
- URL: /passengers
- Payload (JSON):

```json
{
  "full_name": "Juan Pérez",
  "email": "juan@example.com"   // opcional
}
```
- Respuestas:
  - 201 Created: retorna el recurso creado con `id`.
  - 400 Bad Request: payload inválido.

Ejemplo PowerShell:

```powershell
curl -X POST http://localhost:8001/passengers -H "Content-Type: application/json" -d '{"full_name":"Juan Pérez","email":"juan@example.com"}' -UseBasicParsing
```

2) Obtener pasajero por id
- Método: GET
- URL: /passengers/{id}
- Respuestas:
  - 200 OK: retorna el objeto pasajero.
  - 404 Not Found: si no existe.

Ejemplo:

```powershell
curl http://localhost:8001/passengers/pass_001 -UseBasicParsing
```

3) Listar pasajeros (paginado simple)
- Método: GET
- URL: /passengers
- Query params: `page` (int), `size` (int)
- Respuesta: 200 OK con lista y metadata de paginación.

Ejemplo:

```powershell
curl "http://localhost:8001/passengers?page=0&size=10" -UseBasicParsing
```

4) Health check
- Método: GET
- URL: /health
- Respuesta: 200 OK si el servicio está disponible.

Notas para frontend
-------------------
- El servicio devuelve códigos HTTP estándar. El frontend debe mapear 201 → creado, 400 → mostrar validación, 404 → recurso no encontrado.
- Validar inputs en el frontend antes de enviarlos para mejorar UX.
- Si piensas usar `ms-passengers` en local junto con `ms-tickets`, levanta ambos servicios con Docker Compose para que se resuelvan por nombre (`ms-passengers`, `ms-tickets`).

Postman / pruebas
-----------------
- Puedes crear una colección Postman simple con los endpoints anteriores. Si quieres, la genero y la añado al repo.

Ownership y próximas tareas
--------------------------
- Responsable: Backend team
- Próximas mejoras recomendadas:
  - Añadir validaciones más robustas (email, phone).
  - Agregar tests unitarios e integración.
  - Añadir logging estructurado y métricas.

Variables de entorno (ejemplo: `infra/.env`)
-----------------------------------------
Incluye en `infra/.env` estas variables (ejemplo tomado de tu env actual):

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

Notas y buenas prácticas
- `ms-passengers` usa la DB definida en `SQL1_*` si tu implementación está configurada para Postgres. Si el servicio no requiere la DB en memoria para pruebas rápidas, puede servirse sin conexión SQL (pero para integración con otros servicios, configura la BD y las migraciones).
- No comitees credenciales (`SQL1_PASSWORD`, `NOSQL_PASSWORD`) en el repo. Usa `.env` local excluido por `.gitignore` o Docker secrets.
- Variables operativas (`LOG_LEVEL`, `HTTP_TIMEOUT_MS`, `MAX_RETRIES`) son útiles para ajustar comportamiento en desarrollo y pruebas.

Fin del README de `ms-passengers`.
ms-passengers (minimal)
