#!/usr/bin/env node

/**
 * Utilidad para mostrar estadísticas de todas las bases de datos
 */

const chalk = require('chalk');
const DatabaseManager = require('../config/database');

async function showStatistics() {
  console.log(chalk.cyan('\n📊 ESTADÍSTICAS DE BASES DE DATOS - BUS MVP\n'));
  
  const dbManager = new DatabaseManager();
  
  try {
    await dbManager.connectAll();
    
    // Estadísticas MySQL (trips)
    console.log(chalk.blue('🔵 MySQL (ms-trips):'));
    const [routesResult] = await dbManager.mysql.query('SELECT COUNT(*) as count FROM routes');
    const [tripsResult] = await dbManager.mysql.query('SELECT COUNT(*) as count FROM trips');
    const [activeRoutesResult] = await dbManager.mysql.query('SELECT COUNT(*) as count FROM routes WHERE active = true');
    
    console.log(`   📍 Rutas:        ${chalk.white(routesResult[0].count.toLocaleString())} (${activeRoutesResult[0].count} activas)`);
    console.log(`   🚌 Viajes:       ${chalk.white(tripsResult[0].count.toLocaleString())}`);
    
    // Estadísticas PostgreSQL (passengers)
    console.log(chalk.green('\n🟢 PostgreSQL (ms-passengers):'));
    const passengersResult = await dbManager.postgres.query('SELECT COUNT(*) as count FROM passengers');
    const recentPassengersResult = await dbManager.postgres.query(
      "SELECT COUNT(*) as count FROM passengers WHERE created_at > NOW() - INTERVAL '30 days'"
    );
    
    console.log(`   👥 Pasajeros:    ${chalk.white(parseInt(passengersResult.rows[0].count).toLocaleString())} (${recentPassengersResult.rows[0].count} últimos 30 días)`);
    
    // Estadísticas MongoDB (tickets)
    console.log(chalk.yellow('\n🟡 MongoDB (ms-tickets):'));
    const ticketsCount = await dbManager.mongo.collection('tickets').countDocuments();
    const confirmedTickets = await dbManager.mongo.collection('tickets').countDocuments({ booking_status: 'confirmed' });
    const pendingTickets = await dbManager.mongo.collection('tickets').countDocuments({ booking_status: 'pending' });
    
    console.log(`   🎫 Tickets:      ${chalk.white(ticketsCount.toLocaleString())}`);
    console.log(`      Confirmados:  ${chalk.green(confirmedTickets.toLocaleString())}`);
    console.log(`      Pendientes:   ${chalk.yellow(pendingTickets.toLocaleString())}`);
    
    // Total general
    const totalRecords = 
      routesResult[0].count +
      tripsResult[0].count +
      parseInt(passengersResult.rows[0].count) +
      ticketsCount;

    console.log(chalk.cyan('\n' + '═'.repeat(50)));
    console.log(`${chalk.magenta('📊 TOTAL GENERAL:')} ${chalk.white(totalRecords.toLocaleString())} registros`);
    console.log(chalk.cyan('═'.repeat(50) + '\n'));
    
    // Integridad de datos
    console.log(chalk.blue('🔍 Verificación de integridad:'));
    
    // Verificar que existen tickets para viajes existentes
    const tripIds = await dbManager.mysql.query('SELECT trip_id FROM trips LIMIT 10');
    let validTickets = 0;
    
    for (const trip of tripIds[0]) {
      const count = await dbManager.mongo.collection('tickets').countDocuments({ trip_id: trip.trip_id });
      if (count > 0) validTickets++;
    }
    
    console.log(`   ✅ Viajes con tickets: ${validTickets}/${tripIds[0].length} verificados`);
    
    // Verificar que existen tickets para pasajeros existentes
    const passengerResult = await dbManager.postgres.query('SELECT passenger_id FROM passengers LIMIT 10');
    let validPassengerTickets = 0;
    
    for (const passenger of passengerResult.rows) {
      const count = await dbManager.mongo.collection('tickets').countDocuments({ passenger_id: passenger.passenger_id });
      if (count > 0) validPassengerTickets++;
    }
    
    console.log(`   ✅ Pasajeros con tickets: ${validPassengerTickets}/${passengerResult.rows.length} verificados\n`);
    
  } catch (error) {
    console.error(chalk.red('❌ Error obteniendo estadísticas:'), error.message);
    process.exit(1);
  } finally {
    await dbManager.closeAll();
  }
}

if (require.main === module) {
  showStatistics().catch(error => {
    console.error(chalk.red('❌ Error fatal:'), error);
    process.exit(1);
  });
}

module.exports = { showStatistics };
