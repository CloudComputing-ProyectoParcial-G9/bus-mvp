const { Sequelize, DataTypes } = require('sequelize');
require('dotenv').config();

// Configuración de la base de datos
const sequelize = new Sequelize(
  process.env.DB_NAME || 'ms_trips_db',
  process.env.DB_USER || 'root',
  process.env.DB_PASSWORD || 'password123',
  {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 3306,
    dialect: 'mysql',
    logging: false, // Desactivar logs de SQL para mejorar rendimiento
    pool: {
      max: 10,
      min: 0,
      acquire: 30000,
      idle: 10000
    }
  }
);

module.exports = { sequelize, DataTypes };
