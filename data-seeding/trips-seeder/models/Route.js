const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Route = sequelize.define('Route', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  routeId: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
    field: 'route_id'
  },
  routeName: {
    type: DataTypes.STRING,
    allowNull: false,
    field: 'route_name'
  },
  originCity: {
    type: DataTypes.STRING,
    allowNull: false,
    field: 'origin_city'
  },
  destinationCity: {
    type: DataTypes.STRING,
    allowNull: false,
    field: 'destination_city'
  },
  distanceKm: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
    field: 'distance_km'
  },
  estimatedDuration: {
    type: DataTypes.TIME,
    allowNull: false,
    field: 'estimated_duration'
  },
  basePrice: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
    field: 'base_price'
  },
  currency: {
    type: DataTypes.STRING,
    allowNull: false,
    defaultValue: 'PEN'
  },
  active: {
    type: DataTypes.BOOLEAN,
    allowNull: false,
    defaultValue: true
  }
}, {
  tableName: 'routes',
  timestamps: true,
  underscored: true
});

module.exports = Route;
