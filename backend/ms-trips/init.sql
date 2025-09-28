-- Inicialización de la base de datos trips_db
-- Este archivo se ejecuta automáticamente cuando se crea el contenedor

USE trips_db;

-- Verificar que la base de datos fue creada
SELECT 'trips_db database initialized successfully' AS message;

-- Las tablas se crearán automáticamente via Sequelize sync
