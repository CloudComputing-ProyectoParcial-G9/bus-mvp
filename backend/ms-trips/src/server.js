const app = require('./app');
const { sequelize } = require('./config/database');
const logger = require('./config/logger');

const PORT = process.env.PORT || 8002;

async function startServer() {
  try {
    // Conectar a la base de datos
    await sequelize.authenticate();
    logger.info('Database connection established successfully');

    // Sincronizar modelos (solo en desarrollo)
    if (process.env.NODE_ENV === 'development') {
      await sequelize.sync({ force: false }); // force: true recreará las tablas
      logger.info('Database synchronized');
    }

    // Iniciar servidor
    const server = app.listen(PORT, () => {
      logger.info(`🚀 ${process.env.PROJECT_NAME || 'ms-trips'} server is running on port ${PORT}`);
      logger.info(`📚 API Documentation: http://localhost:${PORT}/docs`);
      logger.info(`🏥 Health Check: http://localhost:${PORT}/health`);
      logger.info(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
    });

    // Manejo graceful shutdown
    const gracefulShutdown = async (signal) => {
      logger.info(`Received ${signal}. Starting graceful shutdown...`);
      
      server.close(async () => {
        logger.info('HTTP server closed');
        
        try {
          await sequelize.close();
          logger.info('Database connection closed');
          process.exit(0);
        } catch (error) {
          logger.error('Error during shutdown:', error);
          process.exit(1);
        }
      });
    };

    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));

  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Manejo de errores no capturados
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception thrown:', error);
  process.exit(1);
});

startServer();
