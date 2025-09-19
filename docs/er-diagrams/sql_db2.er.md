# ER Diagram - Segunda Base de Datos SQL

## Descripción
Esta base de datos almacena información relacionada con **[definir dominio según microservicio asignado]**.

## Entidades y Relaciones

### Entidad 1: [NOMBRE_ENTIDAD_1]
**Propósito**: [Describir qué representa esta entidad]

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| id | INT/UUID | PRIMARY KEY, AUTO_INCREMENT/GENERATED | Identificador único |
| codigo | VARCHAR(50) | UNIQUE, NOT NULL | Código identificador |
| nombre | VARCHAR(200) | NOT NULL | Nombre descriptivo |
| descripcion | TEXT | | Descripción detallada |
| activo | BOOLEAN | DEFAULT TRUE | Estado activo/inactivo |
| fecha_inicio | DATE | NOT NULL | Fecha de inicio de vigencia |
| fecha_fin | DATE | | Fecha de fin de vigencia |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha de creación |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Fecha de última actualización |

### Entidad 2: [NOMBRE_ENTIDAD_2]
**Propósito**: [Describir qué representa esta entidad]

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| id | INT/UUID | PRIMARY KEY, AUTO_INCREMENT/GENERATED | Identificador único |
| entidad1_id | INT/UUID | FOREIGN KEY → entidad1(id) | Referencia a entidad1 |
| numero | VARCHAR(100) | UNIQUE, NOT NULL | Número identificador |
| cantidad | INT | CHECK (cantidad >= 0) | Cantidad numérica |
| precio | DECIMAL(12,2) | CHECK (precio >= 0) | Precio o costo |
| moneda | CHAR(3) | DEFAULT 'USD' | Código de moneda ISO |
| estado | ENUM('pendiente','procesado','cancelado') | DEFAULT 'pendiente' | Estado del proceso |
| fecha_proceso | TIMESTAMP | | Fecha de procesamiento |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha de creación |

### Entidad 3: [NOMBRE_ENTIDAD_3]
**Propósito**: [Describir qué representa esta entidad - tabla de auditoría o log]

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| id | INT/UUID | PRIMARY KEY, AUTO_INCREMENT/GENERATED | Identificador único |
| entidad2_id | INT/UUID | FOREIGN KEY → entidad2(id) | Referencia a entidad2 |
| accion | VARCHAR(50) | NOT NULL | Tipo de acción realizada |
| usuario_id | VARCHAR(100) | | Identificador del usuario |
| datos_anteriores | JSON/TEXT | | Estado anterior (para auditoría) |
| datos_nuevos | JSON/TEXT | | Estado nuevo (para auditoría) |
| ip_address | INET/VARCHAR(45) | | Dirección IP de origen |
| user_agent | TEXT | | Información del navegador/cliente |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha de la acción |

## Relaciones

### 1:N - Entidad1 → Entidad2
- **Descripción**: Una instancia de Entidad1 puede tener múltiples instancias de Entidad2
- **Cardinalidad**: 1:N
- **FK**: entidad2.entidad1_id → entidad1.id
- **Cascade**: ON DELETE RESTRICT, ON UPDATE CASCADE

### 1:N - Entidad2 → Entidad3
- **Descripción**: Una instancia de Entidad2 puede tener múltiples registros de auditoría
- **Cardinalidad**: 1:N
- **FK**: entidad3.entidad2_id → entidad2.id
- **Cascade**: ON DELETE CASCADE, ON UPDATE CASCADE

## Índices Recomendados

```sql
-- Índices para optimizar consultas frecuentes
CREATE INDEX idx_entidad1_codigo ON entidad1(codigo);
CREATE INDEX idx_entidad1_activo ON entidad1(activo);
CREATE INDEX idx_entidad1_fechas ON entidad1(fecha_inicio, fecha_fin);

CREATE INDEX idx_entidad2_entidad1_id ON entidad2(entidad1_id);
CREATE INDEX idx_entidad2_numero ON entidad2(numero);
CREATE INDEX idx_entidad2_estado ON entidad2(estado);
CREATE INDEX idx_entidad2_fecha_proceso ON entidad2(fecha_proceso);

CREATE INDEX idx_entidad3_entidad2_id ON entidad3(entidad2_id);
CREATE INDEX idx_entidad3_accion ON entidad3(accion);
CREATE INDEX idx_entidad3_created_at ON entidad3(created_at);
```

## Constrains Adicionales

```sql
-- Constrains de negocio
ALTER TABLE entidad1 ADD CONSTRAINT check_fechas_validas 
    CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio);

ALTER TABLE entidad2 ADD CONSTRAINT check_cantidad_positiva 
    CHECK (cantidad >= 0);

ALTER TABLE entidad2 ADD CONSTRAINT check_precio_positivo 
    CHECK (precio >= 0);

-- Constraint de unicidad compuesta
ALTER TABLE entidad2 ADD CONSTRAINT unique_entidad1_numero 
    UNIQUE (entidad1_id, numero);
```

## Triggers de Auditoría

```sql
-- Trigger para registrar cambios automáticamente
CREATE TRIGGER audit_entidad2_changes
    AFTER UPDATE ON entidad2
    FOR EACH ROW
    INSERT INTO entidad3 (entidad2_id, accion, datos_anteriores, datos_nuevos)
    VALUES (NEW.id, 'UPDATE', 
            JSON_OBJECT('estado', OLD.estado, 'cantidad', OLD.cantidad, 'precio', OLD.precio),
            JSON_OBJECT('estado', NEW.estado, 'cantidad', NEW.cantidad, 'precio', NEW.precio));
```

## Seeds de Ejemplo

```sql
-- Datos de ejemplo para desarrollo y testing
INSERT INTO entidad1 (codigo, nombre, descripcion, fecha_inicio) VALUES
    ('ENT001', 'Entidad Principal 1', 'Descripción de la primera entidad', '2024-01-01'),
    ('ENT002', 'Entidad Principal 2', 'Descripción de la segunda entidad', '2024-01-15'),
    ('ENT003', 'Entidad Principal 3', 'Descripción de la tercera entidad', '2024-02-01');

INSERT INTO entidad2 (entidad1_id, numero, cantidad, precio, moneda, estado) VALUES
    (1, 'NUM001', 10, 150.00, 'USD', 'procesado'),
    (1, 'NUM002', 5, 75.50, 'USD', 'pendiente'),
    (2, 'NUM003', 20, 300.00, 'EUR', 'procesado'),
    (3, 'NUM004', 8, 120.75, 'USD', 'cancelado');

INSERT INTO entidad3 (entidad2_id, accion, usuario_id, ip_address) VALUES
    (1, 'CREATE', 'user123', '192.168.1.100'),
    (1, 'UPDATE', 'user456', '192.168.1.101'),
    (2, 'CREATE', 'user789', '192.168.1.102');
```

## Vistas Útiles

```sql
-- Vista para consultas frecuentes con JOIN
CREATE VIEW vista_entidad_completa AS
SELECT 
    e1.codigo,
    e1.nombre,
    e1.activo,
    e2.numero,
    e2.cantidad,
    e2.precio,
    e2.moneda,
    e2.estado,
    e2.fecha_proceso
FROM entidad1 e1
LEFT JOIN entidad2 e2 ON e1.id = e2.entidad1_id
WHERE e1.activo = TRUE;

-- Vista de auditoría reciente
CREATE VIEW vista_auditoria_reciente AS
SELECT 
    e2.numero,
    e3.accion,
    e3.usuario_id,
    e3.created_at
FROM entidad3 e3
JOIN entidad2 e2 ON e3.entidad2_id = e2.id
WHERE e3.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY e3.created_at DESC;
```

## TODO - Para completar según stack elegido

- [ ] Definir motor de base de datos específico (MySQL, PostgreSQL, etc.)
- [ ] Ajustar tipos de datos JSON/INET según el motor elegido
- [ ] Implementar triggers de auditoría nativos del motor
- [ ] Configurar políticas de retención para tabla de auditoría
- [ ] Crear scripts de migración usando framework elegido
- [ ] Implementar validaciones a nivel de aplicación
- [ ] Configurar conexión desde el microservicio
- [ ] Definir estrategia de particionado para auditoría
- [ ] Configurar replicación si es necesario

## Notas de Implementación

- **Auditoría**: La tabla entidad3 puede crecer rápidamente, considerar particionado por fecha
- **Performance**: Evaluar índices adicionales según patrones de consulta en producción
- **Integridad**: Los foreign keys garantizan consistencia pero pueden impactar performance
- **Escalabilidad**: Considerar sharding horizontal si se requiere alta disponibilidad
- **Backup**: Configurar backup diferencial para tablas de auditoría
