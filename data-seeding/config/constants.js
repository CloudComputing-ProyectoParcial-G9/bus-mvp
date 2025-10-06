require('dotenv').config();

const CONFIG = {
  // Data distribution (must sum to TOTAL_RECORDS)
  counts: {
    routes: parseInt(process.env.ROUTES_COUNT) || 50,
    passengers: parseInt(process.env.PASSENGERS_COUNT) || 2000,
    trips: parseInt(process.env.TRIPS_COUNT) || 3000,
    tickets: parseInt(process.env.TICKETS_COUNT) || 14950
  },

  // Database configurations
  mysql: {
    host: process.env.MYSQL_HOST || 'localhost',
    port: parseInt(process.env.MYSQL_PORT) || 3307,
    database: process.env.MYSQL_DB || 'trips_db',
    user: process.env.MYSQL_USER || 'trips_user',
    password: process.env.MYSQL_PASSWORD || 'secure_password'
  },

  postgres: {
    host: process.env.POSTGRES_HOST || 'localhost',
    port: parseInt(process.env.POSTGRES_PORT) || 5433,
    database: process.env.POSTGRES_DB || 'passengers_db',
    user: process.env.POSTGRES_USER || 'passengers_user',
    password: process.env.POSTGRES_PASSWORD || 'passengers_password'
  },

  mongodb: {
    url: process.env.MONGODB_URL || 'mongodb://tickets_user:tickets_password@localhost:27018/tickets_db?authSource=tickets_db',
    database: process.env.MONGODB_DB || 'tickets_db'
  },

  // Seeding options
  batchSize: parseInt(process.env.BATCH_SIZE) || 1000,
  maxRetries: parseInt(process.env.MAX_RETRIES) || 3,
  logLevel: process.env.LOG_LEVEL || 'info',

  // Business data
  cities: [
    'Lima', 'Arequipa', 'Cusco', 'Trujillo', 'Chiclayo', 'Piura', 'Iquitos',
    'Huancayo', 'Tacna', 'Pucallpa', 'Ayacucho', 'Cajamarca', 'Ica', 'Juliaca',
    'Huaraz', 'Puno', 'Tumbes', 'Tarapoto', 'Chimbote', 'Huánuco'
  ],

  cityCodes: {
    'Lima': 'LIM', 'Arequipa': 'AQP', 'Cusco': 'CUZ', 'Trujillo': 'TRU',
    'Chiclayo': 'CIX', 'Piura': 'PIU', 'Iquitos': 'IQT', 'Huancayo': 'HUA',
    'Tacna': 'TCQ', 'Pucallpa': 'PCL', 'Ayacucho': 'AYA', 'Cajamarca': 'CAJ',
    'Ica': 'ICA', 'Juliaca': 'JUL', 'Huaraz': 'HUZ', 'Puno': 'PUN',
    'Tumbes': 'TBP', 'Tarapoto': 'TPP', 'Chimbote': 'CHM', 'Huánuco': 'HUC'
  },

  driverNames: [
    'Carlos Mendoza', 'Ana Rodriguez', 'Miguel Santos', 'Carmen López', 'Roberto Quispe',
    'Patricia Flores', 'Jorge Ramirez', 'Luis Castillo', 'Elena Martinez', 'Fernando Silva',
    'Rosa Garcia', 'Pedro Gonzalez', 'Maria Torres', 'Juan Vasquez', 'Sofia Herrera',
    'Diego Morales', 'Laura Rojas', 'Alberto Campos', 'Gabriela Soto', 'Ricardo Vega',
    'Lucia Fernandez', 'Manuel Castro', 'Isabel Ruiz', 'Andres Paredes', 'Cristina Delgado'
  ],

  ticketStatuses: ['confirmed', 'confirmed', 'confirmed', 'confirmed', 'pending', 'cancelled'],
  tripStatuses: ['scheduled', 'scheduled', 'scheduled', 'scheduled', 'in_progress', 'completed']
};

// Validate configuration
const totalRecords = Object.values(CONFIG.counts).reduce((a, b) => a + b, 0);
const expectedTotal = parseInt(process.env.TOTAL_RECORDS) || 20000;

if (totalRecords !== expectedTotal) {
  console.warn(`⚠️  Warning: Data distribution (${totalRecords}) doesn't match expected total (${expectedTotal})`);
}

module.exports = CONFIG;
