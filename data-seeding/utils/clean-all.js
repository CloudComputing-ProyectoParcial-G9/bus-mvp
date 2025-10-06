#!/usr/bin/env node

/**
 * Utilidad para limpiar todas las bases de datos del Bus MVP
 */

const chalk = require('chalk');
const DatabaseManager = require('../config/database');

async function cleanAll() {
  console.log(chalk.red('\n⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos de las bases de datos\n'));
  
  const dbManager = new DatabaseManager();
  
  try {
    console.log(chalk.blue('🔌 Conectando a las bases de datos...'));
    await dbManager.connectAll();
    
    console.log(chalk.yellow('🧹 Limpiando todas las bases de datos...'));
    await dbManager.cleanAll();
    
    console.log(chalk.green('✅ Todas las bases de datos han sido limpiadas exitosamente\n'));
    
  } catch (error) {
    console.error(chalk.red('❌ Error limpiando bases de datos:'), error.message);
    process.exit(1);
  } finally {
    await dbManager.closeAll();
  }
}

if (require.main === module) {
  cleanAll().catch(error => {
    console.error(chalk.red('❌ Error fatal:'), error);
    process.exit(1);
  });
}

module.exports = { cleanAll };
