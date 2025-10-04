const { Route } = require('../models');

/**
 * @swagger
 * /api/v1/routes:
 *   get:
 *     tags: [Routes]
 *     summary: Listar todas las rutas
 *     description: Obtiene todas las rutas disponibles con filtros opcionales
 *     parameters:
 *       - in: query
 *         name: active
 *         schema:
 *           type: boolean
 *         description: Filtrar por rutas activas/inactivas
 *       - in: query
 *         name: origin
 *         schema:
 *           type: string
 *         description: Filtrar por ciudad de origen
 *       - in: query
 *         name: destination
 *         schema:
 *           type: string
 *         description: Filtrar por ciudad de destino
 *     responses:
 *       200:
 *         description: Lista de rutas
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/Route'
 *                 count:
 *                   type: integer
 */
const getAllRoutes = async (req, res) => {
  try {
    const { active, origin, destination } = req.query;
    
    // Construir filtros
    const where = {};
    if (active !== undefined) {
      where.active = active === 'true';
    }
    if (origin) {
      where.originCity = origin;
    }
    if (destination) {
      where.destinationCity = destination;
    }

    const routes = await Route.findAll({
      where,
      order: [['routeName', 'ASC']]
    });

    res.json({
      data: routes,
      count: routes.length,
      filters: { active, origin, destination }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * @swagger
 * /api/v1/routes/{routeId}:
 *   get:
 *     tags: [Routes]
 *     summary: Obtener ruta por ID
 *     parameters:
 *       - in: path
 *         name: routeId
 *         required: true
 *         schema:
 *           type: string
 *         example: MAD_BCN_001
 *     responses:
 *       200:
 *         description: Detalles de la ruta
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Route'
 *       404:
 *         description: Ruta no encontrada
 */
const getRouteById = async (req, res, next) => {
  try {
    const { routeId } = req.params;
    
    const route = await Route.findByPk(routeId);
    // TEMPORALMENTE SIN ASOCIACIONES HASTA DEFINIR LAS RELACIONES
    // const route = await Route.findByPk(routeId, {
    //   include: [
    //     {
    //       association: 'trips',
    //       limit: 5,
    //       order: [['departureDateTime', 'DESC']]
    //     }
    //   ]
    // });

    if (!route) {
      const error = new Error(`Route with ID ${routeId} not found`);
      error.name = 'NotFoundError';
      throw error;
    }

    res.json(route);
  } catch (error) {
    next(error);
  }
};

/**
 * @swagger
 * /api/v1/routes:
 *   post:
 *     tags: [Routes]
 *     summary: Crear nueva ruta
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/Route'
 *     responses:
 *       201:
 *         description: Ruta creada exitosamente
 *       400:
 *         description: Error de validación
 */
const createRoute = async (req, res, next) => {
  try {
    const routeData = req.body;
    
    const route = await Route.create(routeData);
    
    res.status(201).json({
      message: 'Route created successfully',
      data: route
    });
  } catch (error) {
    next(error);
  }
};

/**
 * @desc Actualizar una ruta
 * @route PUT /api/v1/routes/:routeId
 * @access Public
 */
const updateRoute = async (req, res, next) => {
  try {
    const { routeId } = req.params;
    const updateData = req.body;

    const route = await Route.findByPk(routeId);
    if (!route) {
      const error = new Error(`Route with ID ${routeId} not found`);
      error.statusCode = 404;
      return next(error);
    }

    await route.update(updateData);

    res.status(200).json({
      message: 'Route updated successfully',
      data: route
    });

  } catch (error) {
    next(error);
  }
};

/**
 * @desc Eliminar una ruta
 * @route DELETE /api/v1/routes/:routeId
 * @access Public
 */
const deleteRoute = async (req, res, next) => {
  try {
    const { routeId } = req.params;

    const route = await Route.findByPk(routeId);
    if (!route) {
      const error = new Error(`Route with ID ${routeId} not found`);
      error.statusCode = 404;
      return next(error);
    }

    // Verificar si hay viajes programados para esta ruta
    const Trip = require('../models/Trip');
    const scheduledTrips = await Trip.count({
      where: {
        routeId: routeId,
        status: 'scheduled'
      }
    });

    if (scheduledTrips > 0) {
      const error = new Error(`Cannot delete route with ${scheduledTrips} scheduled trips. Cancel trips first.`);
      error.statusCode = 409;
      return next(error);
    }

    await route.destroy();

    res.status(200).json({
      message: 'Route deleted successfully',
      deletedRoute: {
        routeId: route.routeId,
        routeName: route.routeName,
        route: `${route.originCity} → ${route.destinationCity}`
      }
    });

  } catch (error) {
    next(error);
  }
};

module.exports = {
  getAllRoutes,
  getRouteById,
  createRoute,
  updateRoute,
  deleteRoute
};
