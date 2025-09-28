const express = require('express');
const router = express.Router();
const {
  getAllTrips,
  getTripById,
  createTrip,
  updateTrip,
  deleteTrip,
  searchTrips,
  updateSeats
} = require('../controllers/tripController');

// Middleware de validación (se puede agregar después)
// const { tripValidation } = require('../middleware/validation');

/**
 * @swagger
 * tags:
 *   name: Trips
 *   description: API para gestión de viajes
 */

/**
 * @swagger
 * /api/v1/trips:
 *   get:
 *     tags: [Trips]
 *     summary: Obtener todos los viajes
 *     parameters:
 *       - in: query
 *         name: routeId
 *         schema:
 *           type: string
 *         description: Filtrar por ID de ruta
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *         description: Filtrar por estado del viaje
 *       - in: query
 *         name: departureDate
 *         schema:
 *           type: string
 *           format: date
 *         description: Filtrar por fecha de salida
 *     responses:
 *       200:
 *         description: Lista de viajes obtenida exitosamente
 */
router.get('/', getAllTrips);

/**
 * @swagger
 * /api/v1/trips/search:
 *   get:
 *     tags: [Trips]
 *     summary: Buscar viajes
 *     parameters:
 *       - in: query
 *         name: origin
 *         required: true
 *         schema:
 *           type: string
 *         description: Ciudad de origen
 *       - in: query
 *         name: destination
 *         required: true
 *         schema:
 *           type: string
 *         description: Ciudad de destino
 *       - in: query
 *         name: departureDate
 *         required: true
 *         schema:
 *           type: string
 *           format: date
 *         description: Fecha de salida
 *     responses:
 *       200:
 *         description: Viajes encontrados exitosamente
 */
router.get('/search', searchTrips);

/**
 * @swagger
 * /api/v1/trips/{tripId}:
 *   get:
 *     tags: [Trips]
 *     summary: Obtener un viaje por ID
 *     parameters:
 *       - in: path
 *         name: tripId
 *         required: true
 *         schema:
 *           type: string
 *         description: ID del viaje
 *     responses:
 *       200:
 *         description: Viaje obtenido exitosamente
 *       404:
 *         description: Viaje no encontrado
 */
router.get('/:tripId', getTripById);

/**
 * @swagger
 * /api/v1/trips:
 *   post:
 *     tags: [Trips]
 *     summary: Crear un nuevo viaje
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               tripId:
 *                 type: string
 *               routeId:
 *                 type: string
 *               departureDateTime:
 *                 type: string
 *                 format: date-time
 *               arrivalDateTime:
 *                 type: string
 *                 format: date-time
 *               busCapacity:
 *                 type: integer
 *               finalPrice:
 *                 type: number
 *     responses:
 *       201:
 *         description: Viaje creado exitosamente
 */
router.post('/', createTrip);

/**
 * @swagger
 * /api/v1/trips/{tripId}:
 *   put:
 *     tags: [Trips]
 *     summary: Actualizar un viaje
 *     parameters:
 *       - in: path
 *         name: tripId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Viaje actualizado exitosamente
 */
router.put('/:tripId', updateTrip);

/**
 * @swagger
 * /api/v1/trips/{tripId}:
 *   delete:
 *     tags: [Trips]
 *     summary: Eliminar un viaje
 *     parameters:
 *       - in: path
 *         name: tripId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Viaje eliminado exitosamente
 */
router.delete('/:tripId', deleteTrip);

/**
 * @swagger
 * /api/v1/trips/{tripId}/seats:
 *   patch:
 *     tags: [Trips]
 *     summary: Reservar o liberar asientos
 *     parameters:
 *       - in: path
 *         name: tripId
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               seatsToReserve:
 *                 type: integer
 *               seatsToRelease:
 *                 type: integer
 *     responses:
 *       200:
 *         description: Asientos actualizados exitosamente
 */
router.patch('/:tripId/seats', updateSeats);

module.exports = router;
