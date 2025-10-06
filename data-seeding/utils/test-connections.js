#!/usr/bin/env node

/**
 * Utilidad para probar las conexiones a todas las bases de datos
 */

const chalk = require('chalk');
const DatabaseManager = require('../config/database');
const CONFIG = require('../config/constants');

async function testConnections() {
  console.log(chalk.cyan('\n🔧 PROBANDO CONEXIONES - BUS MVP\n'));
  
  const dbManager = new DatabaseManager();
  let allConnected = true;
  
  try {
    // Probar MySQL
    console.log(chalk.blue('🔵 Probando MySQL (ms-trips)...'));
    console.log(`   Host: ${CONFIG.mysql.host}:${CONFIG.mysql.port}`);
    console.log(`   Base de datos: ${CONFIG.mysql.database}`);
    
    try {
      await dbManager.connectMySQL();
      const [result] = await dbManager.mysql.query('SELECT VERSION() as version');
      console.log(chalk.green(`   ✅ Conectado - MySQL ${result[0].version}\n`));
    } catch (error) {
      console.log(chalk.red(`   ❌ Error: ${error.message}\n`));
      allConnected = false;
    }
    
    // Probar PostgreSQL
    console.log(chalk.green('🟢 Probando PostgreSQL (ms-passengers)...'));
    console.log(`   Host: ${CONFIG.postgres.host}:${CONFIG.postgres.port}`);
    console.log(`   Base de datos: ${CONFIG.postgres.database}`);
    
    try {
      await dbManager.connectPostgreSQL();
      const result = await dbManager.postgres.query('SELECT version()');
      console.log(chalk.green(`   ✅ Conectado - ${result.rows[0].version.split(' ')[0]} ${result.rows[0].version.split(' ')[1]}\n`));
    } catch (error) {
      console.log(chalk.red(`   ❌ Error: ${error.message}\n`));
      allConnected = false;
    }
    
    // Probar MongoDB
    console.log(chalk.yellow('🟡 Probando MongoDB (ms-tickets)...'));
    console.log(`   URL: ${CONFIG.mongodb.url}`);
    console.log(`   Base de datos: ${CONFIG.mongodb.database}`);
    
    try {
      await dbManager.connectMongoDB();
      const admin = dbManager.mongo.admin();
      const info = await admin.serverInfo();
      console.log(chalk.green(`   ✅ Conectado - MongoDB ${info.version}\n`));
    } catch (error) {
      console.log(chalk.red(`   ❌ Error: ${error.message}\n`));
      allConnected = false;
    }
    
    // Resultado final
    if (allConnected) {
      console.log(chalk.green('🎉 Todas las conexiones exitosas'));
      console.log(chalk.green('✅ El sistema está listo para generar datos\n'));
    } else {
      console.log(chalk.red('❌ Algunas conexiones fallaron'));
      console.log(chalk.yellow('ℹ️  Revisa la configuración en el archivo .env\n'));
      process.exit(1);
    }
    
  } catch (error) {
    console.error(chalk.red('❌ Error general:'), error.message);
    process.exit(1);
  } finally {
    await dbManager.closeAll();
  }
}

if (require.main === module) {
  testConnections().catch(error => {
    console.error(chalk.red('❌ Error fatal:'), error);
    process.exit(1);
  });
}

module.exports = { testConnections };
