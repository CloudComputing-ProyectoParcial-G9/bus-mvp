#!/usr/bin/env node

/**
 * Script para ejecutar el Data Seeder
 * Uso: node scripts/seed.js [opciones]
 * 
 * Opciones:
 *   --no-clear    No limpiar datos existentes
 *   --no-test     No verificar datos después de crearlos
 *   --help        Mostrar ayuda
 */

const path = require('path');
const { sequelize } = require('../src/config/database');
const DataSeeder = require('../src/seeders/dataSeeder');

async function main() {
  const args = process.argv.slice(2);
  
  // Mostrar ayuda
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
🌱 Data Seeder para ms-trips

Uso: node scripts/seed.js [opciones]

Opciones:
  --no-clear    No limpiar datos existentes antes de crear nuevos
  --no-test     No verificar datos después de crearlos
  --help, -h    Mostrar esta ayuda

Ejemplos:
  node scripts/seed.js                    # Ejecutar con opciones por defecto
  node scripts/seed.js --no-clear         # Mantener datos existentes
  node scripts/seed.js --no-test          # Solo crear datos, no verificar
  node scripts/seed.js --no-clear --no-test  # Solo crear datos nuevos
    `);
    process.exit(0);
  }
  
  // Configurar opciones
  const options = {
    clearData: !args.includes('--no-clear'),
    testData: !args.includes('--no-test')
  };
  
  console.log('🚀 Configuración del seeder:');
  console.log(`   Limpiar datos existentes: ${options.clearData ? '✅' : '❌'}`);
  console.log(`   Verificar datos creados: ${options.testData ? '✅' : '❌'}`);
  console.log('');
  
  const seeder = new DataSeeder();
  
  try {
    const startTime = Date.now();
    
    // Ejecutar seeder
    await seeder.run(options);
    
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    
    console.log(`\n⏱️  Tiempo total: ${duration} segundos`);
    console.log('🎊 ¡Proceso completado exitosamente!');
    
    process.exit(0);
    
  } catch (error) {
    console.error('\n💥 Error ejecutando el seeder:', error.message);
    console.error('\n📋 Stack trace:', error.stack);
    process.exit(1);
    
  } finally {
    // Cerrar conexión a la base de datos
    try {
      await sequelize.close();
      console.log('\n🔌 Conexión a base de datos cerrada');
    } catch (error) {
      console.error('❌ Error cerrando conexión:', error.message);
    }
  }
}

// Manejar errores no capturados
process.on('unhandledRejection', (reason, promise) => {
  console.error('💥 Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  console.error('💥 Uncaught Exception:', error.message);
  console.error('📋 Stack trace:', error.stack);
  process.exit(1);
});

// Ejecutar script principal
main();