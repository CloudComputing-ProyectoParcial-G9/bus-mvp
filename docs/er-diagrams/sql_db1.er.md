# ER Diagram - Primera Base de Datos SQL

## Descripción
Esta base de datos almacena información relacionada con **[definir dominio según microservicio asignado]**.

## Entidades y Relaciones

### Entidad 1: [NOMBRE_ENTIDAD_1]
**Propósito**: [Describir qué representa esta entidad]

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| id | INT/UUID | PRIMARY KEY, AUTO_INCREMENT/GENERATED | Identificador único |
| campo1 | VARCHAR(100) | NOT NULL | [Descripción del campo] |
| campo2 | DATE | NOT NULL | [Descripción del campo] |
| campo3 | DECIMAL(10,2) | DEFAULT 0.00 | [Descripción del campo] |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha de creación |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Fecha de última actualización |

### Entidad 2: [NOMBRE_ENTIDAD_2]
**Propósito**: [Describir qué representa esta entidad]

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| id | INT/UUID | PRIMARY KEY, AUTO_INCREMENT/GENERATED | Identificador único |
| entidad1_id | INT/UUID | FOREIGN KEY → entidad1(id) | Referencia a entidad1 |
| campo1 | VARCHAR(255) | NOT NULL | [Descripción del campo] |
| campo2 | INT | CHECK (campo2 > 0) | [Descripción del campo] |
| estado | ENUM('activo','inactivo') | DEFAULT 'activo' | Estado del registro |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha de creación |

### Entidad 3: [NOMBRE_ENTIDAD_3] (Opcional)
**Propósito**: [Describir qué representa esta entidad]

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| id | INT/UUID | PRIMARY KEY, AUTO_INCREMENT/GENERATED | Identificador único |
| entidad1_id | INT/UUID | FOREIGN KEY → entidad1(id) | Referencia a entidad1 |
| entidad2_id | INT/UUID | FOREIGN KEY → entidad2(id) | Referencia a entidad2 |
| campo1 | TEXT | | [Descripción del campo] |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha de creación |

## Relaciones

### 1:N - Entidad1 → Entidad2
- **Descripción**: Una instancia de Entidad1 puede tener múltiples instancias de Entidad2
- **Cardinalidad**: 1:N
- **FK**: entidad2.entidad1_id → entidad1.id

### N:M - Entidad1 ↔ Entidad2 (si aplica)
- **Descripción**: [Describir la relación many-to-many]
- **Tabla intermedia**: entidad1_entidad2
- **Cardinalidad**: N:M

## Índices Recomendados

```sql
-- Índices para optimizar consultas frecuentes
CREATE INDEX idx_entidad1_campo1 ON entidad1(campo1);
CREATE INDEX idx_entidad2_entidad1_id ON entidad2(entidad1_id);
CREATE INDEX idx_entidad2_estado ON entidad2(estado);
CREATE INDEX idx_created_at ON entidad1(created_at);
```

## Constrains Adicionales

```sql
-- Constrains de negocio
ALTER TABLE entidad2 ADD CONSTRAINT check_campo2_positive 
    CHECK (campo2 > 0);

ALTER TABLE entidad1 ADD CONSTRAINT unique_campo1 
    UNIQUE (campo1);
```

## Seeds de Ejemplo

```sql
-- Datos de ejemplo para desarrollo y testing
INSERT INTO entidad1 (campo1, campo2, campo3) VALUES
    ('ejemplo1', '2024-01-01', 100.00),
    ('ejemplo2', '2024-01-02', 250.50),
    ('ejemplo3', '2024-01-03', 75.25);

INSERT INTO entidad2 (entidad1_id, campo1, campo2, estado) VALUES
    (1, 'descripcion1', 5, 'activo'),
    (1, 'descripcion2', 3, 'activo'),
    (2, 'descripcion3', 8, 'inactivo');
```

## TODO - Para completar según stack elegido

- [ ] Definir motor de base de datos específico (MySQL, PostgreSQL, etc.)
- [ ] Ajustar tipos de datos según el motor elegido
- [ ] Crear scripts de migración usando framework elegido
- [ ] Implementar validaciones a nivel de aplicación
- [ ] Configurar conexión desde el microservicio
- [ ] Definir políticas de backup y recovery
- [ ] Configurar monitoring y logging

## Notas de Implementación

- Usar **UUID** si se requiere distribución entre múltiples instancias
- Usar **AUTO_INCREMENT INT** para mejor performance en base única
- Considerar **particionado** si se esperan grandes volúmenes de datos
- Implementar **soft deletes** si se requiere auditoría
- Configurar **foreign key constraints** según políticas de negocio
