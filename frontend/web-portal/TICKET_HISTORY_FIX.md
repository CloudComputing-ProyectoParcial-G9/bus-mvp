# Fix: Historial de Tickets No Se Mostraba Correctamente

**Fecha**: 2025-10-05
**Problema**: La tabla de historial de tickets mostraba "N/A" en todas las columnas a pesar de que el backend estaba retornando datos correctos.

---

## 🔍 Problema Detectado

### Síntoma
Al buscar el historial de un pasajero, la tabla mostraba:

| Ticket ID | Fecha | Estado | Precio |
|-----------|-------|--------|--------|
| N/A | N/A | N/A | $0 |
| N/A | N/A | N/A | $0 |
| N/A | N/A | N/A | $0 |

### Datos Reales del Backend
El backend (ms-history) estaba retornando correctamente:

```json
"recent_tickets": [
  {
    "ticket_id": "ticket_4b01fd33-127d-484d-b3e1-7c41e0c006b2",
    "passenger_id": "7a7d28e4-de02-4f50-b97a-52d7206d61a3",
    "trip_id": "TRP_20250927_LIM_CUS_02",
    "seat_number": "12A",
    "purchase_date": "0001-01-01T00:00:00Z",
    "total_price": 0,
    "currency": "EUR",
    "payment_method": "",
    "booking_status": "confirmed",
    "booking_reference": ""
  }
]
```

---

## 🐛 Causa Raíz

### Mapeo Incorrecto de Campos

El componente `HistorySection.tsx` estaba intentando acceder a campos que no existían en la respuesta del backend:

**Frontend (INCORRECTO)**:
```typescript
{ticket.id || 'N/A'}           // ❌ El backend envía: ticket_id
{ticket.date}                   // ❌ El backend envía: purchase_date
{ticket.status}                 // ❌ El backend envía: booking_status
{ticket.price}                  // ❌ El backend envía: total_price
```

**Backend (CORRECTO)**:
```json
{
  "ticket_id": "...",
  "purchase_date": "...",
  "booking_status": "confirmed",
  "total_price": 0
}
```

### Tabla de Mapeo Incorrecto

| Campo Frontend | Campo Backend | Estado |
|----------------|---------------|--------|
| `ticket.id` | `ticket.ticket_id` | ❌ No coincide |
| `ticket.date` | `ticket.purchase_date` | ❌ No coincide |
| `ticket.status` | `ticket.booking_status` | ❌ No coincide |
| `ticket.price` | `ticket.total_price` | ❌ No coincide |

---

## ✅ Solución Aplicada

### Cambio 1: Actualizar Nombres de Campos

**Archivo**: `frontend/web-portal/src/components/HistorySection.tsx`

```typescript
// ❌ ANTES
<tbody className="bg-white divide-y divide-gray-200">
  {passengerHistory.recent_tickets.map((ticket: any, index: number) => (
    <tr key={index}>
      <td>{ticket.id || 'N/A'}</td>
      <td>{ticket.date ? new Date(ticket.date).toLocaleString() : 'N/A'}</td>
      <td>{ticket.status || 'N/A'}</td>
      <td>${ticket.price || 0}</td>
    </tr>
  ))}
</tbody>

// ✅ DESPUÉS
<tbody className="bg-white divide-y divide-gray-200">
  {passengerHistory.recent_tickets.map((ticket: any, index: number) => (
    <tr key={index}>
      <td>{ticket.ticket_id ? ticket.ticket_id.substring(0, 20) + '...' : 'N/A'}</td>
      <td>{ticket.trip_id || 'N/A'}</td>
      <td>{ticket.seat_number || 'N/A'}</td>
      <td>
        {ticket.purchase_date && ticket.purchase_date !== '0001-01-01T00:00:00Z'
          ? new Date(ticket.purchase_date).toLocaleDateString()
          : 'N/A'}
      </td>
      <td>
        <span className={`badge ${ticket.booking_status === 'confirmed' ? 'green' : 'red'}`}>
          {ticket.booking_status || 'N/A'}
        </span>
      </td>
      <td>
        {ticket.total_price > 0
          ? `${ticket.currency || 'PEN'} ${ticket.total_price.toFixed(2)}`
          : 'N/A'}
      </td>
    </tr>
  ))}
</tbody>
```

### Cambio 2: Mejorar la Tabla con Más Información

Se agregaron columnas adicionales para mostrar más datos útiles:

**Columnas Anteriores**:
- Ticket ID
- Fecha
- Estado
- Precio

**Columnas Nuevas**:
- Ticket ID (truncado)
- **Viaje (trip_id)** ← NUEVO
- **Asiento (seat_number)** ← NUEVO
- Fecha Compra
- Estado (con colores)
- Precio (con moneda)

### Cambio 3: Manejo de Fechas Inválidas

El backend puede devolver fechas vacías como `"0001-01-01T00:00:00Z"`, por lo que se agregó validación:

```typescript
{ticket.purchase_date && ticket.purchase_date !== '0001-01-01T00:00:00Z'
  ? new Date(ticket.purchase_date).toLocaleDateString()
  : 'N/A'}
```

### Cambio 4: Estilos Dinámicos para Estado

```typescript
<span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
  ticket.booking_status === 'confirmed' ? 'bg-green-100 text-green-800' :
  ticket.booking_status === 'cancelled' ? 'bg-red-100 text-red-800' :
  'bg-blue-100 text-blue-800'
}`}>
  {ticket.booking_status || 'N/A'}
</span>
```

---

## 📊 Resultado Esperado

### Antes del Fix
```
┌──────────┬────────┬────────┬────────┐
│ Ticket   │ Fecha  │ Estado │ Precio │
├──────────┼────────┼────────┼────────┤
│ N/A      │ N/A    │ N/A    │ $0     │
│ N/A      │ N/A    │ N/A    │ $0     │
└──────────┴────────┴────────┴────────┘
```

### Después del Fix
```
┌───────────────────────┬─────────────────────────────┬─────────┬─────────┬───────────┬────────┐
│ Ticket ID             │ Viaje                       │ Asiento │ Fecha   │ Estado    │ Precio │
├───────────────────────┼─────────────────────────────┼─────────┼─────────┼───────────┼────────┤
│ ticket_4b01fd33-12... │ TRP_20250927_LIM_CUS_02     │ 12A     │ N/A     │ confirmed │ N/A    │
│ ticket_ac0b0027-15... │ TRP_20250927_ARE_CUS_01     │ 6A      │ N/A     │ confirmed │ N/A    │
│ ticket_40767624-31... │ TRP_20250928_TRU_CHI_19     │ 1B      │ N/A     │ confirmed │ N/A    │
│ ticket_9ea9782d-f8... │ TRP_20250921_LIM_TRU_03     │ 3C      │ N/A     │ confirmed │ N/A    │
└───────────────────────┴─────────────────────────────┴─────────┴─────────┴───────────┴────────┘
```

**Nota**: Los campos "Fecha" y "Precio" muestran "N/A" porque el backend actualmente retorna:
- `purchase_date: "0001-01-01T00:00:00Z"` (fecha inválida)
- `total_price: 0` (precio en 0)

Esto es un problema de **datos**, no del frontend. El componente ahora está listo para mostrar los datos cuando estén disponibles correctamente.

---

## 🔧 Problema Pendiente en el Backend

### ms-history No Está Obteniendo Datos Completos de ms-tickets

El servicio ms-history está consultando a ms-tickets pero no está recibiendo todos los campos necesarios:

**Campos faltantes**:
- ✅ `ticket_id` - Presente
- ✅ `trip_id` - Presente
- ✅ `seat_number` - Presente
- ✅ `booking_status` - Presente
- ❌ `purchase_date` - Retorna fecha vacía `"0001-01-01T00:00:00Z"`
- ❌ `total_price` - Retorna `0`
- ❌ `currency` - Retorna valor por defecto
- ❌ `payment_method` - Retorna vacío

**Posibles causas**:
1. Los tickets en la base de datos de ms-tickets no tienen estos campos completos
2. El servicio ms-history no está mapeando correctamente la respuesta de ms-tickets
3. Los datos de prueba (seed data) no incluyen estos campos

**Verificación recomendada**:

```bash
# Verificar datos en ms-tickets directamente
curl http://localhost:8003/tickets

# Verificar un ticket específico
curl http://localhost:8003/tickets/{ticket_id}
```

Si los datos existen en ms-tickets pero no llegan a ms-history, revisar:
- `backend/ms-history/src/services/aggregation_service.go`
- Método que consulta tickets de un pasajero
- Transformación de la respuesta de ms-tickets

---

## 🧪 Cómo Probar

### 1. Reiniciar el Frontend

```bash
cd frontend/web-portal
npm run dev
```

### 2. Navegar al Historial

1. Abrir: `http://localhost:5173` (o el puerto que muestre Vite)
2. Click en la pestaña "Historial"
3. Click en "Historial Pasajero"

### 3. Buscar un Pasajero

Usar un ID válido:
```
7a7d28e4-de02-4f50-b97a-52d7206d61a3
```

### 4. Verificar la Tabla

Ahora debería mostrar:
- ✅ Ticket ID (truncado)
- ✅ Viaje (trip_id completo)
- ✅ Asiento
- ⚠️ Fecha (N/A porque el dato está vacío)
- ✅ Estado (con badge verde/rojo)
- ⚠️ Precio (N/A porque está en 0)

---

## 📝 Comparación de Campos

### Estructura del Backend (ms-history response)

```typescript
interface RecentTicket {
  ticket_id: string;
  passenger_id: string;
  trip_id: string;
  seat_number: string;
  purchase_date: string;      // "0001-01-01T00:00:00Z" cuando está vacío
  total_price: number;        // 0 cuando no hay precio
  currency: string;           // "EUR", "PEN", etc.
  payment_method: string;
  booking_status: string;     // "confirmed", "cancelled"
  booking_reference: string;
}
```

### Mapeo Correcto Frontend ↔ Backend

| Columna UI | Campo Backend | Tipo | Observaciones |
|------------|---------------|------|---------------|
| Ticket ID | `ticket_id` | string | Se trunca para display |
| Viaje | `trip_id` | string | Código del viaje |
| Asiento | `seat_number` | string | Ej: "12A", "6B" |
| Fecha Compra | `purchase_date` | string (ISO) | Validar fecha != "0001-01-01" |
| Estado | `booking_status` | string | Aplicar colores según estado |
| Precio | `total_price` + `currency` | number + string | Mostrar con símbolo de moneda |

---

## 🎯 Siguiente Pasos

### Prioritario
1. ✅ **Corregir mapeo de campos en frontend** - COMPLETADO
2. ⏳ **Verificar datos en ms-tickets** - Pendiente
3. ⏳ **Revisar agregación en ms-history** - Pendiente

### Opcional (Mejoras Futuras)
- Agregar tooltip con ticket_id completo al hover
- Agregar filtros por estado de ticket
- Agregar ordenamiento por fecha/precio
- Agregar paginación si hay muchos tickets
- Mostrar más detalles del viaje (origen/destino)

---

## 📚 Archivos Modificados

- ✅ `frontend/web-portal/src/components/HistorySection.tsx`
  - Líneas 274-306: Tabla de tickets actualizada
  - Mapeo de campos corregido
  - Columnas adicionales agregadas
  - Validación de fechas mejorada
  - Estilos dinámicos para estado

---

## ✅ Checklist de Verificación

- [x] Campos mapeados correctamente (ticket_id, booking_status, etc.)
- [x] Validación de fechas vacías (`0001-01-01T00:00:00Z`)
- [x] Validación de precios en 0
- [x] Estilos de estado (confirmed = verde, cancelled = rojo)
- [x] Truncamiento de IDs largos
- [x] Columnas adicionales (viaje, asiento)
- [ ] Datos completos en ms-tickets (pendiente backend)
- [ ] Mapeo correcto en ms-history (pendiente backend)

---

**Resumen**: El frontend ahora está correctamente configurado para mostrar los datos. Los campos que muestran "N/A" se deben a que el backend está retornando valores vacíos o en 0, no a un problema del frontend.
