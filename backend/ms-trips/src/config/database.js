const { Sequelize } = require('sequelize');
const logger = require('./logger');

const sequelize = new Sequelize({
  dialect: 'mysql',
  // Priorizar variables del docker-compose, luego las locales
  host: process.env.SQL2_HOST || process.env.MYSQL_HOST || 'localhost',
  port: parseInt(process.env.SQL2_PORT || process.env.MYSQL_PORT) || 3306,
  database: process.env.SQL2_DB || process.env.MYSQL_DATABASE || process.env.MYSQL_DB || 'trips_db',
  username: process.env.SQL2_USER || process.env.MYSQL_USER || 'trips_user',
  password: process.env.SQL2_PASSWORD || process.env.MYSQL_PASSWORD || 'secure_password',
  
  // Configuración de logging
  logging: process.env.NODE_ENV === 'development' ? 
    (msg) => logger.debug('SQL Query:', msg) : false,
  
  // Pool de conexiones
  pool: {
    max: 10,        // Máximo 10 conexiones simultáneas
    min: 0,         // Mínimo 0 conexiones
    acquire: 30000, // Timeout máximo para obtener conexión (30s)
    idle: 10000     // Tiempo antes de liberar conexión inactiva (10s)
  },
  
  // Configuraciones adicionales
  define: {
    timestamps: true,           // Añadir createdAt y updatedAt automáticamente
    underscored: true,          // Usar snake_case para nombres de columnas
    freezeTableName: true,      // No pluralizar nombres de tablas
    paranoid: false,            // No usar soft deletes por defecto
  },
  
  // Zona horaria
  timezone: '+00:00',
  
  // Retry configuración
  retry: {
    max: 3,                     // Máximo 3 reintentos
    match: [                    // Tipos de errores para reintentar
      /ETIMEDOUT/,
      /EHOSTUNREACH/,
      /ECONNRESET/,
      /ECONNREFUSED/,
      /ENOTFOUND/,
      /SequelizeConnectionError/,
      /SequelizeConnectionRefusedError/,
      /SequelizeHostNotFoundError/,
      /SequelizeHostNotReachableError/,
      /SequelizeInvalidConnectionError/,
      /SequelizeConnectionTimedOutError/
    ]
  }
});

// Test de conexión
async function testConnection() {
  try {
    await sequelize.authenticate();
    logger.info('Database connection has been established successfully');
    return true;
  } catch (error) {
    logger.error('Unable to connect to the database:', error);
    return false;
  }
}

module.exports = {
  sequelize,
  testConnection
};
