const { sequelize } = require('../config/database');
const Route = require('../models/Route');
const Trip = require('../models/Trip');

class DataSeeder {
  constructor() {
    this.routes = [];
    this.trips = [];
  }

  /**
   * Datos de rutas peruanas para el seeder
   */
  getRouteData() {
    return [
      {
        routeId: 'LIM_CUZ_001',
        routeName: 'Lima - Cusco Express',
        originCity: 'Lima',
        destinationCity: 'Cusco',
        distanceKm: 1165.5,
        estimatedDuration: '20:00:00',
        basePrice: 120.00,
        currency: 'PEN',
        active: true
      },
      {
        routeId: 'LIM_ARE_002',
        routeName: 'Lima - Arequipa Ejecutivo',
        originCity: 'Lima',
        destinationCity: 'Arequipa',
        distanceKm: 1009.0,
        estimatedDuration: '16:30:00',
        basePrice: 95.50,
        currency: 'PEN',
        active: true
      },
      {
        routeId: 'LIM_TRU_003',
        routeName: 'Lima - Trujillo Directo',
        originCity: 'Lima',
        destinationCity: 'Trujillo',
        distanceKm: 561.0,
        estimatedDuration: '08:45:00',
        basePrice: 75.00,
        currency: 'PEN',
        active: true
      },
      {
        routeId: 'ARE_CUZ_004',
        routeName: 'Arequipa - Cusco Turístico',
        originCity: 'Arequipa',
        destinationCity: 'Cusco',
        distanceKm: 315.0,
        estimatedDuration: '06:00:00',
        basePrice: 60.00,
        currency: 'PEN',
        active: true
      },
      {
        routeId: 'CUZ_PUN_005',
        routeName: 'Cusco - Puno Altiplano',
        originCity: 'Cusco',
        destinationCity: 'Puno',
        distanceKm: 389.0,
        estimatedDuration: '07:30:00',
        basePrice: 65.00,
        currency: 'PEN',
        active: true
      },
      {
        routeId: 'LIM_ICA_006',
        routeName: 'Lima - Ica Express',
        originCity: 'Lima',
        destinationCity: 'Ica',
        distanceKm: 303.0,
        estimatedDuration: '04:30:00',
        basePrice: 45.00,
        currency: 'PEN',
        active: true
      }
    ];
  }

  /**
   * Datos de viajes para el seeder
   */
  getTripData() {
    const now = new Date();
    const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
    const dayAfterTomorrow = new Date(now.getTime() + 48 * 60 * 60 * 1000);
    const threeDaysLater = new Date(now.getTime() + 72 * 60 * 60 * 1000);
    const fourDaysLater = new Date(now.getTime() + 96 * 60 * 60 * 1000);
    
    return [
      {
        tripId: 'TRP_20250921_LIM_CUZ_01',
        routeId: 'LIM_CUZ_001',
        departureDateTime: new Date(tomorrow.setHours(22, 0, 0, 0)),
        arrivalDateTime: new Date(tomorrow.setHours(22, 0, 0, 0) + 20 * 60 * 60 * 1000),
        busNumber: 'BUS-001',
        driverName: 'Carlos Mendoza',
        busCapacity: 45,
        availableSeats: 45,
        finalPrice: 120.00,
        status: 'scheduled'
      },
      {
        tripId: 'TRP_20250921_LIM_ARE_02',
        routeId: 'LIM_ARE_002',
        departureDateTime: new Date(tomorrow.setHours(23, 30, 0, 0)),
        arrivalDateTime: new Date(tomorrow.setHours(23, 30, 0, 0) + 16.5 * 60 * 60 * 1000),
        busNumber: 'BUS-002',
        driverName: 'Ana Rodriguez',
        busCapacity: 40,
        availableSeats: 35,
        finalPrice: 95.50,
        status: 'scheduled'
      },
      {
        tripId: 'TRP_20250921_LIM_TRU_03',
        routeId: 'LIM_TRU_003',
        departureDateTime: new Date(tomorrow.setHours(6, 0, 0, 0)),
        arrivalDateTime: new Date(tomorrow.setHours(6, 0, 0, 0) + 8.75 * 60 * 60 * 1000),
        busNumber: 'BUS-003',
        driverName: 'Miguel Santos',
        busCapacity: 35,
        availableSeats: 30,
        finalPrice: 75.00,
        status: 'scheduled'
      },
      {
        tripId: 'TRP_20250922_ARE_CUZ_04',
        routeId: 'ARE_CUZ_004',
        departureDateTime: new Date(dayAfterTomorrow.setHours(8, 0, 0, 0)),
        arrivalDateTime: new Date(dayAfterTomorrow.setHours(8, 0, 0, 0) + 6 * 60 * 60 * 1000),
        busNumber: 'BUS-004',
        driverName: 'Carmen López',
        busCapacity: 32,
        availableSeats: 28,
        finalPrice: 60.00,
        status: 'scheduled'
      },
      {
        tripId: 'TRP_20250922_CUZ_PUN_05',
        routeId: 'CUZ_PUN_005',
        departureDateTime: new Date(dayAfterTomorrow.setHours(14, 30, 0, 0)),
        arrivalDateTime: new Date(dayAfterTomorrow.setHours(14, 30, 0, 0) + 7.5 * 60 * 60 * 1000),
        busNumber: 'BUS-005',
        driverName: 'Roberto Quispe',
        busCapacity: 38,
        availableSeats: 38,
        finalPrice: 65.00,
        status: 'scheduled'
      },
      {
        tripId: 'TRP_20250922_LIM_ICA_06',
        routeId: 'LIM_ICA_006',
        departureDateTime: new Date(dayAfterTomorrow.setHours(10, 0, 0, 0)),
        arrivalDateTime: new Date(dayAfterTomorrow.setHours(10, 0, 0, 0) + 4.5 * 60 * 60 * 1000),
        busNumber: 'BUS-006',
        driverName: 'Patricia Flores',
        busCapacity: 30,
        availableSeats: 25,
        finalPrice: 45.00,
        status: 'scheduled'
      },
      {
        tripId: 'TRP_20250923_LIM_CUZ_07',
        routeId: 'LIM_CUZ_001',
        departureDateTime: new Date(threeDaysLater.setHours(21, 30, 0, 0)),
        arrivalDateTime: new Date(threeDaysLater.setHours(21, 30, 0, 0) + 20 * 60 * 60 * 1000),
        busNumber: 'BUS-007',
        driverName: 'Jorge Ramirez',
        busCapacity: 45,
        availableSeats: 40,
        finalPrice: 120.00,
        status: 'scheduled'
      },
      {
        tripId: 'TRP_20250923_LIM_TRU_08',
        routeId: 'LIM_TRU_003',
        departureDateTime: new Date(threeDaysLater.setHours(15, 0, 0, 0)),
        arrivalDateTime: new Date(threeDaysLater.setHours(15, 0, 0, 0) + 8.75 * 60 * 60 * 1000),
        busNumber: 'BUS-008',
        driverName: 'Luis Castillo',
        busCapacity: 35,
        availableSeats: 35,
        finalPrice: 75.00,
        status: 'scheduled'
      },
      {
        tripId: 'TRP_20250924_LIM_ARE_09',
        routeId: 'LIM_ARE_002',
        departureDateTime: new Date(fourDaysLater.setHours(20, 0, 0, 0)),
        arrivalDateTime: new Date(fourDaysLater.setHours(20, 0, 0, 0) + 16.5 * 60 * 60 * 1000),
        busNumber: 'BUS-009',
        driverName: 'Elena Martinez',
        busCapacity: 40,
        availableSeats: 32,
        finalPrice: 95.50,
        status: 'scheduled'
      },
      {
        tripId: 'TRP_20250924_CUZ_PUN_10',
        routeId: 'CUZ_PUN_005',
        departureDateTime: new Date(fourDaysLater.setHours(9, 0, 0, 0)),
        arrivalDateTime: new Date(fourDaysLater.setHours(9, 0, 0, 0) + 7.5 * 60 * 60 * 1000),
        busNumber: 'BUS-010',
        driverName: 'Fernando Silva',
        busCapacity: 38,
        availableSeats: 36,
        finalPrice: 65.00,
        status: 'scheduled'
      }
    ];
  }

  /**
   * Limpiar datos existentes
   */
  async clearExistingData() {
    console.log('🧹 Limpiando datos existentes...');
    
    try {
      await Trip.destroy({ where: {} });
      await Route.destroy({ where: {} });
      console.log('✅ Datos existentes eliminados correctamente');
    } catch (error) {
      console.error('❌ Error limpiando datos:', error.message);
      throw error;
    }
  }

  /**
   * Crear rutas de prueba
   */
  async seedRoutes() {
    console.log('🛣️  Creando rutas de prueba...');
    
    const routeData = this.getRouteData();
    
    try {
      for (const route of routeData) {
        const createdRoute = await Route.create(route);
        this.routes.push(createdRoute);
        console.log(`✅ Ruta creada: ${route.routeName} (${route.routeId})`);
      }
      
      console.log(`🎉 ${this.routes.length} rutas creadas exitosamente`);
    } catch (error) {
      console.error('❌ Error creando rutas:', error.message);
      throw error;
    }
  }

  /**
   * Crear viajes de prueba
   */
  async seedTrips() {
    console.log('🚌 Creando viajes de prueba...');
    
    const tripData = this.getTripData();
    
    try {
      for (const trip of tripData) {
        const createdTrip = await Trip.create(trip);
        this.trips.push(createdTrip);
        console.log(`✅ Viaje creado: ${trip.tripId} - Salida: ${trip.departureDateTime.toLocaleString('es-PE')}`);
      }
      
      console.log(`🎉 ${this.trips.length} viajes creados exitosamente`);
    } catch (error) {
      console.error('❌ Error creando viajes:', error.message);
      throw error;
    }
  }

  /**
   * Verificar datos creados
   */
  async testCreatedData() {
    console.log('🔍 Verificando datos creados...');
    
    try {
      // Verificar rutas
      const routeCount = await Route.count();
      const activeRoutes = await Route.count({ where: { active: true } });
      
      console.log(`📊 Rutas en BD: ${routeCount} (${activeRoutes} activas)`);
      
      // Verificar viajes
      const tripCount = await Trip.count();
      const scheduledTrips = await Trip.count({ where: { status: 'scheduled' } });
      
      console.log(`📊 Viajes en BD: ${tripCount} (${scheduledTrips} programados)`);
      
      // Verificar integridad de datos
      const routesWithTrips = await Route.findAll({
        include: [{
          model: Trip,
          as: 'trips',  // Agregar alias explícito
          required: false
        }]
      });
      
      console.log('\n📋 Resumen por ruta:');
      for (const route of routesWithTrips) {
        const tripCount = route.trips ? route.trips.length : 0;
        console.log(`   ${route.routeName}: ${tripCount} viajes`);
      }
      
      return {
        routes: routeCount,
        trips: tripCount,
        activeRoutes,
        scheduledTrips
      };
      
    } catch (error) {
      console.error('❌ Error verificando datos:', error.message);
      throw error;
    }
  }

  /**
   * Ejecutar todo el proceso de seeding
   */
  async run(options = {}) {
    const { clearData = true, testData = true } = options;
    
    console.log('🌱 Iniciando Data Seeder para ms-trips...\n');
    
    try {
      // Verificar conexión a la base de datos
      await sequelize.authenticate();
      console.log('✅ Conexión a base de datos establecida\n');
      
      // Sincronizar modelos
      await sequelize.sync();
      console.log('✅ Modelos sincronizados\n');
      
      // Limpiar datos existentes si está habilitado
      if (clearData) {
        await this.clearExistingData();
        console.log('');
      }
      
      // Crear rutas
      await this.seedRoutes();
      console.log('');
      
      // Crear viajes
      await this.seedTrips();
      console.log('');
      
      // Verificar datos si está habilitado
      if (testData) {
        const summary = await this.testCreatedData();
        console.log('\n🎉 Data Seeder completado exitosamente!');
        console.log(`📈 Resumen: ${summary.routes} rutas, ${summary.trips} viajes creados`);
        return summary;
      }
      
    } catch (error) {
      console.error('\n💥 Error en Data Seeder:', error.message);
      throw error;
    }
  }
}

module.exports = DataSeeder;