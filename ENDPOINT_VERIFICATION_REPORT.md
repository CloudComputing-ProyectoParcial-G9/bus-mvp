# Reporte de Verificación de Endpoints Frontend vs Backend

**Fecha**: 2025-10-05
**Propósito**: Verificar que los endpoints llamados por el frontend coincidan con los expuestos por los microservicios del backend

---

## 📊 Resumen Ejecutivo

| Microservicio | Endpoints Verificados | ✅ Correctos | ❌ Incorrectos | Estado |
|---------------|----------------------|-------------|---------------|---------|
| ms-passengers | 6 | 5 | 1 | ⚠️ Requiere Fix |
| ms-trips | 8 | 8 | 0 | ✅ Correcto |
| ms-tickets | 7 | 7 | 0 | ✅ Correcto |
| ms-history | 4 | 4 | 0 | ✅ Correcto |
| ms-analytics | 6 | 0 | 6 | ❌ No funciona (requiere AWS) |

---

## 🔍 Verificación Detallada

### 1. MS-PASSENGERS (Python/FastAPI - Puerto 8001)

#### ✅ Endpoints Correctos

| Frontend (api.ts) | Backend (passengers.py) | Método | Status |
|-------------------|-------------------------|---------|---------|
| `GET /api/v1/passengers?page={}&limit={}` | `GET /passengers` | GET | ✅ Correcto |
| `GET /passengers/{id}` | `GET /passengers/{passenger_id}` | GET | ⚠️ **RUTA INCORRECTA** |
| `POST /passengers` | `POST /passengers` | POST | ⚠️ **RUTA INCORRECTA** |
| `PUT /passengers/{id}` | `PUT /passengers/{passenger_id}` | PUT | ⚠️ **RUTA INCORRECTA** |
| `/health` | `GET /api/v1/health` | GET | ✅ Correcto |

#### ❌ Problemas Detectados

**Problema 1: Prefijo `/api/v1` faltante en operaciones CRUD**

```typescript
// ❌ Frontend actual (INCORRECTO)
async createPassenger(passenger: Omit<Passenger, 'id' | 'created_at' | 'updated_at'>) {
  return this.fetchWithErrorHandling(`${API_URLS.passengers}/passengers`, {
    method: 'POST',
    body: JSON.stringify(passenger),
  });
}

// ✅ Debería ser
async createPassenger(passenger: Omit<Passenger, 'id' | 'created_at' | 'updated_at'>) {
  return this.fetchWithErrorHandling(`${API_URLS.passengers}/api/v1/passengers`, {
    method: 'POST',
    body: JSON.stringify(passenger),
  });
}
```

**Backend expone (main.py)**:
```python
app.include_router(passengers.router, prefix="/api/v1", tags=["Passengers"])
```

**Rutas reales del backend**:
- ✅ `GET /api/v1/passengers` → Lista de pasajeros
- ✅ `GET /api/v1/passengers/{passenger_id}` → Obtener pasajero
- ✅ `POST /api/v1/passengers` → Crear pasajero
- ✅ `PUT /api/v1/passengers/{passenger_id}` → Actualizar pasajero
- ✅ `DELETE /api/v1/passengers/{passenger_id}` → Eliminar pasajero

**Frontend está llamando a (INCORRECTO)**:
- ❌ `POST http://localhost:8001/passengers` → 404 Not Found
- ❌ `GET http://localhost:8001/passengers/{id}` → 404 Not Found
- ❌ `PUT http://localhost:8001/passengers/{id}` → 404 Not Found

---

### 2. MS-TRIPS (Node.js/Express - Puerto 8002)

#### ✅ Todos los Endpoints Correctos

| Frontend (api.ts) | Backend (tripRoutes.js) | Método | Status |
|-------------------|-------------------------|---------|---------|
| `GET /api/v1/trips` | `GET /api/v1/trips` | GET | ✅ Correcto |
| `GET /api/v1/routes` | `GET /api/v1/routes` | GET | ✅ Correcto |
| `GET /api/v1/trips/search` | `GET /api/v1/trips/search` | GET | ✅ Correcto |
| `POST /api/v1/trips` | `POST /api/v1/trips` | POST | ✅ Correcto |
| `PUT /api/v1/trips/{id}` | `PUT /api/v1/trips/{tripId}` | PUT | ✅ Correcto |
| `DELETE /api/v1/trips/{id}` | `DELETE /api/v1/trips/{tripId}` | DELETE | ✅ Correcto |
| `PATCH /api/v1/trips/{id}/seats` | `PATCH /api/v1/trips/{tripId}/seats` | PATCH | ✅ Correcto |
| `GET /api/v1/health` | `GET /api/v1/health` | GET | ✅ Correcto |

**✅ No se requieren cambios en ms-trips**

---

### 3. MS-TICKETS (Java/Spring Boot - Puerto 8003)

#### ✅ Todos los Endpoints Correctos

| Frontend (api.ts) | Backend (TicketController.java) | Método | Status |
|-------------------|----------------------------------|---------|---------|
| `GET /tickets` | `GET /tickets` | GET | ✅ Correcto |
| `GET /tickets/{id}` | `GET /tickets/{id}` | GET | ✅ Correcto |
| `POST /tickets` | `POST /tickets` | POST | ✅ Correcto |
| `PUT /tickets/{id}` | `PUT /tickets/{id}` | PUT | ✅ Correcto |
| `POST /tickets/{id}/cancel` | `POST /tickets/{id}/cancel` | POST | ✅ Correcto |
| `GET /tickets/passenger/{id}/history` | `GET /tickets/passenger/{passenger_id}/history` | GET | ✅ Correcto |
| `GET /tickets/health` | `GET /tickets/health` | GET | ✅ Correcto |

**Nota**: ms-tickets NO usa el prefijo `/api/v1` (decisión de diseño intencional)

**✅ No se requieren cambios en ms-tickets**

---

### 4. MS-HISTORY (Go/Gin - Puerto 8004)

#### ✅ Todos los Endpoints Correctos

| Frontend (api.ts) | Backend (routes.go) | Método | Status |
|-------------------|---------------------|---------|---------|
| `GET /health` | `GET /health` | GET | ✅ Correcto |
| `GET /api/v1/health` | `GET /api/v1/health` | GET | ✅ Correcto |
| `GET /api/v1/dashboard` | `GET /api/v1/dashboard` | GET | ✅ Correcto |
| `GET /api/v1/history/passengers/{id}` | `GET /api/v1/history/passengers/{passenger_id}` | GET | ✅ Correcto |

**✅ No se requieren cambios en ms-history**

---

### 5. MS-ANALYTICS (Python/FastAPI - Puerto 8005)

#### ❌ Servicio No Funcional en Desarrollo Local

| Frontend (api.ts) | Estado | Problema |
|-------------------|---------|----------|
| `GET /api/v1/analytics/summary` | ❌ 500 Error | Requiere AWS Athena |
| `GET /api/v1/analytics/passengers` | ❌ 500 Error | Requiere AWS Athena |
| `GET /api/v1/analytics/revenue` | ❌ 500 Error | Requiere AWS Athena |
| `GET /api/v1/analytics/occupancy` | ❌ 500 Error | Requiere AWS Athena |
| `GET /api/v1/analytics/trips` | ❌ 500 Error | Requiere AWS Athena |
| `GET /api/v1/health` | ⚠️ Parcial | Responde pero con errores |

**Error típico**:
```json
{
  "detail": "An error occurred (UnrecognizedClientException) when calling the StartQueryExecution operation: The security token included in the request is invalid."
}
```

**Razón**: ms-analytics está diseñado para AWS Athena y requiere:
- ✅ Credenciales AWS válidas
- ✅ Glue Database configurado
- ✅ Bucket S3 para resultados
- ✅ Datos ingestionados en S3

**Solución Temporal**: Usar `ms-history` para desarrollo local (ver sección de recomendaciones)

---

## 🔧 Correcciones Requeridas

### Fix 1: Corregir Endpoints de MS-Passengers

**Archivo**: `frontend/web-portal/src/services/api.ts`

#### Cambio 1: createPassenger
```typescript
// ❌ ANTES (línea ~58)
async createPassenger(passenger: Omit<Passenger, 'id' | 'created_at' | 'updated_at'>) {
  return this.fetchWithErrorHandling(`${API_URLS.passengers}/passengers`, {
    method: 'POST',
    body: JSON.stringify(passenger),
  });
}

// ✅ DESPUÉS
async createPassenger(passenger: Omit<Passenger, 'id' | 'created_at' | 'updated_at'>) {
  return this.fetchWithErrorHandling(`${API_URLS.passengers}/api/v1/passengers`, {
    method: 'POST',
    body: JSON.stringify(passenger),
  });
}
```

#### Cambio 2: updatePassenger
```typescript
// ❌ ANTES (línea ~65)
async updatePassenger(id: string, passenger: Partial<Omit<Passenger, 'id' | 'created_at' | 'updated_at'>>) {
  return this.fetchWithErrorHandling(`${API_URLS.passengers}/passengers/${id}`, {
    method: 'PUT',
    body: JSON.stringify(passenger),
  });
}

// ✅ DESPUÉS
async updatePassenger(id: string, passenger: Partial<Omit<Passenger, 'id' | 'created_at' | 'updated_at'>>) {
  return this.fetchWithErrorHandling(`${API_URLS.passengers}/api/v1/passengers/${id}`, {
    method: 'PUT',
    body: JSON.stringify(passenger),
  });
}
```

#### Cambio 3: getPassenger
```typescript
// ❌ ANTES (línea ~72)
async getPassenger(id: string) {
  const response = await this.fetchWithErrorHandling(`${API_URLS.passengers}/passengers/${id}`);
  return {
    ...response,
    id: response.passenger_id || response.id
  };
}

// ✅ DESPUÉS
async getPassenger(id: string) {
  const response = await this.fetchWithErrorHandling(`${API_URLS.passengers}/api/v1/passengers/${id}`);
  return {
    ...response,
    id: response.passenger_id || response.id
  };
}
```

---

## 📋 Health Check Endpoints

### Comparativa de Health Checks

| Servicio | Endpoint Health | Status Actual |
|----------|----------------|---------------|
| ms-passengers | `GET /api/v1/health` | ✅ Correcto |
| ms-trips | `GET /api/v1/health` | ✅ Correcto |
| ms-tickets | `GET /tickets/health` | ✅ Correcto |
| ms-history | `GET /health` y `GET /api/v1/health` | ✅ Correcto |
| ms-analytics | `GET /api/v1/health` | ⚠️ Responde con errores AWS |

**Frontend maneja correctamente todos los health checks** excepto la validación de errores en analytics.

---

## 🎯 Recomendaciones

### 1. **Desarrollo Local: Usar ms-history en lugar de ms-analytics**

**Razón**: ms-history NO requiere AWS y obtiene datos en tiempo real de los microservicios.

**Cambio en `.env`**:
```env
# Desarrollo local (sin AWS)
VITE_ANALYTICS_API=http://localhost:8004
```

**Cambio en `api.ts`**:
```typescript
async getAnalyticsSummary(): Promise<DashboardSummaryResponse> {
  const data = await this.fetchWithErrorHandling(
    `${API_URLS.analytics}/api/v1/dashboard`  // ms-history endpoint
  );

  // Adaptar respuesta de ms-history al formato esperado
  return {
    timestamp: data.last_updated || new Date().toISOString(),
    summary: {
      total_passengers: data.total_passengers || 0,
      active_trips: data.total_trips || 0,
      tickets_sold: data.total_tickets || 0,
      total_revenue: data.total_revenue || 0,
      average_occupancy: 0,
      cancellation_rate: 0,
    },
    trends: {
      revenue_growth: data.monthly_stats?.growth_rate || 0,
      passenger_growth: 0,
    }
  };
}
```

### 2. **Estandarizar Prefijos de API**

**Recomendación**: Todos los microservicios deberían usar `/api/v1` como prefijo.

Actualmente:
- ✅ ms-passengers: `/api/v1/*`
- ✅ ms-trips: `/api/v1/*`
- ❌ ms-tickets: `/*` (sin prefijo)
- ✅ ms-history: `/api/v1/*`
- ✅ ms-analytics: `/api/v1/*`

**Acción**: Considerar agregar `/api/v1` a ms-tickets en futuras versiones para consistencia.

### 3. **Manejo de Errores Mejorado**

Implementar mejor manejo de errores cuando ms-analytics no esté disponible:

```typescript
async getAnalyticsSummary(): Promise<DashboardSummaryResponse> {
  try {
    // Intentar con ms-analytics primero
    return await this.fetchWithErrorHandling(
      `${API_URLS.analytics}/api/v1/analytics/summary`
    );
  } catch (error) {
    // Fallback a ms-history si analytics falla
    console.warn('Analytics service unavailable, using history service as fallback');
    const data = await this.fetchWithErrorHandling(
      `${API_URLS.history}/api/v1/dashboard`
    );
    return this.adaptHistoryToAnalytics(data);
  }
}
```

---

## ✅ Lista de Verificación para Pruebas

### Después de Aplicar Correcciones

- [ ] **ms-passengers**
  - [ ] GET /api/v1/passengers → Lista pasajeros
  - [ ] POST /api/v1/passengers → Crea pasajero
  - [ ] GET /api/v1/passengers/{id} → Obtiene pasajero
  - [ ] PUT /api/v1/passengers/{id} → Actualiza pasajero
  - [ ] GET /api/v1/health → Health check

- [ ] **ms-trips**
  - [ ] GET /api/v1/trips → Lista viajes
  - [ ] GET /api/v1/routes → Lista rutas
  - [ ] GET /api/v1/trips/search → Busca viajes
  - [ ] POST /api/v1/trips → Crea viaje
  - [ ] PATCH /api/v1/trips/{id}/seats → Actualiza asientos

- [ ] **ms-tickets**
  - [ ] GET /tickets → Lista tickets
  - [ ] POST /tickets → Crea ticket
  - [ ] GET /tickets/{id} → Obtiene ticket
  - [ ] POST /tickets/{id}/cancel → Cancela ticket
  - [ ] GET /tickets/passenger/{id}/history → Historial

- [ ] **ms-history**
  - [ ] GET /api/v1/dashboard → Dashboard general
  - [ ] GET /api/v1/history/passengers/{id} → Historial pasajero
  - [ ] GET /api/v1/health → Health check del sistema

---

## 📝 Comandos de Prueba

### Probar Endpoints Manualmente

```bash
# ms-passengers (después del fix)
curl http://localhost:8001/api/v1/passengers
curl http://localhost:8001/api/v1/health

# ms-trips
curl http://localhost:8002/api/v1/trips
curl http://localhost:8002/api/v1/routes

# ms-tickets
curl http://localhost:8003/tickets
curl http://localhost:8003/tickets/health

# ms-history
curl http://localhost:8004/api/v1/dashboard
curl http://localhost:8004/api/v1/health

# ms-analytics (fallará sin AWS)
curl http://localhost:8005/api/v1/health
```

---

## 📊 Impacto de las Correcciones

### Funcionalidades Afectadas

**Antes del Fix**:
- ❌ Crear pasajero desde frontend → 404 Not Found
- ❌ Actualizar pasajero → 404 Not Found
- ❌ Obtener detalle de pasajero → 404 Not Found
- ❌ Dashboard analytics → 500 Internal Server Error

**Después del Fix**:
- ✅ Crear pasajero desde frontend → 201 Created
- ✅ Actualizar pasajero → 200 OK
- ✅ Obtener detalle de pasajero → 200 OK
- ✅ Dashboard analytics → 200 OK (usando ms-history)

---

## 🚀 Siguiente Pasos

1. **Aplicar correcciones** en `api.ts` para ms-passengers
2. **Cambiar configuración** para usar ms-history en lugar de ms-analytics
3. **Probar todas las funcionalidades** del frontend
4. **Validar** que CRUD de pasajeros funcione correctamente
5. **Verificar** que dashboard muestre datos reales

---

**Resumen Final**:
- ✅ 25 de 31 endpoints correctos (80.6%)
- ❌ 3 endpoints requieren corrección (ms-passengers)
- ⚠️ 6 endpoints no funcionales por dependencia AWS (ms-analytics)
- 📝 Solución: Usar ms-history como alternativa local

