-- Limpiar datos existentes
DELETE FROM trips;
DELETE FROM routes;

-- Insertar rutas
INSERT INTO routes (route_id, route_name, origin_city, destination_city, distance_km, estimated_duration, base_price, currency, active, created_at, updated_at) VALUES
('LIM_CUZ_001', 'Lima - Cusco Express', 'Lima', 'Cusco', 1165.5, '20:00:00', 120.00, 'PEN', 1, NOW(), NOW()),
('LIM_ARE_002', 'Lima - Arequipa Ejecutivo', 'Lima', 'Arequipa', 1009.0, '16:30:00', 95.50, 'PEN', 1, NOW(), NOW()),
('LIM_TRU_003', 'Lima - Trujillo Directo', 'Lima', 'Trujillo', 561.0, '08:45:00', 75.00, 'PEN', 1, NOW(), NOW()),
('ARE_CUZ_004', 'Arequipa - Cusco Turístico', 'Arequipa', 'Cusco', 315.0, '06:00:00', 60.00, 'PEN', 1, NOW(), NOW()),
('CUZ_PUN_005', 'Cusco - Puno Altiplano', 'Cusco', 'Puno', 389.0, '07:30:00', 65.00, 'PEN', 1, NOW(), NOW()),
('LIM_ICA_006', 'Lima - Ica Express', 'Lima', 'Ica', 303.0, '04:30:00', 45.00, 'PEN', 1, NOW(), NOW());

-- Insertar 10 viajes
INSERT INTO trips (trip_id, route_id, departure_date_time, arrival_date_time, bus_capacity, available_seats, final_price, status, driver_name, created_at, updated_at) VALUES
('TRP_20251006_LIM_CUZ_01', 'LIM_CUZ_001', DATE_ADD(NOW(), INTERVAL 1 DAY) + INTERVAL 22 HOUR, DATE_ADD(NOW(), INTERVAL 1 DAY) + INTERVAL 42 HOUR, 45, 45, 120.00, 'scheduled', 'Carlos Mendoza', NOW(), NOW()),
('TRP_20251006_LIM_ARE_02', 'LIM_ARE_002', DATE_ADD(NOW(), INTERVAL 1 DAY) + INTERVAL 23 HOUR + INTERVAL 30 MINUTE, DATE_ADD(NOW(), INTERVAL 2 DAY) + INTERVAL 16 HOUR, 40, 35, 95.50, 'scheduled', 'Ana Rodriguez', NOW(), NOW()),
('TRP_20251006_LIM_TRU_03', 'LIM_TRU_003', DATE_ADD(NOW(), INTERVAL 1 DAY) + INTERVAL 6 HOUR, DATE_ADD(NOW(), INTERVAL 1 DAY) + INTERVAL 14 HOUR + INTERVAL 45 MINUTE, 35, 30, 75.00, 'scheduled', 'Miguel Santos', NOW(), NOW()),
('TRP_20251007_ARE_CUZ_04', 'ARE_CUZ_004', DATE_ADD(NOW(), INTERVAL 2 DAY) + INTERVAL 8 HOUR, DATE_ADD(NOW(), INTERVAL 2 DAY) + INTERVAL 14 HOUR, 32, 28, 60.00, 'scheduled', 'Carmen López', NOW(), NOW()),
('TRP_20251007_CUZ_PUN_05', 'CUZ_PUN_005', DATE_ADD(NOW(), INTERVAL 2 DAY) + INTERVAL 14 HOUR + INTERVAL 30 MINUTE, DATE_ADD(NOW(), INTERVAL 2 DAY) + INTERVAL 22 HOUR, 38, 38, 65.00, 'scheduled', 'Roberto Quispe', NOW(), NOW()),
('TRP_20251007_LIM_ICA_06', 'LIM_ICA_006', DATE_ADD(NOW(), INTERVAL 2 DAY) + INTERVAL 10 HOUR, DATE_ADD(NOW(), INTERVAL 2 DAY) + INTERVAL 14 HOUR + INTERVAL 30 MINUTE, 30, 25, 45.00, 'scheduled', 'Patricia Flores', NOW(), NOW()),
('TRP_20251008_LIM_CUZ_07', 'LIM_CUZ_001', DATE_ADD(NOW(), INTERVAL 3 DAY) + INTERVAL 21 HOUR + INTERVAL 30 MINUTE, DATE_ADD(NOW(), INTERVAL 4 DAY) + INTERVAL 17 HOUR + INTERVAL 30 MINUTE, 45, 40, 120.00, 'scheduled', 'Jorge Ramirez', NOW(), NOW()),
('TRP_20251008_LIM_TRU_08', 'LIM_TRU_003', DATE_ADD(NOW(), INTERVAL 3 DAY) + INTERVAL 15 HOUR, DATE_ADD(NOW(), INTERVAL 3 DAY) + INTERVAL 23 HOUR + INTERVAL 45 MINUTE, 35, 35, 75.00, 'scheduled', 'Luis Castillo', NOW(), NOW()),
('TRP_20251009_LIM_ARE_09', 'LIM_ARE_002', DATE_ADD(NOW(), INTERVAL 4 DAY) + INTERVAL 20 HOUR, DATE_ADD(NOW(), INTERVAL 5 DAY) + INTERVAL 12 HOUR + INTERVAL 30 MINUTE, 40, 32, 95.50, 'scheduled', 'Elena Martinez', NOW(), NOW()),
('TRP_20251009_CUZ_PUN_10', 'CUZ_PUN_005', DATE_ADD(NOW(), INTERVAL 4 DAY) + INTERVAL 9 HOUR, DATE_ADD(NOW(), INTERVAL 4 DAY) + INTERVAL 16 HOUR + INTERVAL 30 MINUTE, 38, 36, 65.00, 'scheduled', 'Fernando Silva', NOW(), NOW());

-- Verificar los datos insertados
SELECT 'Rutas insertadas:' as Mensaje;
SELECT route_id, route_name FROM routes;

SELECT 'Viajes insertados:' as Mensaje;
SELECT trip_id, route_id, departure_date_time, status FROM trips;
