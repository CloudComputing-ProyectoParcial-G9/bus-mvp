# Guía de Migración - Data Seeding

Esta guía te ayuda a migrar los scripts de seeding desde los microservicios individuales hacia la nueva estructura centralizada.

## Scripts Originales a Remover/Mover

### 1. Scripts en el directorio raíz
- `scripts/seed-all-20k.js` → ✅ **YA MIGRADO** como `data-seeding/seed-all.js`

### 2. Scripts en ms-trips
- `backend/ms-trips/scripts/seed.js` → Mover lógica a `data-seeding/seeders/trips-seeder.js`
- `backend/ms-trips/scripts/seed20k.js` → ✅ **FUNCIONALIDAD MIGRADA**
- `backend/ms-trips/scripts/seed-all-20k.js` → ✅ **DUPLICADO, PUEDE REMOVERSE**
- `backend/ms-trips/src/seeders/dataSeeder.js` → Mover lógica a `data-seeding/seeders/trips-seeder.js`

### 3. Scripts en ms-passengers
- `backend/ms-passengers/seed.py` → Mover lógica a `data-seeding/seeders/passengers-seeder.js`
- `backend/ms-passengers/src/seed_data.py` → ✅ **FUNCIONALIDAD MIGRADA**

### 4. Scripts en otros microservicios
- `backend/ms-tickets/src/main/java/com/busmvp/mstickets/config/DataSeeder.java` → ✅ **FUNCIONALIDAD MIGRADA**

## Pasos de Migración

### Paso 1: Backup (Recomendado)
```bash
# Crear backup de los scripts existentes
mkdir -p backup/scripts
cp -r scripts/ backup/scripts/
cp -r backend/ms-*/scripts/ backup/
cp -r backend/ms-*/src/**/seed* backup/
```

### Paso 2: Configurar nuevo sistema
```bash
cd data-seeding
./install.sh
# Editar .env con las configuraciones correctas
```

### Paso 3: Probar el nuevo sistema
```bash
cd data-seeding
npm run test:connections
npm run seed:all:clean  # Generar datos de prueba
npm run stats          # Verificar resultados
```

### Paso 4: Remover scripts antiguos (OPCIONAL)
Una vez verificado que el nuevo sistema funciona correctamente:

```bash
# Remover scripts duplicados del directorio raíz
rm -f scripts/seed-all-20k.js

# Remover scripts de ms-trips (mantener solo los necesarios para desarrollo local)
# CUIDADO: Evaluar si algunos scripts son necesarios para desarrollo local
rm -f backend/ms-trips/scripts/seed20k.js
rm -f backend/ms-trips/scripts/seed-all-20k.js

# Los seeders individuales pueden mantenerse para desarrollo local
# pero ya no serán la fuente principal de datos masivos
```

### Paso 5: Actualizar documentación
- Actualizar README.md principal
- Actualizar documentación de cada microservicio
- Actualizar scripts de CI/CD si los hay

## Ventajas de la Nueva Estructura

### ✅ Ventajas
1. **Centralización**: Todos los seeders en un lugar
2. **Configuración unificada**: Un solo archivo .env
3. **Coherencia de datos**: IDs relacionados correctamente entre microservicios
4. **Mejor rendimiento**: Generación en lotes optimizada
5. **Estadísticas centralizadas**: Vista completa del sistema
6. **Fácil mantenimiento**: Un solo lugar para actualizar lógica de seeding

### ⚠️ Consideraciones
1. **Dependencias**: El nuevo sistema depende de acceso directo a las BD
2. **Configuración**: Requiere configurar conexiones a todas las BD
3. **Aprendizaje**: El equipo necesita familiarizarse con la nueva estructura

## Scripts Obsoletos Después de la Migración

Estos scripts pueden considerarse para remoción una vez validado el nuevo sistema:

- `scripts/seed-all-20k.js` (duplicado)
- `backend/ms-trips/scripts/seed20k.js`
- `backend/ms-trips/scripts/seed-all-20k.js`

## Scripts a Mantener (para desarrollo local)

Estos scripts pueden mantenerse para desarrollo local de cada microservicio:

- `backend/ms-trips/scripts/seed.js` (datos pequeños para desarrollo)
- `backend/ms-trips/src/seeders/dataSeeder.js` (puede usarse para pruebas unitarias)
- `backend/ms-passengers/seed.py` (desarrollo local)

## Migración de Configuraciones

### Variables de entorno
El nuevo sistema usa estas variables (definir en `data-seeding/.env`):

```env
# MySQL (ms-trips)
MYSQL_HOST=localhost
MYSQL_PORT=3307
MYSQL_DB=trips_db
MYSQL_USER=trips_user
MYSQL_PASSWORD=secure_password

# PostgreSQL (ms-passengers)
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=passengers_db
POSTGRES_USER=passengers_user
POSTGRES_PASSWORD=passengers_password

# MongoDB (ms-tickets)
MONGODB_URL=mongodb://tickets_user:tickets_password@localhost:27018/tickets_db?authSource=tickets_db
```

### Docker Compose
Si usas Docker, asegúrate de que los puertos estén expuestos:

```yaml
# En docker-compose.yml
services:
  mysql-trips:
    ports:
      - "3307:3306"  # Exponer puerto para acceso desde host
  
  postgres-passengers:
    ports:
      - "5433:5432"  # Exponer puerto para acceso desde host
  
  mongodb-tickets:
    ports:
      - "27018:27017"  # Exponer puerto para acceso desde host
```
