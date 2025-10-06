const { DataTypes, Model } = require('sequelize');
const { sequelize } = require('../config/database');

class Trip extends Model {
  // Métodos de instancia personalizados
  
  /**
   * Verificar si el viaje tiene asientos disponibles
   */
  hasAvailableSeats(requiredSeats = 1) {
    return this.availableSeats >= requiredSeats;
  }
  
  /**
   * Reservar asientos (disminuir disponibles)
   */
  async reserveSeats(seatsToReserve) {
    if (!this.hasAvailableSeats(seatsToReserve)) {
      throw new Error(`Not enough seats available. Required: ${seatsToReserve}, Available: ${this.availableSeats}`);
    }
    
    this.availableSeats -= seatsToReserve;
    await this.save();
    return this.availableSeats;
  }
  
  /**
   * Liberar asientos (aumentar disponibles)
   */
  async releaseSeats(seatsToRelease) {
    const newAvailableSeats = this.availableSeats + seatsToRelease;
    
    if (newAvailableSeats > this.busCapacity) {
      throw new Error(`Cannot release more seats than bus capacity. Max: ${this.busCapacity}`);
    }
    
    this.availableSeats = newAvailableSeats;
    await this.save();
    return this.availableSeats;
  }
  
  /**
   * Verificar si el viaje está en el futuro
   */
  isFuture() {
    return new Date(this.departureDateTime) > new Date();
  }
  
  /**
   * Verificar si el viaje se puede cancelar
   */
  isCancellable() {
    return this.status === 'scheduled' && this.isFuture();
  }
  
  /**
   * Obtener ocupación como porcentaje
   */
  getOccupancyRate() {
    const occupiedSeats = this.busCapacity - this.availableSeats;
    return ((occupiedSeats / this.busCapacity) * 100).toFixed(2);
  }
  
  /**
   * Calcular duración real del viaje
   */
  getRealDuration() {
    const departure = new Date(this.departureDateTime);
    const arrival = new Date(this.arrivalDateTime);
    const durationMs = arrival - departure;
    const hours = Math.floor(durationMs / (1000 * 60 * 60));
    const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  }
}

Trip.init({
  tripId: {
    type: DataTypes.STRING(50),
    primaryKey: true,
    allowNull: false,
    validate: {
      notEmpty: true,
      is: /^TRP_\d{8}_[A-Z]{3}_[A-Z]{3}_\d{2}$/, // Formato: TRP_20240925_MAD_BCN_15
    },
    comment: 'Identificador único del viaje (formato: TRP_YYYYMMDD_ORG_DST_HH)'
  },
  
  routeId: {
    type: DataTypes.STRING(20),
    allowNull: false,
    // TEMPORALMENTE COMENTAMOS LA FOREIGN KEY PARA QUE FUNCIONE
    // references: {
    //   model: 'routes',
    //   key: 'routeId'
    // },
    // onUpdate: 'CASCADE',
    // onDelete: 'RESTRICT',
    comment: 'ID de la ruta asociada'
  },
  
  departureDateTime: {
    type: DataTypes.DATE,
    allowNull: false,
    validate: {
      notEmpty: true,
      isDate: true,
      isAfterNow(value) {
        // Permitir margen de 5 minutos para evitar problemas de sincronización
        const now = new Date();
        const fiveMinutesAgo = new Date(now.getTime() - (5 * 60 * 1000));
        if (new Date(value) < fiveMinutesAgo) {
          throw new Error('Departure date must be in the future');
        }
      }
    },
    comment: 'Fecha y hora de salida'
  },
  
  arrivalDateTime: {
    type: DataTypes.DATE,
    allowNull: false,
    validate: {
      notEmpty: true,
      isDate: true
    },
    comment: 'Fecha y hora de llegada'
  },
  
  busCapacity: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: 1,
      max: 100,
      isInt: true
    },
    comment: 'Capacidad total del autobús'
  },
  
  availableSeats: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: 0,
      isInt: true
    },
    comment: 'Asientos disponibles'
  },
  
  finalPrice: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
    validate: {
      min: 0.01,
      max: 99999.99
    },
    comment: 'Precio final del viaje (puede diferir del precio base de la ruta)'
  },
  
  status: {
    type: DataTypes.ENUM('scheduled', 'in_progress', 'completed', 'cancelled'),
    allowNull: false,
    defaultValue: 'scheduled',
    comment: 'Estado actual del viaje'
  },
  
  driverName: {
    type: DataTypes.STRING(100),
    allowNull: true,
    validate: {
      len: [2, 100]
    },
    comment: 'Nombre del conductor asignado'
  },
  
  busPlate: {
    type: DataTypes.STRING(20),
    allowNull: true,
    validate: {
      len: [6, 20]
    },
    comment: 'Placa del autobús asignado'
  }
}, {
  sequelize,
  modelName: 'Trip',
  tableName: 'trips',
  timestamps: true,
  
    // Índices básicos (simplificados)
  indexes: [
    // Comentamos los índices por ahora para evitar problemas
    // {
    //   name: 'idx_trips_route_id',
    //   fields: ['route_id']
    // }
  ],
  
  // Validaciones a nivel de modelo
  validate: {
    arrivalAfterDeparture() {
      if (this.arrivalDateTime <= this.departureDateTime) {
        throw new Error('Arrival time must be after departure time');
      }
    },
    
    availableSeatsNotExceedCapacity() {
      if (this.availableSeats > this.busCapacity) {
        throw new Error('Available seats cannot exceed bus capacity');
      }
    },
    
    validTripDuration() {
      const departure = new Date(this.departureDateTime);
      const arrival = new Date(this.arrivalDateTime);
      const durationHours = (arrival - departure) / (1000 * 60 * 60);
      
      if (durationHours > 24) {
        throw new Error('Trip duration cannot exceed 24 hours');
      }
      
      if (durationHours < 0.5) {
        throw new Error('Trip duration must be at least 30 minutes');
      }
    }
  },
  
  // Hooks de Sequelize
  hooks: {
    beforeCreate: (trip, options) => {
      // Validar que el viaje no sea en el pasado al crear
      // Permitir margen de 5 minutos para evitar problemas de sincronización
      const now = new Date();
      const fiveMinutesAgo = new Date(now.getTime() - (5 * 60 * 1000));
      if (new Date(trip.departureDateTime) <= fiveMinutesAgo) {
        throw new Error('Cannot create trips in the past');
      }
    },
    
    beforeUpdate: (trip, options) => {
      // Si se está cancelando, no validar fechas
      if (trip.status === 'cancelled') {
        return;
      }

      // Validar que no se pueda cambiar fecha a pasado si no está cancelado
      // Permitir margen de 5 minutos para evitar problemas de sincronización
      const now = new Date();
      const fiveMinutesAgo = new Date(now.getTime() - (5 * 60 * 1000));
      if (trip.changed('departureDateTime') && new Date(trip.departureDateTime) <= fiveMinutesAgo) {
        throw new Error('Cannot update departure time to the past');
      }
    }
  }
});

module.exports = Trip;
