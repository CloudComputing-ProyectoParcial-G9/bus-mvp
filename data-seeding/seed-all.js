#!/usr/bin/env node

/**
 * Script de generación masiva de datos para todo el sistema Bus MVP
 * Genera 20,000 registros distribuidos coherentemente entre todos los microservicios
 *
 * Distribución por defecto:
 * - 50 rutas (ms-trips/MySQL)
 * - 2,000 pasajeros (ms-passengers/PostgreSQL)
 * - 3,000 viajes (ms-trips/MySQL)
 * - 14,950 tickets (ms-tickets/MongoDB)
 *
 * Total: 20,000 registros
 *
 * Uso: node seed-all.js [opciones]
 * 
 * Opciones:
 *   --clean        Limpiar bases de datos antes de generar
 *   --no-stats     No mostrar estadísticas al final
 *   --help         Mostrar ayuda
 */

const chalk = require('chalk');
const cliProgress = require('cli-progress');
const DatabaseManager = require('./config/database');
const CONFIG = require('./config/constants');
const { faker } = require('@faker-js/faker');
const { Sequelize } = require('sequelize');
const { Client } = require('pg');
const { MongoClient } = require('mongodb');

// ============================================================================
// CONEXIONES
// ============================================================================

let mysqlConn;
let pgClient;
let mongoClient;
let mongoDB;

async function connectDatabases() {
  console.log('🔌 Conectando a las bases de datos...\n');

  // MySQL (Sequelize)
  mysqlConn = new Sequelize(
    CONFIG.mysql.database,
    CONFIG.mysql.user,
    CONFIG.mysql.password,
    {
      host: CONFIG.mysql.host,
      port: CONFIG.mysql.port,
      dialect: 'mysql',
      logging: false,
      define: {
        timestamps: true,
        underscored: true,  // Usar snake_case para nombres de columnas
        freezeTableName: true
      }
    }
  );

  await mysqlConn.authenticate();
  console.log('✅ MySQL conectado');

  // PostgreSQL
  pgClient = new Client({
    host: CONFIG.postgres.host,
    port: CONFIG.postgres.port,
    database: CONFIG.postgres.database,
    user: CONFIG.postgres.user,
    password: CONFIG.postgres.password
  });

  await pgClient.connect();
  console.log('✅ PostgreSQL conectado');

  // MongoDB
  mongoClient = new MongoClient(CONFIG.mongodb.url);
  await mongoClient.connect();
  mongoDB = mongoClient.db(CONFIG.mongodb.database);
  console.log('✅ MongoDB conectado\n');
}

async function closeDatabases() {
  console.log('\n🔌 Cerrando conexiones...');

  if (mysqlConn) await mysqlConn.close();
  if (pgClient) await pgClient.end();
  if (mongoClient) await mongoClient.close();

  console.log('✅ Conexiones cerradas');
}

// ============================================================================
// LIMPIEZA
// ============================================================================

async function cleanDatabases() {
  console.log('🧹 Limpiando bases de datos...\n');

  // Limpiar MySQL (trips, routes)
  await mysqlConn.query('SET FOREIGN_KEY_CHECKS = 0');
  await mysqlConn.query('TRUNCATE TABLE trips');
  await mysqlConn.query('TRUNCATE TABLE routes');
  await mysqlConn.query('SET FOREIGN_KEY_CHECKS = 1');
  console.log('✅ MySQL limpio (trips, routes)');

  // Limpiar PostgreSQL (passengers)
  await pgClient.query('TRUNCATE TABLE passenger CASCADE');
  console.log('✅ PostgreSQL limpio (passengers)');

  // Limpiar MongoDB (tickets)
  await mongoDB.collection('tickets').deleteMany({});
  console.log('✅ MongoDB limpio (tickets)\n');
}

// ============================================================================
// GENERADORES DE DATOS
// ============================================================================

function generateRouteId(origin, destination, number) {
  const originCode = CONFIG.cityCodes[origin];
  const destCode = CONFIG.cityCodes[destination];
  return `${originCode}_${destCode}_${String(number).padStart(3, '0')}`;
}

function generateTripId(date, routeId, hour) {
  const dateStr = date.toISOString().slice(0, 10).replace(/-/g, '');
  const [origin, dest] = routeId.split('_');
  const hourStr = String(hour).padStart(2, '0');
  // El modelo espera formato: TRP_YYYYMMDD_ORG_DST_HH
  return `TRP_${dateStr}_${origin}_${dest}_${hourStr}`;
}

function getRandomElements(array, count) {
  const shuffled = [...array].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

// ============================================================================
// GENERACIÓN DE RUTAS
// ============================================================================

async function generateRoutes() {
  console.log(`📍 Generando ${CONFIG.counts.routes} rutas...`);

  const routes = [];
  const routeMap = new Map();
  let routeCount = 0;

  for (let i = 0; i < CONFIG.counts.routes; i++) {
    const cities = getRandomElements(CONFIG.cities, 2);
    const [origin, destination] = cities;

    const routeId = generateRouteId(origin, destination, i + 1);
    const distanceKm = faker.number.int({ min: 50, max: 1500 });
    const durationHours = Math.ceil(distanceKm / 60); // ~60 km/h promedio
    const basePrice = faker.number.int({ min: 20, max: 200 });

    const route = {
      routeId,
      routeName: `Ruta ${origin} - ${destination}`,
      originCity: origin,
      destinationCity: destination,
      distanceKm,
      estimatedDuration: `${durationHours}:00:00`,
      basePrice,
      currency: 'PEN',
      active: true,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    routes.push(route);
    routeMap.set(routeId, route);
  }

  // Insertar en lotes
  const batchSize = 100;
  for (let i = 0; i < routes.length; i += batchSize) {
    const batch = routes.slice(i, i + batchSize);
    await mysqlConn.query(
      `INSERT INTO routes (route_id, route_name, origin_city, destination_city, distance_km, estimated_duration, base_price, currency, active, created_at, updated_at)
       VALUES ${batch.map(() => '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)').join(', ')}`,
      {
        replacements: batch.flatMap(r => [r.routeId, r.routeName, r.originCity, r.destinationCity, r.distanceKm, r.estimatedDuration, r.basePrice, r.currency, r.active, r.createdAt, r.updatedAt]),
        type: mysqlConn.QueryTypes.INSERT
      }
    );
    routeCount += batch.length;
    process.stdout.write(`\r   Insertadas: ${routeCount}/${CONFIG.counts.routes}`);
  }

  console.log(`\n✅ ${routes.length} rutas generadas\n`);
  return Array.from(routeMap.keys());
}

// ============================================================================
// GENERACIÓN DE PASAJEROS
// ============================================================================

async function generatePassengers() {
  console.log(`👥 Generando ${CONFIG.counts.passengers} pasajeros...`);

  const passengers = [];
  const passengerIds = [];

  for (let i = 0; i < CONFIG.counts.passengers; i++) {
    const passengerId = `PASS_${String(i + 1).padStart(6, '0')}`;
    const fullName = faker.person.fullName();
    const email = faker.internet.email().toLowerCase();
    const phone = faker.phone.number('+51 9## ### ###');
    const documentType = faker.helpers.arrayElement(['DNI', 'PASSPORT', 'CE']);
    const documentNumber = documentType === 'DNI'
      ? faker.string.numeric(8)
      : faker.string.alphanumeric(9).toUpperCase();
    const dateOfBirth = faker.date.birthdate({ min: 18, max: 80, mode: 'age' }).toISOString().split('T')[0];
    const registrationDate = faker.date.past({ years: 2 }).toISOString().split('T')[0];
    const status = 'active';

    passengers.push([
      passengerId,
      fullName,
      email,
      phone,
      documentType,
      documentNumber,
      dateOfBirth,
      registrationDate,
      status
    ]);

    passengerIds.push(passengerId);
  }

  // Insertar en lotes
  const batchSize = 500;
  let passengerCount = 0;

  for (let i = 0; i < passengers.length; i += batchSize) {
    const batch = passengers.slice(i, i + batchSize);

    // Crear placeholders para parametros preparados
    const placeholders = batch.map((_, batchIdx) => {
      const offset = batchIdx * 9;
      return `($${offset + 1}, $${offset + 2}, $${offset + 3}, $${offset + 4}, $${offset + 5}, $${offset + 6}, $${offset + 7}, $${offset + 8}, $${offset + 9})`;
    }).join(', ');

    const flatValues = batch.flat();

    await pgClient.query(
      `INSERT INTO passenger (passenger_id, full_name, email, phone, document_type, document_number, date_of_birth, registration_date, status)
       VALUES ${placeholders}`,
      flatValues
    );

    passengerCount += batch.length;
    process.stdout.write(`\r   Insertados: ${passengerCount}/${CONFIG.counts.passengers}`);
  }

  console.log(`\n✅ ${passengers.length} pasajeros generados\n`);
  return passengerIds;
}

// ============================================================================
// GENERACIÓN DE VIAJES
// ============================================================================

async function generateTrips(routeIds) {
  console.log(`🚌 Generando ${CONFIG.counts.trips} viajes...`);

  const trips = [];
  const tripIds = [];
  const now = new Date();

  // Generar viajes de forma controlada para evitar duplicados
  const existingTripIds = new Set();

  for (let i = 0; i < CONFIG.counts.trips; i++) {
    let attempts = 0;
    let tripId, departureDate, hour, minute, routeId;

    // Intentar generar un tripId único
    do {
      routeId = faker.helpers.arrayElement(routeIds);

      // Empezar desde 1 hora en el futuro para evitar problemas de validación
      const minDate = new Date(now.getTime() + 60 * 60 * 1000); // 1 hora después
      departureDate = faker.date.between({
        from: minDate,
        to: new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000) // 90 días
      });

      hour = faker.number.int({ min: 6, max: 22 });
      minute = faker.helpers.arrayElement([0, 15, 30, 45]);
      departureDate.setHours(hour, minute, 0, 0);

      tripId = generateTripId(departureDate, routeId, hour);
      attempts++;
    } while (existingTripIds.has(tripId) && attempts < 50);

    // Si después de 50 intentos aún hay duplicado, agregar segundos random
    if (existingTripIds.has(tripId)) {
      const seconds = faker.number.int({ min: 0, max: 59 });
      departureDate.setSeconds(seconds);
    }

    existingTripIds.add(tripId);

    const durationHours = faker.number.int({ min: 2, max: 18 });
    const arrivalDate = new Date(departureDate.getTime() + durationHours * 60 * 60 * 1000);
    const busCapacity = faker.helpers.arrayElement([30, 40, 45, 50]);
    const availableSeats = busCapacity; // Inicialmente todos disponibles
    const finalPrice = faker.number.int({ min: 25, max: 250 });
    const status = 'scheduled';
    const driverName = faker.person.fullName();
    const busPlate = faker.vehicle.vrm().toUpperCase();

    trips.push({
      tripId,
      routeId,
      departureDateTime: departureDate,
      arrivalDateTime: arrivalDate,
      busCapacity,
      availableSeats,
      finalPrice,
      status,
      driverName,
      busPlate,
      createdAt: new Date(),
      updatedAt: new Date()
    });

    tripIds.push(tripId);
  }

  // Insertar en lotes
  const batchSize = 200;
  let tripCount = 0;

  for (let i = 0; i < trips.length; i += batchSize) {
    const batch = trips.slice(i, i + batchSize);
    await mysqlConn.query(
      `INSERT INTO trips (trip_id, route_id, departure_date_time, arrival_date_time, bus_capacity, available_seats, final_price, status, driver_name, bus_plate, created_at, updated_at)
       VALUES ${batch.map(() => '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)').join(', ')}`,
      {
        replacements: batch.flatMap(t => [t.tripId, t.routeId, t.departureDateTime, t.arrivalDateTime, t.busCapacity, t.availableSeats, t.finalPrice, t.status, t.driverName, t.busPlate, t.createdAt, t.updatedAt]),
        type: mysqlConn.QueryTypes.INSERT
      }
    );

    tripCount += batch.length;
    process.stdout.write(`\r   Insertados: ${tripCount}/${CONFIG.counts.trips}`);
  }

  console.log(`\n✅ ${trips.length} viajes generados\n`);
  return { tripIds, tripsMap: new Map(trips.map(t => [t.tripId, t])) };
}

// ============================================================================
// GENERACIÓN DE TICKETS
// ============================================================================

async function generateTickets(passengerIds, tripIds) {
  console.log(`🎫 Generando ${CONFIG.counts.tickets} tickets...`);

  const tickets = [];
  const tripSeatMap = new Map(); // Para rastrear asientos por viaje

  for (let i = 0; i < CONFIG.counts.tickets; i++) {
    const ticketId = `TICK_${String(i + 1).padStart(8, '0')}`;
    const passengerId = faker.helpers.arrayElement(passengerIds);
    const tripId = faker.helpers.arrayElement(tripIds);

    // Generar número de asiento único por viaje
    if (!tripSeatMap.has(tripId)) {
      tripSeatMap.set(tripId, new Set());
    }

    const usedSeats = tripSeatMap.get(tripId);
    let seatNumber;
    let attempts = 0;

    do {
      seatNumber = `${faker.helpers.arrayElement(['A', 'B', 'C', 'D'])}${faker.number.int({ min: 1, max: 15 })}`;
      attempts++;
      if (attempts > 50) {
        seatNumber = `${faker.helpers.arrayElement(['A', 'B', 'C', 'D'])}${faker.number.int({ min: 1, max: 50 })}`;
        break;
      }
    } while (usedSeats.has(seatNumber));

    usedSeats.add(seatNumber);

    const totalPrice = faker.number.float({ min: 25, max: 250, precision: 0.01 });
    const purchaseDate = faker.date.recent({ days: 30 });
    const bookingReference = faker.string.alphanumeric(8).toUpperCase();

    tickets.push({
      ticket_id: ticketId,
      passenger_id: passengerId,
      trip_id: tripId,
      seat_number: seatNumber,
      booking_status: faker.helpers.arrayElement(['confirmed', 'confirmed', 'confirmed', 'pending', 'cancelled']),
      total_price: totalPrice,
      currency: 'PEN',
      purchase_date: purchaseDate,
      payment_method: faker.helpers.arrayElement(['credit_card', 'debit_card', 'cash', 'bank_transfer']),
      booking_reference: bookingReference,
      created_at: purchaseDate
    });
  }

  // Insertar en lotes
  const batchSize = 1000;
  let ticketCount = 0;

  for (let i = 0; i < tickets.length; i += batchSize) {
    const batch = tickets.slice(i, i + batchSize);
    await mongoDB.collection('tickets').insertMany(batch);

    ticketCount += batch.length;
    process.stdout.write(`\r   Insertados: ${ticketCount}/${CONFIG.counts.tickets}`);
  }

  console.log(`\n✅ ${tickets.length} tickets generados\n`);
  return tripSeatMap;
}

// ============================================================================
// ACTUALIZACIÓN DE ASIENTOS DISPONIBLES
// ============================================================================

async function updateAvailableSeats(tripSeatMap) {
  console.log('🔄 Actualizando asientos disponibles en viajes...');

  let updateCount = 0;
  const totalUpdates = tripSeatMap.size;

  for (const [tripId, seats] of tripSeatMap.entries()) {
    const soldSeats = seats.size;

    await mysqlConn.query(
      `UPDATE trips
       SET available_seats = GREATEST(0, bus_capacity - ?)
       WHERE trip_id = ?`,
      {
        replacements: [soldSeats, tripId],
        type: mysqlConn.QueryTypes.UPDATE
      }
    );

    updateCount++;
    if (updateCount % 100 === 0) {
      process.stdout.write(`\r   Actualizados: ${updateCount}/${totalUpdates}`);
    }
  }

  console.log(`\n✅ ${tripSeatMap.size} viajes actualizados\n`);
}

// ============================================================================
// ESTADÍSTICAS
// ============================================================================

async function showStatistics() {
  console.log('📊 ESTADÍSTICAS FINALES\n');
  console.log('═'.repeat(50));

  // MySQL Stats
  const [routesResult] = await mysqlConn.query('SELECT COUNT(*) as count FROM routes');
  const [tripsResult] = await mysqlConn.query('SELECT COUNT(*) as count FROM trips');
  const [tripsOccupancy] = await mysqlConn.query(`
    SELECT
      AVG((bus_capacity - available_seats) / bus_capacity * 100) as avg_occupancy,
      SUM(bus_capacity - available_seats) as total_sold_seats
    FROM trips
  `);

  console.log('\n🗄️  MySQL (ms-trips):');
  console.log(`   Rutas: ${routesResult[0].count}`);
  console.log(`   Viajes: ${tripsResult[0].count}`);
  console.log(`   Ocupación promedio: ${parseFloat(tripsOccupancy[0].avg_occupancy || 0).toFixed(2)}%`);
  console.log(`   Total asientos vendidos: ${tripsOccupancy[0].total_sold_seats || 0}`);

  // PostgreSQL Stats
  const passengersResult = await pgClient.query('SELECT COUNT(*) as count FROM passenger');
  const activePassengers = await pgClient.query("SELECT COUNT(*) as count FROM passenger WHERE status = 'active'");

  console.log('\n🗄️  PostgreSQL (ms-passengers):');
  console.log(`   Pasajeros totales: ${passengersResult.rows[0].count}`);
  console.log(`   Pasajeros activos: ${activePassengers.rows[0].count}`);

  // MongoDB Stats
  const ticketsCount = await mongoDB.collection('tickets').countDocuments();
  const ticketsByStatus = await mongoDB.collection('tickets').aggregate([
    { $group: { _id: '$booking_status', count: { $sum: 1 } } }
  ]).toArray();

  console.log('\n🗄️  MongoDB (ms-tickets):');
  console.log(`   Tickets totales: ${ticketsCount}`);
  ticketsByStatus.forEach(s => {
    console.log(`   ${s._id}: ${s.count}`);
  });

  // Total
  const totalRecords =
    parseInt(routesResult[0].count) +
    parseInt(tripsResult[0].count) +
    parseInt(passengersResult.rows[0].count) +
    ticketsCount;

  console.log('\n' + '═'.repeat(50));
  console.log(`📈 TOTAL DE REGISTROS: ${totalRecords.toLocaleString()}`);
  console.log('═'.repeat(50) + '\n');
}

// ============================================================================
// MAIN
// ============================================================================

async function main() {
  console.log('\n' + '═'.repeat(60));
  console.log('🚀 GENERACIÓN MASIVA DE DATOS - BUS MVP');
  console.log('═'.repeat(60) + '\n');

  console.log('📋 Configuración:');
  console.log(`   Rutas: ${CONFIG.counts.routes}`);
  console.log(`   Pasajeros: ${CONFIG.counts.passengers}`);
  console.log(`   Viajes: ${CONFIG.counts.trips}`);
  console.log(`   Tickets: ${CONFIG.counts.tickets}`);
  console.log(`   TOTAL: ${Object.values(CONFIG.counts).reduce((a, b) => a + b, 0)} registros\n`);

  const startTime = Date.now();

  try {
    await connectDatabases();
    await cleanDatabases();

    const routeIds = await generateRoutes();
    const passengerIds = await generatePassengers();
    const { tripIds } = await generateTrips(routeIds);
    const tripSeatMap = await generateTickets(passengerIds, tripIds);
    await updateAvailableSeats(tripSeatMap);

    await showStatistics();

    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`⏱️  Tiempo total: ${duration} segundos\n`);
    console.log('✅ Generación masiva completada exitosamente!\n');

  } catch (error) {
    console.error('\n❌ Error en el proceso:', error.message);
    console.error('\n📋 Stack trace:', error.stack);
    process.exit(1);
  } finally {
    await closeDatabases();
  }
}

// Ejecutar
if (require.main === module) {
  main().catch(error => {
    console.error('❌ Error fatal:', error);
    process.exit(1);
  });
}

module.exports = { main };
