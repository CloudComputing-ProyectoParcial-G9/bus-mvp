const logger = require('../config/logger');

const errorHandler = (err, req, res, next) => {
  // Log del error
  logger.error('Error occurred:', {
    error: err.message,
    stack: err.stack,
    method: req.method,
    url: req.url,
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });

  // Error de validación de Sequelize
  if (err.name === 'SequelizeValidationError') {
    const errors = err.errors.map(error => ({
      field: error.path,
      message: error.message,
      value: error.value
    }));
    
    return res.status(400).json({
      error: 'Validation Error',
      message: 'One or more fields have invalid values',
      code: 'VALIDATION_ERROR',
      details: errors
    });
  }

  // Error de constraint único de Sequelize
  if (err.name === 'SequelizeUniqueConstraintError') {
    return res.status(409).json({
      error: 'Conflict',
      message: 'Resource already exists',
      code: 'UNIQUE_CONSTRAINT_ERROR',
      details: {
        field: err.errors[0]?.path,
        value: err.errors[0]?.value
      }
    });
  }

  // Error de foreign key de Sequelize
  if (err.name === 'SequelizeForeignKeyConstraintError') {
    return res.status(400).json({
      error: 'Foreign Key Error',
      message: 'Referenced resource does not exist',
      code: 'FOREIGN_KEY_ERROR',
      details: {
        field: err.fields,
        table: err.table
      }
    });
  }

  // Error de conexión a base de datos
  if (err.name === 'SequelizeConnectionError') {
    return res.status(503).json({
      error: 'Service Unavailable',
      message: 'Database connection error',
      code: 'DATABASE_CONNECTION_ERROR'
    });
  }

  // Error de sintaxis JSON
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return res.status(400).json({
      error: 'Bad Request',
      message: 'Invalid JSON in request body',
      code: 'INVALID_JSON'
    });
  }

  // Error de validación customizado
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      error: 'Validation Error',
      message: err.message,
      code: 'CUSTOM_VALIDATION_ERROR',
      details: err.details || {}
    });
  }

  // Error de recurso no encontrado
  if (err.name === 'NotFoundError') {
    return res.status(404).json({
      error: 'Not Found',
      message: err.message,
      code: 'RESOURCE_NOT_FOUND'
    });
  }

  // Error de autorización
  if (err.name === 'UnauthorizedError') {
    return res.status(401).json({
      error: 'Unauthorized',
      message: err.message || 'Authentication required',
      code: 'UNAUTHORIZED'
    });
  }

  // Error de permisos
  if (err.name === 'ForbiddenError') {
    return res.status(403).json({
      error: 'Forbidden',
      message: err.message || 'Insufficient permissions',
      code: 'FORBIDDEN'
    });
  }

  // Error de rate limiting
  if (err.status === 429) {
    return res.status(429).json({
      error: 'Too Many Requests',
      message: 'Rate limit exceeded',
      code: 'RATE_LIMIT_EXCEEDED'
    });
  }

  // Error genérico del servidor
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'production' 
      ? 'An unexpected error occurred' 
      : err.message,
    code: 'INTERNAL_SERVER_ERROR',
    ...(process.env.NODE_ENV !== 'production' && { stack: err.stack })
  });
};

module.exports = errorHandler;
