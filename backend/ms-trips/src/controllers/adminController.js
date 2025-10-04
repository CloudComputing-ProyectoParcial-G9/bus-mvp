const DataSeeder = require('../seeders/dataSeeder');

/**
 * @desc Ejecutar data seeder
 * @route POST /api/v1/admin/seed
 * @access Private (solo para desarrollo)
 */
const runSeeder = async (req, res) => {
  try {
    const { clearData = true, testData = true } = req.body;
    
    // Solo permitir en desarrollo
    if (process.env.NODE_ENV === 'production') {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'Data seeder not available in production',
        code: 'SEEDER_FORBIDDEN'
      });
    }
    
    const seeder = new DataSeeder();
    
    const startTime = Date.now();
    
    const summary = await seeder.run({ clearData, testData });
    
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    
    res.status(200).json({
      message: 'Data seeder executed successfully',
      summary: {
        routes: summary.routes,
        trips: summary.trips,
        activeRoutes: summary.activeRoutes,
        scheduledTrips: summary.scheduledTrips,
        executionTime: `${duration}s`
      },
      options: {
        clearData,
        testData
      },
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    res.status(500).json({
      error: 'Seeder Error',
      message: error.message,
      code: 'SEEDER_EXECUTION_ERROR'
    });
  }
};

/**
 * @desc Verificar datos existentes
 * @route GET /api/v1/admin/data-status
 * @access Private (solo para desarrollo)
 */
const getDataStatus = async (req, res) => {
  try {
    const Route = require('../models/Route');
    const Trip = require('../models/Trip');
    
    const routeCount = await Route.count();
    const tripCount = await Trip.count();
    const activeRoutes = await Route.count({ where: { active: true } });
    const scheduledTrips = await Trip.count({ where: { status: 'scheduled' } });
    
    // Obtener resumen básico sin asociaciones
    const routes = await Route.findAll({
      attributes: ['routeId', 'routeName', 'originCity', 'destinationCity'],
      order: [['createdAt', 'ASC']]
    });
    
    const trips = await Trip.findAll({
      attributes: ['tripId', 'routeId', 'status', 'departureDateTime'],
      order: [['departureDateTime', 'ASC']]
    });
    
    // Crear resumen manual
    const routeDetails = routes.map(route => {
      const routeTrips = trips.filter(trip => trip.routeId === route.routeId);
      return {
        routeId: route.routeId,
        routeName: route.routeName,
        route: `${route.originCity} → ${route.destinationCity}`,
        tripCount: routeTrips.length,
        scheduledTrips: routeTrips.filter(trip => trip.status === 'scheduled').length
      };
    });
    
    res.status(200).json({
      message: 'Database status retrieved successfully',
      summary: {
        totalRoutes: routeCount,
        totalTrips: tripCount,
        activeRoutes,
        scheduledTrips
      },
      routes: routeDetails,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    res.status(500).json({
      error: 'Database Status Error',
      message: error.message,
      code: 'DATA_STATUS_ERROR'
    });
  }
};

/**
 * @desc Limpiar todos los datos
 * @route DELETE /api/v1/admin/clear-data
 * @access Private (solo para desarrollo)
 */
const clearAllData = async (req, res) => {
  try {
    // Solo permitir en desarrollo
    if (process.env.NODE_ENV === 'production') {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'Data clearing not available in production',
        code: 'CLEAR_FORBIDDEN'
      });
    }
    
    const Trip = require('../models/Trip');
    const Route = require('../models/Route');
    
    const tripCount = await Trip.count();
    const routeCount = await Route.count();
    
    await Trip.destroy({ where: {} });
    await Route.destroy({ where: {} });
    
    res.status(200).json({
      message: 'All data cleared successfully',
      deleted: {
        trips: tripCount,
        routes: routeCount
      },
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    res.status(500).json({
      error: 'Clear Data Error',
      message: error.message,
      code: 'CLEAR_DATA_ERROR'
    });
  }
};

module.exports = {
  runSeeder,
  getDataStatus,
  clearAllData
};