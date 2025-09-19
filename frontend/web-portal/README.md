# Web Portal - Frontend SPA

## Descripción
Aplicación SPA (Single Page Application) que consume los 5 microservicios del sistema Bus MVP.

> **TODO (@F)**: Elegir framework frontend específico y completar implementación.

## Requisitos del Proyecto
- ✅ **Debe consumir los 5 microservicios**
- ✅ **Interfaz responsive para gestión de boletos de autobús**
- ✅ **Dockerizado para despliegue**
- ✅ **Integración con Load Balancer**

## Opciones de Tecnología

### Framework Recomendados
```bash
# Opción 1: React + Vite (Rápido desarrollo)
npm create react-app web-portal
cd web-portal
npm install axios react-router-dom

# Opción 2: Vue.js + Vite (Curva de aprendizaje suave)
npm create vue@latest web-portal
cd web-portal
npm install axios vue-router

# Opción 3: Angular (Robusto para aplicaciones grandes)
npx @angular/cli new web-portal
cd web-portal
npm install

# Opción 4: Next.js (Full-stack React)
npx create-next-app@latest web-portal
cd web-portal
npm install axios

# Opción 5: Svelte + SvelteKit (Ligero y moderno)
npm create svelte@latest web-portal
cd web-portal
npm install
```

## Estructura Base (Framework Agnóstico)

```
frontend/web-portal/
├── public/                    # Archivos estáticos
│   ├── index.html
│   ├── favicon.ico
│   └── assets/
│       ├── images/
│       └── icons/
├── src/                       # Código fuente
│   ├── components/           # Componentes reutilizables
│   │   ├── common/          # Componentes comunes
│   │   ├── passengers/      # Componentes de pasajeros
│   │   ├── trips/          # Componentes de viajes
│   │   ├── tickets/        # Componentes de boletos
│   │   ├── history/        # Componentes de historial
│   │   └── analytics/      # Componentes analíticos
│   ├── services/           # Servicios API
│   │   ├── api.js          # Cliente HTTP base
│   │   ├── passengers.js   # API pasajeros
│   │   ├── trips.js        # API viajes
│   │   ├── tickets.js      # API boletos
│   │   ├── history.js      # API historial
│   │   └── analytics.js    # API analytics
│   ├── views/              # Vistas/páginas principales
│   │   ├── Home.js/vue/tsx
│   │   ├── Search.js/vue/tsx
│   │   ├── Booking.js/vue/tsx
│   │   ├── Profile.js/vue/tsx
│   │   └── Dashboard.js/vue/tsx
│   ├── router/             # Configuración de rutas
│   ├── store/              # Estado global (Redux/Vuex/etc)
│   ├── utils/              # Utilidades
│   ├── styles/             # Estilos CSS/SCSS
│   └── main.js             # Punto de entrada
├── Dockerfile              # Imagen para producción
├── package.json            # Dependencias del proyecto
├── .env.example           # Variables de entorno
└── README.md              # Este archivo
```

## Funcionalidades Principales

### 1. Gestión de Pasajeros (ms-passengers)
- Registro de nuevos pasajeros
- Edición de perfil
- Consulta de información personal
- Historial de viajes

### 2. Búsqueda de Viajes (ms-trips)
- Buscador de rutas disponibles
- Filtros por fecha, horario, precio
- Visualización de asientos disponibles
- Información detallada de viajes

### 3. Compra de Boletos (ms-tickets)
- Selección de asientos
- Proceso de compra
- Generación de boletos digitales
- Cancelación de boletos

### 4. Historial Completo (ms-history)
- Vista unificada de todas las actividades
- Historial de compras y cancelaciones
- Reportes personalizados
- Exportación de datos

### 5. Dashboard Analítico (ms-analytics)
- Métricas de uso del sistema
- Reportes de ingresos
- Análisis de rutas populares
- Visualizaciones gráficas

## Variables de Entorno

```bash
# URL base del Load Balancer
VITE_API_BASE_URL=http://localhost:8080

# URLs específicas de microservicios (para desarrollo)
VITE_MS_PASSENGERS_URL=http://localhost:8001
VITE_MS_TRIPS_URL=http://localhost:8002
VITE_MS_TICKETS_URL=http://localhost:8003
VITE_MS_HISTORY_URL=http://localhost:8004
VITE_MS_ANALYTICS_URL=http://localhost:8005

# Configuración de la aplicación
VITE_APP_NAME="Bus MVP Portal"
VITE_APP_VERSION="1.0.0"
VITE_ENVIRONMENT=development

# Configuración de autenticación (opcional)
VITE_JWT_SECRET=your_jwt_secret_here
VITE_SESSION_TIMEOUT=3600000

# Configuración de logs
VITE_LOG_LEVEL=info
VITE_ENABLE_ANALYTICS=true
```

## Casos de Uso Principales

### UC-01: Búsqueda y Reserva de Viaje
1. Usuario busca viajes disponibles (ms-trips)
2. Selecciona viaje y asientos disponibles
3. Registra/autentica información personal (ms-passengers)
4. Procesa compra de boleto (ms-tickets)
5. Confirma reserva y genera boleto digital

### UC-02: Consulta de Historial
1. Usuario se autentica en el sistema
2. Consulta historial completo (ms-history)
3. Filtra por fechas, tipos de transacción
4. Exporta o imprime información

### UC-03: Cancelación de Boleto
1. Usuario busca boleto en historial
2. Solicita cancelación (ms-tickets)
3. Sistema valida política de cancelación
4. Procesa reembolso y actualiza estado

### UC-04: Dashboard Operacional
1. Administrador accede a analytics (ms-analytics)
2. Consulta métricas en tiempo real
3. Genera reportes específicos
4. Exporta datos para análisis externo

## Integración con Microservicios

### Cliente HTTP Base
```javascript
// src/services/api.js
const API_BASE = process.env.VITE_API_BASE_URL || 'http://localhost:8080';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE;
    this.timeout = 10000;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Métodos específicos
  get(endpoint, headers = {}) {
    return this.request(endpoint, { method: 'GET', headers });
  }

  post(endpoint, data, headers = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      headers
    });
  }

  put(endpoint, data, headers = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
      headers
    });
  }

  delete(endpoint, headers = {}) {
    return this.request(endpoint, { method: 'DELETE', headers });
  }
}

export default new ApiClient();
```

## Comandos de Desarrollo

```bash
# Instalación de dependencias
npm install

# Desarrollo local
npm run dev

# Build para producción
npm run build

# Previsualización de build
npm run preview

# Linting y formateo
npm run lint
npm run format

# Testing
npm run test
npm run test:coverage

# Docker
docker build -t bus-mvp-frontend .
docker run -p 3000:3000 bus-mvp-frontend
```

## Arquitectura Frontend

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
│                   (nginx:8080)                          │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                  Frontend SPA                          │
│                (React/Vue/Angular)                      │
└─┬─────┬─────┬─────┬─────┬─────────────────────────────────┘
  │     │     │     │     │
  │     │     │     │     └─> ms-analytics:8005
  │     │     │     └────────> ms-history:8004
  │     │     └─────────────> ms-tickets:8003
  │     └───────────────────> ms-trips:8002
  └─────────────────────────> ms-passengers:8001
```

## Consideraciones de Diseño

### Responsive Design
- Mobile-first approach
- Breakpoints: 320px, 768px, 1024px, 1440px
- Componentes adaptables a diferentes pantallas
- Touch-friendly para dispositivos móviles

### Accesibilidad (a11y)
- Cumplimiento con WCAG 2.1 AA
- Navegación por teclado
- Screen reader compatible
- Alto contraste y legibilidad

### Performance
- Code splitting por rutas
- Lazy loading de componentes
- Optimización de imágenes
- Service Worker para cache offline

### Seguridad
- Validación de entrada en cliente y servidor
- Sanitización de datos
- HTTPS en producción
- Gestión segura de tokens JWT

## Próximos Pasos

1. **Elegir Framework** (@F): Decidir entre React, Vue, Angular u otro
2. **Configurar Proyecto** (@F): Inicializar con el framework elegido
3. **Implementar API Client** (@F): Crear servicios de integración
4. **Diseñar UI/UX** (@F): Crear mockups y componentes base
5. **Integrar con Backend** (@F): Conectar con los 5 microservicios
6. **Dockerizar** (@F): Crear Dockerfile y configuración
7. **Testing** (@F): Implementar pruebas unitarias e integración

## Enlaces Útiles
- [Documentación API](../backend/): OpenAPI specs de todos los microservicios
- [Docker Compose](../infra/docker-compose.yml): Configuración completa del sistema
- [Load Balancer](../infra/lb/default.conf): Configuración de nginx
