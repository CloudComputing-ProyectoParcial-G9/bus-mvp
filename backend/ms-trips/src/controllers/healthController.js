const { testConnection } = require('../config/database');
const { Route, Trip } = require('../models');

/**
 * @swagger
 * /health:
 *   get:
 *     tags: [Health]
 *     summary: Health check básico
 *     description: Verifica que el servicio está funcionando
 *     responses:
 *       200:
 *         description: Servicio funcionando correctamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: "healthy"
 *                 timestamp:
 *                   type: string
 *                   format: date-time
 *                 service:
 *                   type: string
 *                   example: "ms-trips"
 *                 version:
 *                   type: string
 *                   example: "1.0.0"
 */
const healthCheck = async (req, res) => {
  try {
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'ms-trips',
      version: process.env.PROJECT_VERSION || '1.0.0',
      environment: process.env.NODE_ENV || 'development'
    });
  } catch (error) {
    res.status(500).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
};

/**
 * @swagger
 * /health/db:
 *   get:
 *     tags: [Health]
 *     summary: Health check de base de datos
 *     description: Verifica la conexión a MySQL y cuenta registros
 *     responses:
 *       200:
 *         description: Base de datos funcionando correctamente
 *       503:
 *         description: Error en la base de datos
 */
const healthCheckDb = async (req, res) => {
  try {
    // Probar conexión
    const isConnected = await testConnection();
    
    if (!isConnected) {
      return res.status(503).json({
        status: 'unhealthy',
        database: 'disconnected',
        timestamp: new Date().toISOString(),
        error: 'Cannot connect to database'
      });
    }

    // Contar registros (opcional)
    const routeCount = await Route.count();
    const tripCount = await Trip.count();

    res.json({
      status: 'healthy',
      database: 'connected',
      timestamp: new Date().toISOString(),
      tables: {
        routes: routeCount,
        trips: tripCount
      }
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      database: 'error',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
};

module.exports = {
  healthCheck,
  healthCheckDb
};
