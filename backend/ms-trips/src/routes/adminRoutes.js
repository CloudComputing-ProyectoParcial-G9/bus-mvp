const express = require('express');
const router = express.Router();
const {
  runSeeder,
  getDataStatus,
  clearAllData
} = require('../controllers/adminController');

/**
 * @swagger
 * /api/v1/admin/seed:
 *   post:
 *     tags: [Admin]
 *     summary: Ejecutar data seeder
 *     description: Poblar la base de datos con datos de prueba (solo en desarrollo)
 *     requestBody:
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               clearData:
 *                 type: boolean
 *                 default: true
 *                 description: Limpiar datos existentes antes de crear nuevos
 *               testData:
 *                 type: boolean
 *                 default: true
 *                 description: Verificar datos después de crearlos
 *     responses:
 *       200:
 *         description: Seeder ejecutado exitosamente
 *       403:
 *         description: No permitido en producción
 *       500:
 *         description: Error ejecutando seeder
 */
router.post('/seed', runSeeder);

/**
 * @swagger
 * /api/v1/admin/data-status:
 *   get:
 *     tags: [Admin]
 *     summary: Obtener estado de los datos
 *     description: Verificar cuántos datos existen en la base de datos
 *     responses:
 *       200:
 *         description: Estado de datos obtenido exitosamente
 *       500:
 *         description: Error obteniendo estado
 */
router.get('/data-status', getDataStatus);

/**
 * @swagger
 * /api/v1/admin/clear-data:
 *   delete:
 *     tags: [Admin]
 *     summary: Limpiar todos los datos
 *     description: Eliminar todos los datos de la base de datos (solo en desarrollo)
 *     responses:
 *       200:
 *         description: Datos eliminados exitosamente
 *       403:
 *         description: No permitido en producción
 *       500:
 *         description: Error eliminando datos
 */
router.delete('/clear-data', clearAllData);

module.exports = router;