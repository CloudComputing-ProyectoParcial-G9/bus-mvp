const { body, param, query, validationResult } = require('express-validator');

// Middleware para manejar errores de validación
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    return res.status(400).json({
      error: 'Validation Error',
      message: 'Invalid input data',
      code: 'VALIDATION_ERROR',
      details: errors.array().map(error => ({
        field: error.path,
        message: error.msg,
        value: error.value,
        location: error.location
      }))
    });
  }
  
  next();
};

// Validaciones para Route
const routeValidation = {
  create: [
    body('routeId')
      .matches(/^[A-Z]{3}_[A-Z]{3}_\d{3}$/)
      .withMessage('Route ID must follow format: ABC_XYZ_123'),
    
    body('routeName')
      .isLength({ min: 5, max: 100 })
      .withMessage('Route name must be between 5 and 100 characters'),
    
    body('originCity')
      .isLength({ min: 2, max: 50 })
      .withMessage('Origin city must be between 2 and 50 characters'),
    
    body('destinationCity')
      .isLength({ min: 2, max: 50 })
      .withMessage('Destination city must be between 2 and 50 characters')
      .custom((value, { req }) => {
        if (value === req.body.originCity) {
          throw new Error('Origin and destination cities must be different');
        }
        return true;
      }),
    
    body('distanceKm')
      .isFloat({ min: 1.0, max: 9999.99 })
      .withMessage('Distance must be between 1.0 and 9999.99 km'),
    
    body('estimatedDuration')
      .matches(/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/)
      .withMessage('Estimated duration must be in HH:MM:SS format'),
    
    body('basePrice')
      .isFloat({ min: 0.01, max: 99999.99 })
      .withMessage('Base price must be between 0.01 and 99999.99'),
    
    body('currency')
      .optional()
      .isIn(['PEN', 'USD', 'EUR'])
      .withMessage('Currency must be a valid ISO code (PEN, USD, EUR)'),
    
    body('active')
      .optional()
      .isBoolean()
      .withMessage('Active must be a boolean value'),
    
    handleValidationErrors
  ],

  update: [
    param('routeId')
      .matches(/^[A-Z]{3}_[A-Z]{3}_\d{3}$/)
      .withMessage('Route ID must follow format: ABC_XYZ_123'),
    
    body('routeName')
      .optional()
      .isLength({ min: 5, max: 100 })
      .withMessage('Route name must be between 5 and 100 characters'),
    
    body('originCity')
      .optional()
      .isLength({ min: 2, max: 50 })
      .withMessage('Origin city must be between 2 and 50 characters'),
    
    body('destinationCity')
      .optional()
      .isLength({ min: 2, max: 50 })
      .withMessage('Destination city must be between 2 and 50 characters'),
    
    body('distanceKm')
      .optional()
      .isFloat({ min: 1.0, max: 9999.99 })
      .withMessage('Distance must be between 1.0 and 9999.99 km'),
    
    body('estimatedDuration')
      .optional()
      .matches(/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/)
      .withMessage('Estimated duration must be in HH:MM:SS format'),
    
    body('basePrice')
      .optional()
      .isFloat({ min: 0.01, max: 99999.99 })
      .withMessage('Base price must be between 0.01 and 99999.99'),
    
    body('currency')
      .optional()
      .isIn(['PEN', 'USD', 'EUR'])
      .withMessage('Currency must be a valid ISO code (PEN, USD, EUR)'),
    
    body('active')
      .optional()
      .isBoolean()
      .withMessage('Active must be a boolean value'),
    
    handleValidationErrors
  ],

  getById: [
    param('routeId')
      .matches(/^[A-Z]{3}_[A-Z]{3}_\d{3}$/)
      .withMessage('Route ID must follow format: ABC_XYZ_123'),
    
    handleValidationErrors
  ]
};

// Validaciones para Trip
const tripValidation = {
  create: [
    body('tripId')
      .matches(/^TRP_\d{8}_[A-Z]{3}_[A-Z]{3}_\d{2}$/)
      .withMessage('Trip ID must follow format: TRP_YYYYMMDD_ABC_XYZ_HH'),
    
    body('routeId')
      .matches(/^[A-Z]{3}_[A-Z]{3}_\d{3}$/)
      .withMessage('Route ID must follow format: ABC_XYZ_123'),
    
    body('departureDateTime')
      .isISO8601()
      .withMessage('Departure date must be a valid ISO 8601 date')
      .custom((value) => {
        if (new Date(value) <= new Date()) {
          throw new Error('Departure date must be in the future');
        }
        return true;
      }),
    
    body('arrivalDateTime')
      .isISO8601()
      .withMessage('Arrival date must be a valid ISO 8601 date')
      .custom((value, { req }) => {
        if (new Date(value) <= new Date(req.body.departureDateTime)) {
          throw new Error('Arrival date must be after departure date');
        }
        return true;
      }),
    
    body('busCapacity')
      .isInt({ min: 1, max: 100 })
      .withMessage('Bus capacity must be between 1 and 100'),
    
    body('availableSeats')
      .isInt({ min: 0 })
      .withMessage('Available seats must be a positive integer')
      .custom((value, { req }) => {
        if (value > req.body.busCapacity) {
          throw new Error('Available seats cannot exceed bus capacity');
        }
        return true;
      }),
    
    body('finalPrice')
      .isFloat({ min: 0.01, max: 99999.99 })
      .withMessage('Final price must be between 0.01 and 99999.99'),
    
    body('status')
      .optional()
      .isIn(['scheduled', 'in_progress', 'completed', 'cancelled'])
      .withMessage('Status must be one of: scheduled, in_progress, completed, cancelled'),
    
    body('driverName')
      .optional()
      .isLength({ min: 2, max: 100 })
      .withMessage('Driver name must be between 2 and 100 characters'),
    
    body('busPlate')
      .optional()
      .isLength({ min: 6, max: 20 })
      .withMessage('Bus plate must be between 6 and 20 characters'),
    
    handleValidationErrors
  ],

  update: [
    param('tripId')
      .matches(/^TRP_\d{8}_[A-Z]{3}_[A-Z]{3}_\d{2}$/)
      .withMessage('Trip ID must follow format: TRP_YYYYMMDD_ABC_XYZ_HH'),
    
    body('availableSeats')
      .optional()
      .isInt({ min: 0 })
      .withMessage('Available seats must be a positive integer'),
    
    body('status')
      .optional()
      .isIn(['scheduled', 'in_progress', 'completed', 'cancelled'])
      .withMessage('Status must be one of: scheduled, in_progress, completed, cancelled'),
    
    body('driverName')
      .optional()
      .isLength({ min: 2, max: 100 })
      .withMessage('Driver name must be between 2 and 100 characters'),
    
    body('busPlate')
      .optional()
      .isLength({ min: 6, max: 20 })
      .withMessage('Bus plate must be between 6 and 20 characters'),
    
    handleValidationErrors
  ],

  updateSeats: [
    param('tripId')
      .matches(/^TRP_\d{8}_[A-Z]{3}_[A-Z]{3}_\d{2}$/)
      .withMessage('Trip ID must follow format: TRP_YYYYMMDD_ABC_XYZ_HH'),
    
    body('seatsToReserve')
      .optional()
      .isInt({ min: 1 })
      .withMessage('Seats to reserve must be a positive integer'),
    
    body('seatsToRelease')
      .optional()
      .isInt({ min: 1 })
      .withMessage('Seats to release must be a positive integer'),
    
    handleValidationErrors
  ],

  search: [
    query('origin')
      .optional()
      .isLength({ min: 2, max: 50 })
      .withMessage('Origin must be between 2 and 50 characters'),
    
    query('destination')
      .optional()
      .isLength({ min: 2, max: 50 })
      .withMessage('Destination must be between 2 and 50 characters'),
    
    query('date')
      .optional()
      .isISO8601()
      .withMessage('Date must be a valid ISO 8601 date'),
    
    query('minSeats')
      .optional()
      .isInt({ min: 1, max: 100 })
      .withMessage('Minimum seats must be between 1 and 100'),
    
    query('maxPrice')
      .optional()
      .isFloat({ min: 0.01 })
      .withMessage('Maximum price must be a positive number'),
    
    query('status')
      .optional()
      .isIn(['scheduled', 'in_progress', 'completed', 'cancelled'])
      .withMessage('Status must be one of: scheduled, in_progress, completed, cancelled'),
    
    query('page')
      .optional()
      .isInt({ min: 1 })
      .withMessage('Page must be a positive integer'),
    
    query('limit')
      .optional()
      .isInt({ min: 1, max: 100 })
      .withMessage('Limit must be between 1 and 100'),
    
    handleValidationErrors
  ],

  getById: [
    param('tripId')
      .matches(/^TRP_\d{8}_[A-Z]{3}_[A-Z]{3}_\d{2}$/)
      .withMessage('Trip ID must follow format: TRP_YYYYMMDD_ABC_XYZ_HH'),
    
    handleValidationErrors
  ]
};

module.exports = {
  routeValidation,
  tripValidation,
  handleValidationErrors
};
