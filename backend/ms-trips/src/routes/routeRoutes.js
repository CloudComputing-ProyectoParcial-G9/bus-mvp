const express = require('express');
const router = express.Router();
const routeController = require('../controllers/routeController');
const { routeValidation } = require('../middleware/validation');

// GET /api/v1/routes - Listar todas las rutas
router.get('/', routeController.getAllRoutes);

// GET /api/v1/routes/:routeId - Obtener ruta específica
router.get('/:routeId', routeValidation.getById, routeController.getRouteById);

// POST /api/v1/routes - Crear nueva ruta
router.post('/', routeValidation.create, routeController.createRoute);

// PUT /api/v1/routes/:routeId - Actualizar ruta
router.put('/:routeId', routeValidation.update, routeController.updateRoute);

// DELETE /api/v1/routes/:routeId - Eliminar ruta
router.delete('/:routeId', routeValidation.getById, routeController.deleteRoute);

module.exports = router;
