# Guía del Dashboard - MS History

## 📊 Estructura del Dashboard

El endpoint `/api/v1/dashboard` proporciona un resumen ejecutivo con estadísticas agregadas de todos los microservicios.

### Campos Principales

#### 1. **total_passengers** (número)
- **Qué es**: Cantidad total de pasajeros registrados en el sistema
- **Origen**: ms-passengers (`/passengers`)
- **Para qué sirve**: Conocer el tamaño de la base de usuarios
- **Ejemplo**: `3` (hay 3 pasajeros registrados)

#### 2. **total_trips** (número)
- **Qué es**: Cantidad total de viajes programados
- **Origen**: ms-trips (`/trips`)
- **Para qué sirve**: Ver cuántos viajes están disponibles o se han programado
- **Ejemplo**: `7` (hay 7 viajes en el sistema)

#### 3. **total_tickets** (número)
- **Qué es**: Cantidad total de boletos vendidos/emitidos
- **Origen**: ms-tickets (`/tickets`)
- **Para qué sirve**: Medir volumen de ventas
- **Ejemplo**: `2` (se han vendido 2 tickets)

#### 4. **total_revenue** (número decimal)
- **Qué es**: Ingresos totales generados por venta de boletos
- **Origen**: ms-tickets (suma de `total_price` de todos los tickets)
- **Para qué sirve**: Ver cuánto dinero se ha generado
- **Ejemplo**: `150.50` (se han generado $150.50 en ventas)

#### 5. **active_routes** (número)
- **Qué es**: Cantidad de rutas activas disponibles
- **Origen**: ms-trips (`/routes` con status="active")
- **Para qué sirve**: Conocer cuántas rutas están operativas
- **Ejemplo**: `6` (hay 6 rutas activas)

#### 6. **popular_routes** (array)
- **Qué es**: Lista de rutas más populares ordenadas por número de tickets vendidos
- **Origen**: Agregación de ms-tickets + ms-trips
- **Para qué sirve**: Identificar qué rutas tienen más demanda
- **Estructura**:
  ```json
  [
    {
      "route_code": "LIM-ARQ",
      "origin_city": "Lima",
      "destination_city": "Arequipa",
      "total_tickets": 25,
      "total_revenue": 1250.00
    }
  ]
  ```

#### 7. **recent_activity** (array)
- **Qué es**: Actividad reciente del sistema (tickets comprados, viajes creados, etc.)
- **Origen**: Agregación de eventos recientes de todos los microservicios
- **Para qué sirve**: Ver qué está pasando en tiempo real en el sistema
- **Estructura**:
  ```json
  [
    {
      "type": "ticket_purchased",
      "description": "Juan Pérez compró ticket para Lima-Arequipa",
      "timestamp": "2025-10-04T10:30:00Z",
      "details": {
        "passenger_name": "Juan Pérez",
        "route": "LIM-ARQ",
        "amount": 50.00
      }
    }
  ]
  ```

#### 8. **monthly_stats** (objeto)
- **Qué es**: Estadísticas comparativas del mes actual vs mes anterior
- **Para qué sirve**: Ver tendencias y crecimiento del negocio
- **Estructura**:
  ```json
  {
    "current_month": {
      "month": "October 2025",
      "passengers": 15,
      "trips": 45,
      "tickets": 120,
      "revenue": 6000.00
    },
    "previous_month": {
      "month": "September 2025",
      "passengers": 12,
      "trips": 40,
      "tickets": 100,
      "revenue": 5000.00
    },
    "growth_rate": 20.0  // Crecimiento del 20%
  }
  ```

#### 9. **last_updated** (timestamp)
- **Qué es**: Fecha y hora de la última actualización del dashboard
- **Para qué sirve**: Saber qué tan recientes son los datos
- **Ejemplo**: `"2025-10-04T16:11:25.101759129Z"`

---

## 🔧 Problemas Actuales y Soluciones

### Problema 1: `total_passengers: 0` (SOLUCIONADO)
**Causa**: El método `GetPassengerStats` intentaba parsear un array como objeto  
**Solución**: Corregir para obtener la lista de pasajeros y contar correctamente

### Problema 2: `total_revenue: 0`
**Causa**: Los tickets en MongoDB tienen `total_price: 0`  
**Solución**: Necesitas actualizar los tickets con precios reales o calcularlos desde ms-trips

### Problema 3: `popular_routes: []` vacío
**Causa**: Funcionalidad no implementada (marcada como TODO)  
**Solución**: Implementar análisis de tickets agrupados por trip_id → route_id

### Problema 4: `recent_activity: []` vacío
**Causa**: Funcionalidad no implementada (marcada como TODO)  
**Solución**: Obtener últimos tickets/trips ordenados por fecha

### Problema 5: `monthly_stats` vacío
**Causa**: Funcionalidad no implementada (marcada como TODO)  
**Solución**: Filtrar datos por mes y comparar períodos

---

## 📝 Cómo Usar el Dashboard

### 1. Para Monitoreo General
```bash
curl http://localhost:8004/api/v1/dashboard
```

### 2. En el Frontend
```typescript
const response = await fetch('http://localhost:8004/api/v1/dashboard');
const dashboard = await response.json();

console.log(`Pasajeros: ${dashboard.total_passengers}`);
console.log(`Ingresos: $${dashboard.total_revenue}`);
```

### 3. Para Análisis de Negocio
- **KPI de Ventas**: `total_tickets` / `total_trips` = % de ocupación
- **Ingreso Promedio**: `total_revenue` / `total_tickets` = precio promedio
- **Tendencia**: `monthly_stats.growth_rate` = crecimiento mensual

---

## 🚀 Próximas Mejoras

1. **Implementar `popular_routes`**: TOP 5 rutas por ventas
2. **Implementar `recent_activity`**: Últimas 10 actividades
3. **Implementar `monthly_stats`**: Comparación mensual automática
4. **Agregar caché**: Redis para evitar consultas repetidas
5. **Agregar filtros**: Poder filtrar por fecha, ruta, etc.
6. **Agregar gráficos**: Endpoints específicos para datos de visualización
