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
  getDataStatus,
  clearAllData
};