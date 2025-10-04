const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Bus MVP - Trips Service API',
      version: process.env.PROJECT_VERSION || '1.0.0',
      description: 'API para gestión de rutas y viajes del sistema Bus MVP',
      contact: {
        name: 'Bus MVP Team',
        email: 'dev@busmvp.com'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      }
    },
    servers: [
      {
        url: `http://localhost:${process.env.PORT || 8002}`,
        description: 'Servidor de desarrollo'
      },
      {
        url: 'http://localhost:8080',
        description: 'Load Balancer'
      }
    ],
    tags: [
      {
        name: 'Health',
        description: 'Health check endpoints para monitoreo del servicio'
      },
      {
        name: 'Routes',
        description: 'Gestión de rutas de autobús entre ciudades peruanas'
      },
      {
        name: 'Trips',
        description: 'Gestión de viajes programados y reserva de asientos'
      },
      {
        name: 'Admin',
        description: 'Endpoints administrativos para seeding y gestión de datos (solo desarrollo)'
      }
    ],
    components: {
      schemas: {
        Route: {
          type: 'object',
          required: ['routeId', 'routeName', 'originCity', 'destinationCity', 'distanceKm', 'estimatedDuration', 'basePrice'],
          properties: {
            routeId: {
              type: 'string',
              description: 'Identificador único de la ruta (formato: ORG_DST_NNN)',
              example: 'LIM_CUZ_001'
            },
            routeName: {
              type: 'string',
              description: 'Nombre descriptivo de la ruta',
              example: 'Lima - Cusco Express'
            },
            originCity: {
              type: 'string',
              description: 'Ciudad de origen',
              example: 'Lima'
            },
            destinationCity: {
              type: 'string',
              description: 'Ciudad de destino',
              example: 'Cusco'
            },
            distanceKm: {
              type: 'number',
              format: 'decimal',
              description: 'Distancia en kilómetros',
              example: 1165.50
            },
            estimatedDuration: {
              type: 'string',
              format: 'time',
              description: 'Duración estimada del viaje (HH:MM:SS)',
              example: '20:00:00'
            },
            basePrice: {
              type: 'number',
              format: 'decimal',
              description: 'Precio base de la ruta en soles peruanos',
              example: 120.00
            },
            currency: {
              type: 'string',
              description: 'Código de moneda (PEN = Sol Peruano)',
              example: 'PEN',
              enum: ['PEN', 'USD', 'EUR']
            },
            active: {
              type: 'boolean',
              description: 'Estado activo de la ruta',
              example: true
            },
            createdAt: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha de creación'
            },
            updatedAt: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha de última actualización'
            }
          }
        },
        Trip: {
          type: 'object',
          required: ['tripId', 'routeId', 'departureDateTime', 'arrivalDateTime', 'busCapacity', 'availableSeats', 'finalPrice'],
          properties: {
            tripId: {
              type: 'string',
              description: 'Identificador único del viaje (formato: TRP_YYYYMMDD_ORG_DST_NN)',
              example: 'TRP_20250921_LIM_CUZ_01'
            },
            routeId: {
              type: 'string',
              description: 'ID de la ruta asociada',
              example: 'LIM_CUZ_001'
            },
            departureDateTime: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha y hora de salida',
              example: '2025-09-21T22:00:00.000Z'
            },
            arrivalDateTime: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha y hora de llegada',
              example: '2025-09-22T18:00:00.000Z'
            },
            busCapacity: {
              type: 'integer',
              description: 'Capacidad total del autobús',
              example: 45,
              minimum: 1,
              maximum: 100
            },
            availableSeats: {
              type: 'integer',
              description: 'Asientos disponibles',
              example: 40,
              minimum: 0
            },
            finalPrice: {
              type: 'number',
              format: 'decimal',
              description: 'Precio final del viaje en soles peruanos',
              example: 120.00
            },
            status: {
              type: 'string',
              enum: ['scheduled', 'in_progress', 'completed', 'cancelled'],
              description: 'Estado del viaje',
              example: 'scheduled'
            },
            driverName: {
              type: 'string',
              description: 'Nombre del conductor',
              example: 'Carlos Mendoza'
            },
            busPlate: {
              type: 'string',
              description: 'Placa del autobús',
              example: 'ABC-123',
              nullable: true
            },
            createdAt: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha de creación'
            },
            updatedAt: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha de última actualización'
            }
          }
        },
        DataStatus: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              example: 'Database status retrieved successfully'
            },
            summary: {
              type: 'object',
              properties: {
                totalRoutes: {
                  type: 'integer',
                  example: 6
                },
                totalTrips: {
                  type: 'integer',
                  example: 5
                },
                activeRoutes: {
                  type: 'integer',
                  example: 6
                },
                scheduledTrips: {
                  type: 'integer',
                  example: 5
                }
              }
            },
            routes: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  routeId: {
                    type: 'string',
                    example: 'LIM_CUZ_001'
                  },
                  routeName: {
                    type: 'string',
                    example: 'Lima - Cusco Express'
                  },
                  route: {
                    type: 'string',
                    example: 'Lima → Cusco'
                  },
                  tripCount: {
                    type: 'integer',
                    example: 1
                  },
                  scheduledTrips: {
                    type: 'integer',
                    example: 1
                  }
                }
              }
            },
            timestamp: {
              type: 'string',
              format: 'date-time'
            }
          }
        },
        SeederResult: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              example: 'Data seeder executed successfully'
            },
            summary: {
              type: 'object',
              properties: {
                routes: {
                  type: 'integer',
                  example: 6
                },
                trips: {
                  type: 'integer',
                  example: 5
                },
                activeRoutes: {
                  type: 'integer',
                  example: 6
                },
                scheduledTrips: {
                  type: 'integer',
                  example: 5
                },
                executionTime: {
                  type: 'string',
                  example: '2.45s'
                }
              }
            },
            options: {
              type: 'object',
              properties: {
                clearData: {
                  type: 'boolean',
                  example: true
                },
                testData: {
                  type: 'boolean',
                  example: true
                }
              }
            },
            timestamp: {
              type: 'string',
              format: 'date-time'
            }
          }
        },
        Error: {
          type: 'object',
          properties: {
            error: {
              type: 'string',
              description: 'Tipo de error'
            },
            message: {
              type: 'string',
              description: 'Mensaje descriptivo del error'
            },
            code: {
              type: 'string',
              description: 'Código interno del error'
            },
            details: {
              type: 'object',
              description: 'Detalles adicionales del error'
            }
          }
        }
      },
      responses: {
        NotFound: {
          description: 'Recurso no encontrado',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              }
            }
          }
        },
        ValidationError: {
          description: 'Error de validación',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              }
            }
          }
        },
        ServerError: {
          description: 'Error interno del servidor',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              }
            }
          }
        }
      }
    }
  },
  apis: ['./src/routes/*.js', './src/controllers/*.js'], // Rutas donde buscar documentación
};

const specs = swaggerJsdoc(options);

function setupSwagger(app) {
  app.use('/docs', swaggerUi.serve, swaggerUi.setup(specs, {
    explorer: true,
    customCssUrl: 'https://cdn.jsdelivr.net/npm/swagger-ui-themes@3.0.1/themes/3.x/theme-material.css'
  }));
  
  // Endpoint para obtener la spec en JSON
  app.get('/api-docs', (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.send(specs);
  });
}

module.exports = setupSwagger;
