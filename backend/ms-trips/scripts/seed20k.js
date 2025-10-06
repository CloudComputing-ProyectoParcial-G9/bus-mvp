#!/usr/bin/env node

/**
 * Script para generar 20,000 viajes de prueba
 * Uso: node scripts/seed20k.js [opciones]
 *
 * Opciones:
 *   --count <number>  Número de viajes a crear (default: 20000)
 *   --no-clear        No limpiar datos existentes
 *   --help            Mostrar ayuda
 */

const { sequelize } = require('../src/config/database');
const Route = require('../src/models/Route');
const Trip = require('../src/models/Trip');

// Ciudades peruanas para generar rutas
const cities = ['Lima', 'Cusco', 'Arequipa', 'Trujillo', 'Puno', 'Ica', 'Chiclayo', 'Piura', 'Tacna', 'Huancayo'];

// Nombres de conductores
const driverNames = [
  'Carlos Mendoza', 'Ana Rodriguez', 'Miguel Santos', 'Carmen López', 'Roberto Quispe',
  'Patricia Flores', 'Jorge Ramirez', 'Luis Castillo', 'Elena Martinez', 'Fernando Silva',
  'Rosa Garcia', 'Pedro Gonzalez', 'Maria Torres', 'Juan Vasquez', 'Sofia Herrera',
  'Diego Morales', 'Laura Rojas', 'Alberto Campos', 'Gabriela Soto', 'Ricardo Vega'
];

// Estados de viaje
const statuses = ['scheduled', 'scheduled', 'scheduled', 'scheduled', 'in_progress', 'completed'];

class MassSeeder {
  constructor(count = 20000) {
    this.count = count;
    this.routes = [];
  }

  /**
   * Generar rutas base (20 rutas diferentes)
   */
  generateRoutes() {
    const routes = [];
    let routeCounter = 1;

    for (let i = 0; i < cities.length; i++) {
      for (let j = 0; j < cities.length; j++) {
        if (i !== j && routes.length < 20) {
          const origin = cities[i];
          const destination = cities[j];
          const distance = Math.floor(Math.random() * 1000) + 100;
          const duration = Math.floor(distance / 60); // ~60 km/h promedio

          routes.push({
            routeId: `${origin.substring(0, 3).toUpperCase()}_${destination.substring(0, 3).toUpperCase()}_${String(routeCounter).padStart(3, '0')}`,
            routeName: `${origin} - ${destination} Express`,
            originCity: origin,
            destinationCity: destination,
            distanceKm: distance,
            estimatedDuration: `${String(Math.floor(duration)).padStart(2, '0')}:${String(Math.floor((duration % 1) * 60)).padStart(2, '0')}:00`,
            basePrice: Math.floor(distance * 0.08) + 30,
            currency: 'PEN',
            active: true
          });
          routeCounter++;
        }
      }
    }

    return routes;
  }

  /**
   * Generar un tripId único
   */
  generateTripId(date, routeId, counter) {
    const dateStr = date.toISOString().substring(0, 10).replace(/-/g, '');
    const [origin, dest] = routeId.split('_').slice(0, 2);
    return `TRP_${dateStr}_${origin}_${dest}_${String(counter).padStart(5, '0')}`;
  }

  /**
   * Generar placa de bus
   */
  generateBusPlate(counter) {
    const letters = String.fromCharCode(65 + Math.floor(Math.random() * 26)) +
                   String.fromCharCode(65 + Math.floor(Math.random() * 26)) +
                   String.fromCharCode(65 + Math.floor(Math.random() * 26));
    const numbers = String(counter % 1000).padStart(3, '0');
    return `${letters}-${numbers}`;
  }

  /**
   * Generar viajes masivamente
   */
  async generateTrips() {
    console.log(`🚌 Generando ${this.count.toLocaleString()} viajes...`);

    const trips = [];
    const batchSize = 1000; // Insertar en lotes de 1000
    let tripCounter = 1;

    // Generar viajes distribuidos en los próximos 90 días
    const startDate = new Date();
    startDate.setHours(startDate.getHours() + 1, 0, 0, 0); // Empezar desde la próxima hora

    for (let i = 0; i < this.count; i++) {
      // Seleccionar ruta aleatoria
      const route = this.routes[Math.floor(Math.random() * this.routes.length)];

      // Generar fecha aleatoria en los próximos 90 días
      const daysOffset = Math.floor(Math.random() * 90);
      const hoursOffset = Math.floor(Math.random() * 24);
      const departureDate = new Date(startDate);
      departureDate.setDate(departureDate.getDate() + daysOffset);
      departureDate.setHours(hoursOffset, 0, 0, 0);

      // Calcular fecha de llegada basada en duración estimada
      const [hours, minutes] = route.estimatedDuration.split(':').map(Number);
      const arrivalDate = new Date(departureDate);
      arrivalDate.setHours(arrivalDate.getHours() + hours);
      arrivalDate.setMinutes(arrivalDate.getMinutes() + minutes);

      // Capacidad aleatoria entre 30 y 50
      const busCapacity = Math.floor(Math.random() * 21) + 30;

      // Asientos disponibles aleatorios (0 a capacidad completa)
      const availableSeats = Math.floor(Math.random() * (busCapacity + 1));

      // Precio con variación del ±20% sobre el precio base
      const priceVariation = (Math.random() * 0.4 - 0.2); // -20% a +20%
      const finalPrice = Math.round(route.basePrice * (1 + priceVariation) * 100) / 100;

      // Estado aleatorio (más probabilidad de scheduled)
      const status = statuses[Math.floor(Math.random() * statuses.length)];

      trips.push({
        tripId: this.generateTripId(departureDate, route.routeId, tripCounter),
        routeId: route.routeId,
        departureDateTime: departureDate,
        arrivalDateTime: arrivalDate,
        busCapacity: busCapacity,
        availableSeats: availableSeats,
        finalPrice: finalPrice,
        status: status,
        driverName: driverNames[Math.floor(Math.random() * driverNames.length)],
        busPlate: this.generateBusPlate(tripCounter)
      });

      tripCounter++;

      // Insertar en lotes
      if (trips.length >= batchSize || i === this.count - 1) {
        await Trip.bulkCreate(trips, {
          validate: true,
          individualHooks: false // Desactivar hooks para mejor performance
        });

        const progress = ((i + 1) / this.count * 100).toFixed(1);
        console.log(`   ✅ Progreso: ${progress}% (${(i + 1).toLocaleString()}/${this.count.toLocaleString()} viajes)`);

        trips.length = 0; // Limpiar array
      }
    }

    console.log(`🎉 ${this.count.toLocaleString()} viajes creados exitosamente`);
  }

  /**
   * Limpiar datos existentes
   */
  async clearExistingData() {
    console.log('🧹 Limpiando datos existentes...');

    try {
      await Trip.destroy({ where: {}, truncate: true });
      await Route.destroy({ where: {}, truncate: true });
      console.log('✅ Datos existentes eliminados correctamente');
    } catch (error) {
      console.error('❌ Error limpiando datos:', error.message);
      throw error;
    }
  }

  /**
   * Crear rutas en la base de datos
   */
  async seedRoutes() {
    console.log('🛣️  Creando rutas...');

    const routeData = this.generateRoutes();

    try {
      this.routes = await Route.bulkCreate(routeData, { validate: true });
      console.log(`✅ ${this.routes.length} rutas creadas exitosamente`);
    } catch (error) {
      console.error('❌ Error creando rutas:', error.message);
      throw error;
    }
  }

  /**
   * Mostrar estadísticas finales
   */
  async showStats() {
    console.log('\n📊 Estadísticas finales:');

    const routeCount = await Route.count();
    const tripCount = await Trip.count();
    const scheduledTrips = await Trip.count({ where: { status: 'scheduled' } });
    const inProgressTrips = await Trip.count({ where: { status: 'in_progress' } });
    const completedTrips = await Trip.count({ where: { status: 'completed' } });

    console.log(`   📍 Rutas: ${routeCount.toLocaleString()}`);
    console.log(`   🚌 Viajes totales: ${tripCount.toLocaleString()}`);
    console.log(`   📅 Programados: ${scheduledTrips.toLocaleString()}`);
    console.log(`   🚦 En progreso: ${inProgressTrips.toLocaleString()}`);
    console.log(`   ✅ Completados: ${completedTrips.toLocaleString()}`);
  }

  /**
   * Ejecutar el proceso completo
   */
  async run(options = {}) {
    const { clearData = true } = options;

    console.log('🌱 Iniciando generación masiva de datos...\n');
    console.log(`📈 Objetivo: ${this.count.toLocaleString()} viajes\n`);

    const startTime = Date.now();

    try {
      // Verificar conexión
      await sequelize.authenticate();
      console.log('✅ Conexión a base de datos establecida\n');

      // Sincronizar modelos
      await sequelize.sync();
      console.log('✅ Modelos sincronizados\n');

      // Limpiar datos si está habilitado
      if (clearData) {
        await this.clearExistingData();
        console.log('');
      }

      // Crear rutas
      await this.seedRoutes();
      console.log('');

      // Crear viajes masivamente
      await this.generateTrips();

      // Mostrar estadísticas
      await this.showStats();

      const endTime = Date.now();
      const duration = ((endTime - startTime) / 1000).toFixed(2);

      console.log(`\n⏱️  Tiempo total: ${duration} segundos`);
      console.log('🎊 ¡Proceso completado exitosamente!');

    } catch (error) {
      console.error('\n💥 Error en el proceso:', error.message);
      console.error('📋 Stack trace:', error.stack);
      throw error;
    }
  }
}

// Función principal
async function main() {
  const args = process.argv.slice(2);

  // Mostrar ayuda
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
🌱 Generador masivo de datos para ms-trips

Uso: node scripts/seed20k.js [opciones]

Opciones:
  --count <number>  Número de viajes a crear (default: 20000)
  --no-clear        No limpiar datos existentes antes de crear nuevos
  --help, -h        Mostrar esta ayuda

Ejemplos:
  node scripts/seed20k.js                    # Crear 20,000 viajes
  node scripts/seed20k.js --count 50000      # Crear 50,000 viajes
  node scripts/seed20k.js --no-clear         # Agregar sin limpiar datos existentes
    `);
    process.exit(0);
  }

  // Obtener cantidad de viajes
  let count = 20000;
  const countIndex = args.indexOf('--count');
  if (countIndex !== -1 && args[countIndex + 1]) {
    count = parseInt(args[countIndex + 1], 10);
    if (isNaN(count) || count <= 0) {
      console.error('❌ El valor de --count debe ser un número positivo');
      process.exit(1);
    }
  }

  // Configurar opciones
  const options = {
    clearData: !args.includes('--no-clear')
  };

  console.log('🚀 Configuración:');
  console.log(`   Cantidad de viajes: ${count.toLocaleString()}`);
  console.log(`   Limpiar datos existentes: ${options.clearData ? '✅' : '❌'}`);
  console.log('');

  const seeder = new MassSeeder(count);

  try {
    await seeder.run(options);
    process.exit(0);
  } catch (error) {
    console.error('\n💥 Error ejecutando el seeder:', error.message);
    process.exit(1);
  } finally {
    try {
      await sequelize.close();
      console.log('🔌 Conexión a base de datos cerrada');
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

// Ejecutar
main();
