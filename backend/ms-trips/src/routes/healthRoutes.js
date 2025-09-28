const express = require('express');
const router = express.Router();
const healthController = require('../controllers/healthController');

// Health check básico
router.get('/', healthController.healthCheck);

// Health check de base de datos
router.get('/db', healthController.healthCheckDb);

module.exports = router;
