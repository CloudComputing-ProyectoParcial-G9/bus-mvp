require('dotenv').config();
require('express-async-errors');

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');

// Importar configuraciones
const { sequelize } = require('./config/database');
const logger = require('./config/logger');
const swaggerSetup = require('./config/swagger');

// Importar rutas
const healthRoutes = require('./routes/healthRoutes');
const routeRoutes = require('./routes/routeRoutes');
const tripRoutes = require('./routes/tripRoutes');

// Importar middleware
const errorHandler = require('./middleware/errorHandler');

const app = express();

// Middleware de seguridad
app.use(helmet());
app.use(compression());

// CORS
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  methods: process.env.CORS_METHODS || 'GET,POST,PUT,PATCH,DELETE',
  allowedHeaders: process.env.CORS_ALLOWED_HEADERS || 'Content-Type,Authorization'
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 1 * 60 * 1000, // 1 minuto
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 500, // máximo 500 requests por minuto
  message: {
    error: 'Too many requests from this IP, please try again later.',
    code: 'RATE_LIMIT_EXCEEDED'
  },
  standardHeaders: true,
  legacyHeaders: false,
  // Excluir llamadas entre microservicios internos
  skip: (req) => {
    // No aplicar rate limit si viene de un microservicio interno
    const internalServices = ['ms-history', 'ms-passengers', 'ms-tickets', 'ms-analytics'];
    const userAgent = req.get('User-Agent') || '';
    const referer = req.get('Referer') || '';
    
    // Detectar si la llamada viene de Docker network interno
    const isInternalCall = req.headers['x-internal-call'] === 'true' ||
                          internalServices.some(service => userAgent.includes(service)) ||
                          req.ip.startsWith('172.') || // Docker network
                          req.ip === '::ffff:172.19.0.'; // IPv6 Docker
    
    return isInternalCall;
  }
});
app.use(limiter);

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Logging middleware
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`, {
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });
  next();
});

// Configurar Swagger si está habilitado
if (process.env.SWAGGER_ENABLED === 'true') {
  swaggerSetup(app);
}

// Rutas
app.use(`${process.env.API_V1_PREFIX || '/api/v1'}/health`, healthRoutes);
app.use(`${process.env.API_V1_PREFIX || '/api/v1'}/routes`, routeRoutes);
app.use(`${process.env.API_V1_PREFIX || '/api/v1'}/trips`, tripRoutes);
app.use(`${process.env.API_V1_PREFIX || '/api/v1'}/admin`, require('./routes/adminRoutes'));

// Ruta raíz
app.get('/', (req, res) => {
  res.json({
    message: `${process.env.PROJECT_NAME || 'ms-trips'} is running`,
    version: process.env.PROJECT_VERSION || '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString(),
    docs: process.env.SWAGGER_ENABLED === 'true' ? `${req.protocol}://${req.get('host')}/docs` : 'Swagger disabled'
  });
});

// Error handling middleware (debe ir al final)
app.use(errorHandler);

// Manejo de rutas no encontradas
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Route not found',
    message: `The requested route ${req.method} ${req.originalUrl} was not found on this server.`,
    code: 'ROUTE_NOT_FOUND'
  });
});

module.exports = app;
