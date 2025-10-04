const { DataTypes, Model } = require('sequelize');
const { sequelize } = require('../config/database');

class Route extends Model {
  // Métodos de instancia personalizados
  
  /**
   * Verificar si la ruta está activa
   */
  isActive() {
    return this.active === true;
  }
  
  /**
   * Obtener la descripción completa de la ruta
   */
  getFullDescription() {
    return `${this.routeName} (${this.originCity} → ${this.destinationCity})`;
  }
  
  /**
   * Calcular precio con descuento/recargo
   */
  calculatePriceWithModifier(modifier = 1.0) {
    return (this.basePrice * modifier).toFixed(2);
  }
}

Route.init({
  routeId: {
    type: DataTypes.STRING(20),
    primaryKey: true,
    allowNull: false,
    validate: {
      notEmpty: true,
      is: /^[A-Z]{3}_[A-Z]{3}_\d{3}$/, // Formato: MAD_BCN_001
    },
    comment: 'Identificador único de la ruta (formato: ORG_DST_NNN)'
  },
  
  routeName: {
    type: DataTypes.STRING(100),
    allowNull: false,
    validate: {
      notEmpty: true,
      len: [5, 100]
    },
    comment: 'Nombre descriptivo de la ruta'
  },
  
  originCity: {
    type: DataTypes.STRING(50),
    allowNull: false,
    validate: {
      notEmpty: true,
      len: [2, 50]
    },
    comment: 'Ciudad de origen'
  },
  
  destinationCity: {
    type: DataTypes.STRING(50),
    allowNull: false,
    validate: {
      notEmpty: true,
      len: [2, 50]
    },
    comment: 'Ciudad de destino'
  },
  
  distanceKm: {
    type: DataTypes.DECIMAL(8, 2),
    allowNull: false,
    validate: {
      min: 1.0,
      max: 9999.99
    },
    comment: 'Distancia en kilómetros'
  },
  
  estimatedDuration: {
    type: DataTypes.TIME,
    allowNull: false,
    validate: {
      notEmpty: true
    },
    comment: 'Duración estimada del viaje (HH:MM:SS)'
  },
  
  basePrice: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
    validate: {
      min: 0.01,
      max: 99999.99
    },
    comment: 'Precio base de la ruta'
  },
  
  currency: {
    type: DataTypes.STRING(3),
    allowNull: false,
    defaultValue: 'PEN',
    validate: {
      isIn: [['PEN', 'USD', 'EUR']]
    },
    comment: 'Código de moneda ISO 4217 (PEN = Sol Peruano)'
  },
  
  active: {
    type: DataTypes.BOOLEAN,
    allowNull: false,
    defaultValue: true,
    comment: 'Indica si la ruta está activa'
  }
}, {
  sequelize,
  modelName: 'Route',
  tableName: 'routes',
  timestamps: true,
  
  // Índices básicos (simplificados)
  indexes: [
    // Comentamos los índices por ahora para evitar problemas
    // {
    //   name: 'idx_routes_cities',
    //   fields: ['origin_city', 'destination_city']
    // },
    // {
    //   name: 'idx_routes_active',
    //   fields: ['active']
    // }
  ],
  
  // Validaciones a nivel de modelo
  validate: {
    differentCities() {
      if (this.originCity === this.destinationCity) {
        throw new Error('Origin and destination cities must be different');
      }
    }
  }
});

module.exports = Route;
