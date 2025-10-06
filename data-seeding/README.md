# Data Seeding - Bus MVP

Este directorio contiene todos los scripts de generación de datos para el proyecto Bus MVP, movidos desde los microservicios individuales para centralizar la creación de datos de prueba.

## Estructura

```
data-seeding/
├── README.md                     # Este archivo
├── package.json                  # Dependencias principales
├── .env.example                  # Configuración de ejemplo
├── seed-all.js                   # Script principal para 20k registros
├── config/
│   ├── database.js              # Configuraciones de BD
│   └── constants.js             # Constantes compartidas
├── seeders/
│   ├── trips-seeder.js          # Seeder para ms-trips
│   ├── passengers-seeder.js     # Seeder para ms-passengers  
│   ├── tickets-seeder.js        # Seeder para ms-tickets
│   └── history-seeder.js        # Seeder para ms-history
├── models/
│   ├── mysql/                   # Modelos para MySQL (trips)
│   ├── postgresql/              # Modelos para PostgreSQL (passengers)
│   └── mongodb/                 # Modelos para MongoDB (tickets)
└── utils/
    ├── faker-helpers.js         # Utilidades para generar datos
    ├── database-helpers.js      # Utilidades de conexión BD
    └── statistics.js            # Generación de estadísticas
```

## Distribución de datos (20k registros)

- **50 rutas** (ms-trips/MySQL)
- **2,000 pasajeros** (ms-passengers/PostgreSQL)  
- **3,000 viajes** (ms-trips/MySQL)
- **14,950 tickets** (ms-tickets/MongoDB)

**Total: 20,000 registros**

## Uso

### Configuración inicial

```bash
cd data-seeding
npm install
cp .env.example .env
# Editar .env con las configuraciones de tu entorno
```

### Generar todos los datos (20k)

```bash
npm run seed:all
```

### Generar datos específicos

```bash
npm run seed:trips      # Solo viajes y rutas
npm run seed:passengers # Solo pasajeros  
npm run seed:tickets    # Solo tickets
```

### Limpiar todas las bases de datos

```bash
npm run clean:all
```

### Ver estadísticas

```bash
npm run stats
```

## Configuración

El archivo `.env` debe contener las configuraciones de conexión para todas las bases de datos:

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
MONGODB_DB=tickets_db

# Configuración del seeder
TOTAL_RECORDS=20000
BATCH_SIZE=1000
```

## Requisitos

- Node.js 18+
- Acceso a las bases de datos de los microservicios
- Los microservicios deben estar ejecutándose (para acceso a BD)

## Notas importantes

- Los scripts se conectan directamente a las bases de datos usando los puertos expuestos
- Se debe ejecutar desde el HOST, no desde dentro de containers
- Los datos generados son coherentes entre microservicios (IDs relacionados)
- Se incluye generación de datos para analytics e históricos
