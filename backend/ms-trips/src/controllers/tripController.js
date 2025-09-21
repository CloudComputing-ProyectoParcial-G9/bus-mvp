const Trip = require('../models/Trip');
const Route = require('../models/Route');

/**
 * @desc Obtener todos los viajes con filtros opcionales
 * @route GET /api/v1/trips
 * @access Public
 */
const getAllTrips = async (req, res, next) => {
  try {
    const { 
      routeId, 
      status, 
      departureDate,
      originCity,
      destinationCity,
      page = 1, 
      limit = 10 
    } = req.query;

    // Construir filtros básicos
    const whereConditions = {};
    
    if (routeId) {
      whereConditions.routeId = routeId;
    }
    
    if (status) {
      whereConditions.status = status;
    }
    
    if (departureDate) {
      const startOfDay = new Date(departureDate);
      const endOfDay = new Date(departureDate);
      endOfDay.setHours(23, 59, 59, 999);
      
      whereConditions.departureDateTime = {
        [require('sequelize').Op.between]: [startOfDay, endOfDay]
      };
    }

    // Calcular offset para paginación
    const offset = (parseInt(page) - 1) * parseInt(limit);

    // BÚSQUEDA SIMPLIFICADA SIN ASOCIACIONES
    let trips;
    
    if (originCity || destinationCity) {
      // Si se filtran por ciudades, buscar rutas primero
      const routeWhere = {};
      if (originCity) routeWhere.originCity = originCity;
      if (destinationCity) routeWhere.destinationCity = destinationCity;
      
      const matchingRoutes = await Route.findAll({
        where: routeWhere,
        attributes: ['routeId']
      });
      
      if (matchingRoutes.length === 0) {
        return res.status(200).json({
          data: [],
          pagination: {
            currentPage: parseInt(page),
            totalPages: 0,
            totalItems: 0,
            itemsPerPage: parseInt(limit)
          },
          filters: {
            routeId,
            status,
            departureDate,
            originCity,
            destinationCity
          }
        });
      }
      
      whereConditions.routeId = {
        [require('sequelize').Op.in]: matchingRoutes.map(route => route.routeId)
      };
    }

    trips = await Trip.findAndCountAll({
      where: whereConditions,
      order: [['departureDateTime', 'ASC']],
      limit: parseInt(limit),
      offset: offset
    });

    res.status(200).json({
      data: trips.rows,
      pagination: {
        currentPage: parseInt(page),
        totalPages: Math.ceil(trips.count / parseInt(limit)),
        totalItems: trips.count,
        itemsPerPage: parseInt(limit)
      },
      filters: {
        routeId,
        status,
        departureDate,
        originCity,
        destinationCity
      }
    });

  } catch (error) {
    next(error);
  }
};

/**
 * @desc Obtener un viaje por ID
 * @route GET /api/v1/trips/:tripId
 * @access Public
 */
const getTripById = async (req, res, next) => {
  try {
    const { tripId } = req.params;
    
    const trip = await Trip.findByPk(tripId);

    if (!trip) {
      const error = new Error(`Trip with ID ${tripId} not found`);
      error.statusCode = 404;
      return next(error);
    }

    res.status(200).json(trip);

  } catch (error) {
    next(error);
  }
};

/**
 * @desc Crear un nuevo viaje
 * @route POST /api/v1/trips
 * @access Public
 */
const createTrip = async (req, res, next) => {
  try {
    const tripData = req.body;
    
    // Verificar que la ruta existe
    const route = await Route.findByPk(tripData.routeId);
    if (!route) {
      const error = new Error(`Route with ID ${tripData.routeId} not found`);
      error.statusCode = 404;
      return next(error);
    }

    const trip = await Trip.create(tripData);

    res.status(201).json({
      message: 'Trip created successfully',
      data: trip
    });

  } catch (error) {
    next(error);
  }
};

/**
 * @desc Actualizar un viaje
 * @route PUT /api/v1/trips/:tripId
 * @access Public
 */
const updateTrip = async (req, res, next) => {
  try {
    const { tripId } = req.params;
    const updateData = req.body;

    const trip = await Trip.findByPk(tripId);
    if (!trip) {
      const error = new Error(`Trip with ID ${tripId} not found`);
      error.statusCode = 404;
      return next(error);
    }

    // Si se está actualizando la ruta, verificar que existe
    if (updateData.routeId && updateData.routeId !== trip.routeId) {
      const route = await Route.findByPk(updateData.routeId);
      if (!route) {
        const error = new Error(`Route with ID ${updateData.routeId} not found`);
        error.statusCode = 404;
        return next(error);
      }
    }

    await trip.update(updateData);

    res.status(200).json({
      message: 'Trip updated successfully',
      data: trip
    });

  } catch (error) {
    next(error);
  }
};

/**
 * @desc Eliminar un viaje
 * @route DELETE /api/v1/trips/:tripId
 * @access Public
 */
const deleteTrip = async (req, res, next) => {
  try {
    const { tripId } = req.params;

    const trip = await Trip.findByPk(tripId);
    if (!trip) {
      const error = new Error(`Trip with ID ${tripId} not found`);
      error.statusCode = 404;
      return next(error);
    }

    await trip.destroy();

    res.status(200).json({
      message: 'Trip deleted successfully',
      deletedTrip: {
        tripId: trip.tripId,
        routeId: trip.routeId,
        departureDateTime: trip.departureDateTime
      }
    });

  } catch (error) {
    next(error);
  }
};

/**
 * @desc Buscar viajes con criterios específicos
 * @route GET /api/v1/trips/search
 * @access Public
 */
const searchTrips = async (req, res, next) => {
  try {
    const { 
      origin, 
      destination, 
      departureDate,
      minSeats = 1,
      maxPrice,
      page = 1,
      limit = 20
    } = req.query;

    if (!origin || !destination || !departureDate) {
      const error = new Error('Origin, destination, and departure date are required for search');
      error.statusCode = 400;
      return next(error);
    }

    // BÚSQUEDA SIMPLIFICADA SIN ASOCIACIONES (temporalmente)
    // Primero encontrar rutas que coincidan
    const matchingRoutes = await Route.findAll({
      where: {
        originCity: origin,
        destinationCity: destination,
        active: true
      },
      attributes: ['routeId', 'routeName', 'originCity', 'destinationCity', 'distanceKm', 'estimatedDuration']
    });

    if (matchingRoutes.length === 0) {
      return res.status(200).json({
        data: [],
        pagination: {
          currentPage: parseInt(page),
          totalPages: 0,
          totalItems: 0,
          itemsPerPage: parseInt(limit)
        },
        searchCriteria: {
          origin,
          destination,
          departureDate,
          minSeats: parseInt(minSeats),
          maxPrice: maxPrice ? parseFloat(maxPrice) : null
        },
        message: 'No routes found for the specified origin and destination'
      });
    }

    // Construir filtros para fecha
    const startOfDay = new Date(departureDate);
    const endOfDay = new Date(departureDate);
    endOfDay.setHours(23, 59, 59, 999);

    // Filtros para el viaje
    const tripWhere = {
      routeId: {
        [require('sequelize').Op.in]: matchingRoutes.map(route => route.routeId)
      },
      departureDateTime: {
        [require('sequelize').Op.between]: [startOfDay, endOfDay]
      },
      availableSeats: {
        [require('sequelize').Op.gte]: parseInt(minSeats)
      },
      status: 'scheduled'
    };

    if (maxPrice) {
      tripWhere.finalPrice = {
        [require('sequelize').Op.lte]: parseFloat(maxPrice)
      };
    }

    const offset = (parseInt(page) - 1) * parseInt(limit);

    const trips = await Trip.findAndCountAll({
      where: tripWhere,
      order: [['departureDateTime', 'ASC'], ['finalPrice', 'ASC']],
      limit: parseInt(limit),
      offset: offset
    });

    // Agregar información de ruta manualmente
    const tripsWithRoutes = trips.rows.map(trip => {
      const route = matchingRoutes.find(r => r.routeId === trip.routeId);
      return {
        ...trip.toJSON(),
        Route: route ? route.toJSON() : null
      };
    });

    res.status(200).json({
      data: tripsWithRoutes,
      pagination: {
        currentPage: parseInt(page),
        totalPages: Math.ceil(trips.count / parseInt(limit)),
        totalItems: trips.count,
        itemsPerPage: parseInt(limit)
      },
      searchCriteria: {
        origin,
        destination,
        departureDate,
        minSeats: parseInt(minSeats),
        maxPrice: maxPrice ? parseFloat(maxPrice) : null
      }
    });

  } catch (error) {
    next(error);
  }
};

/**
 * @desc Reservar asientos en un viaje
 * @route PATCH /api/v1/trips/:tripId/seats
 * @access Public
 */
const updateSeats = async (req, res, next) => {
  try {
    const { tripId } = req.params;
    const { seatsToReserve, seatsToRelease } = req.body;

    if (!seatsToReserve && !seatsToRelease) {
      const error = new Error('Either seatsToReserve or seatsToRelease must be provided');
      error.statusCode = 400;
      return next(error);
    }

    if (seatsToReserve && seatsToRelease) {
      const error = new Error('Cannot reserve and release seats in the same operation');
      error.statusCode = 400;
      return next(error);
    }

    const trip = await Trip.findByPk(tripId);
    if (!trip) {
      const error = new Error(`Trip with ID ${tripId} not found`);
      error.statusCode = 404;
      return next(error);
    }

    let newAvailableSeats;
    let operation;

    if (seatsToReserve) {
      newAvailableSeats = await trip.reserveSeats(parseInt(seatsToReserve));
      operation = 'reserved';
    } else {
      newAvailableSeats = await trip.releaseSeats(parseInt(seatsToRelease));
      operation = 'released';
    }

    res.status(200).json({
      message: `Seats ${operation} successfully`,
      tripId: trip.tripId,
      seatsOperation: {
        operation,
        seats: seatsToReserve || seatsToRelease,
        newAvailableSeats,
        totalCapacity: trip.busCapacity
      }
    });

  } catch (error) {
    next(error);
  }
};

module.exports = {
  getAllTrips,
  getTripById,
  createTrip,
  updateTrip,
  deleteTrip,
  searchTrips,
  updateSeats
};