# Variables de entorno (infra/.env)

Este archivo explica las variables que usamos en `infra/.env` para el entorno de desarrollo local. Mantener estas variables en un archivo `.env` separado (no commiteado con secretos reales) facilita levantar el stack con Docker Compose.

Bloque de ejemplo (usa tu `infra/.env` real):

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

Descripción de variables
------------------------

Bases de datos SQL (ej. Postgres / MySQL)
- `SQL1_HOST`, `SQL1_PORT`, `SQL1_DB`, `SQL1_USER`, `SQL1_PASSWORD` — Parámetros de conexión para la base de datos del servicio `ms-passengers` (ej. Postgres). Ajusta según tu motor.
- `SQL2_HOST`, `SQL2_PORT`, `SQL2_DB`, `SQL2_USER`, `SQL2_PASSWORD` — Parámetros para la base de datos del servicio `ms-trips`.

Base de datos NoSQL (MongoDB)
- `NOSQL_URL` — URL base de conexión para MongoDB, p. ej. `mongodb://nosql-db:27017`.
- `NOSQL_DB` — Nombre de la base a usar, p. ej. `tickets_db`.
- `NOSQL_USER`, `NOSQL_PASSWORD` — Credenciales (si usas autenticación en el contenedor de Mongo).

Puertos de microservicios
- `MS_PASSENGERS_PORT`, `MS_TRIPS_PORT`, `MS_TICKETS_PORT`, `MS_HISTORY_PORT`, `MS_ANALYTICS_PORT` — Puertos locales para mapear cada servicio. Úsalos al arrancar con Docker Compose o al ejecutar localmente.
- `LB_PORT` — Puerto del load-balancer / reverse-proxy local si aplica.

Variables operativas / runtime
- `NODE_ENV` — Modo de ejecución (development/production).
- `LOG_LEVEL` — Nivel de logs (debug, info, warn, error).
- `HTTP_TIMEOUT_MS` — Timeout por defecto en ms para llamadas HTTP entre microservicios.
- `MAX_RETRIES` — Reintentos por llamada HTTP cuando apliquen.
- `RETRY_DELAY_MS` — Delay entre reintentos en ms.

Notas y buenas prácticas
-----------------------
- No almacenar secretos reales en repositorios. Usa `.env` local excluido por `.gitignore`, Docker secrets o un vault para producción.
- Mantén consistencia de nombres: evita tener dos variables que significan lo mismo con nombres distintos (por ejemplo: `NOSQL_URL` vs `SPRING_DATA_MONGODB_URI`). En Compose es común derivar la variable que usa la app a partir de las variables infra:

  SPRING_DATA_MONGODB_URI=${NOSQL_URL}/${NOSQL_DB}

- Documenta cualquier transformación que haga `docker-compose.yml` (por ejemplo, si se concatena o se reemplaza variables).
- Para entornos de CI, exporta variables seguras en los secretos del runner en lugar de archivo `.env`.

Recomendaciones de seguridad
---------------------------
- Usa contraseñas robustas para las bases de datos y no las comitees.
- Considera levantar Mongo con autenticación y autorización en entornos que no sean locales.
- Para datos sensibles, usa encriptación en reposo/transferencia y un mecanismo de rotación de credenciales.

Ejemplos de uso en Docker Compose
---------------------------------
En `infra/docker-compose.yml` puedes mapear variables a servicios así:

```yaml
services:
  ms-tickets:
    env_file: ["./.env"]
    environment:
      - SPRING_DATA_MONGODB_URI=${NOSQL_URL}/${NOSQL_DB}
      - SPRING_DATA_MONGODB_USERNAME=${NOSQL_USER}
      - SPRING_DATA_MONGODB_PASSWORD=${NOSQL_PASSWORD}

  nosql-db:
    image: mongo:6.0
    environment:
      - MONGO_INITDB_DATABASE=${NOSQL_DB}
      - MONGO_INITDB_ROOT_USERNAME=${NOSQL_USER}
      - MONGO_INITDB_ROOT_PASSWORD=${NOSQL_PASSWORD}
```


