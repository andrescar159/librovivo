-- ============================================
-- LIBROVIVO - Datos Iniciales (CORREGIDO)
-- ============================================

USE librovivo;

-- ============================================
-- 1. CATEGORIAS DEWEY
-- ============================================
INSERT INTO categorias_dewey (codigo_dewey, nombre, descripcion) VALUES
('000', 'Generalidades', 'Obras generales, informatica, bibliotecologia'),
('100', 'Filosofia', 'Filosofia, psicologia, logica, etica'),
('200', 'Religion', 'Teologia, religiones del mundo, mitologia'),
('300', 'Ciencias Sociales', 'Sociologia, economia, derecho, educacion'),
('400', 'Lenguas', 'Linguistica, gramaticas, diccionarios'),
('500', 'Ciencias Naturales', 'Matematicas, fisica, quimica, biologia'),
('600', 'Tecnologia', 'Medicina, ingenieria, agricultura'),
('700', 'Artes', 'Arquitectura, musica, pintura, deportes'),
('800', 'Literatura', 'Poesia, teatro, novela, ensayo'),
('900', 'Historia y Geografia', 'Historia universal, geografia, biografias');

-- ============================================
-- 2. USUARIO ADMINISTRADOR
-- Contrasena: admin123
-- ============================================
INSERT INTO usuarios (nombre, apellido, email, password_hash, rol, documento, telefono, activo) VALUES
('Administrador', 'Sistema', 'admin@librovivo.com', '$2b$12$qV8X01/0zWWn9zuNY9koZ.jPnLMJgDsV8TnYdy0ilT4GwKyT0IKzi', 'admin', '1234567890', '3001234567', TRUE);

-- ============================================
-- 3. USUARIO BIBLIOTECARIO
-- Contrasena: biblio123
-- ============================================
INSERT INTO usuarios (nombre, apellido, email, password_hash, rol, documento, telefono, activo) VALUES
('Carlos', 'Martinez', 'bibliotecario@librovivo.com', '$2b$12$dI8eKmhtt4bHKtCuNp1JKOhHmmQZJAqXDrcSakxDqVp/W.u.j37SK', 'bibliotecario', '0987654321', '3009876543', TRUE);

-- ============================================
-- 4. ESTUDIANTES DE PRUEBA
-- Contrasena: estudiante123
-- ============================================
INSERT INTO usuarios (nombre, apellido, email, password_hash, rol, documento, telefono, activo) VALUES
('Juan', 'Perez', 'juan.perez@colegio.edu', '$2b$12$Fm/YyHMs8gFmI3PoJdH9zO.BmCdvK6vuysezUEHkTrYDsoraL33.C', 'estudiante', '1111111111', '3001111111', TRUE),
('Maria', 'Gomez', 'maria.gomez@colegio.edu', '$2b$12$Fm/YyHMs8gFmI3PoJdH9zO.BmCdvK6vuysezUEHkTrYDsoraL33.C', 'estudiante', '2222222222', '3002222222', TRUE),
('Ana', 'Lopez', 'ana.lopez@colegio.edu', '$2b$12$Fm/YyHMs8gFmI3PoJdH9zO.BmCdvK6vuysezUEHkTrYDsoraL33.C', 'estudiante', '3333333333', '3003333333', TRUE),
('Pedro', 'Rodriguez', 'pedro.rodriguez@colegio.edu', '$2b$12$Fm/YyHMs8gFmI3PoJdH9zO.BmCdvK6vuysezUEHkTrYDsoraL33.C', 'estudiante', '4444444444', '3004444444', TRUE),
('Laura', 'Torres', 'laura.torres@colegio.edu', '$2b$12$Fm/YyHMs8gFmI3PoJdH9zO.BmCdvK6vuysezUEHkTrYDsoraL33.C', 'estudiante', '5555555555', '3005555555', TRUE);

-- ============================================
-- 5. AUTORES DE PRUEBA
-- ============================================
INSERT INTO autores (nombre, nacionalidad, biografia) VALUES
('Gabriel Garcia Marquez', 'Colombiana', 'Escritor colombiano, premio Nobel de Literatura 1982'),
('Miguel de Cervantes', 'Espanola', 'Escritor espanol, autor de Don Quijote'),
('Homero', 'Griega', 'Poeta epico griego, autor de La Odisea'),
('William Shakespeare', 'Britanica', 'Dramaturgo y poeta ingles'),
('Antoine de Saint-Exupery', 'Francesa', 'Escritor y aviador frances'),
('Jorge Isaacs', 'Colombiana', 'Escritor colombiano, autor de Maria'),
('Jose Eustasio Rivera', 'Colombiana', 'Escritor colombiano, autor de La Voragine'),
('Alvaro Mutis', 'Colombiana', 'Poeta y novelista colombiano'),
('Fernando Botero', 'Colombiana', 'Pintor y escultor colombiano'),
('Silvia Galvis', 'Colombiana', 'Periodista y escritora colombiana');

-- ============================================
-- 6. LIBROS DE PRUEBA
-- ============================================
INSERT INTO libros (categoria_id, isbn, titulo, editorial, anio_publicacion, descripcion, area_conocimiento, activo) VALUES
(8, '978-0307474728', 'Cien anos de soledad', 'Editorial Sudamericana', 1967, 'Novela que narra la historia de la familia Buendia en el pueblo ficticio de Macondo.', 'Novela Latinoamericana', TRUE),
(8, '978-8420412146', 'El principito', 'Emecé Editores', 1943, 'Cuento filosofico sobre un pequeno principe que viaja por diferentes planetas.', 'Literatura Infantil', TRUE),
(8, '978-8467038324', 'Don Quijote de la Mancha', 'Espasa-Calpe', 1605, 'Novela que cuenta las aventuras de un hidalgo que enloquece leyendo libros de caballeria.', 'Novela Clasica', TRUE),
(8, '978-8491050360', 'La Odisea', 'Alianza Editorial', -800, 'Poema epico que narra el regreso de Odiseo a Itaca despues de la guerra de Troya.', 'Poesia Epica', TRUE),
(8, '978-0743477116', 'Romeo y Julieta', 'Simon & Schuster', 1597, 'Tragedia que cuenta la historia de dos jovenes amantes de familias enemistadas.', 'Teatro', TRUE),
(8, '978-9583003682', 'Maria', 'Norma', 1867, 'Novela romantica que narra un idilio entre un joven y una mestiza en el Valle del Cauca.', 'Novela Romantica', TRUE),
(8, '978-9583001220', 'La voragine', 'Norma', 1924, 'Novela que describe las atrocidades del caucho en la selva amazonica.', 'Novela Regional', TRUE),
(7, '978-9584213417', 'Botero: La busqueda de un estilo', 'Planeta', 2012, 'Libro sobre la obra y el estilo del pintor Fernando Botero.', 'Arte Colombiano', TRUE),
(3, '978-9584273541', 'Historia de Colombia', 'Planeta', 2015, 'Recorrido por la historia de Colombia desde la colonia hasta la actualidad.', 'Historia de Colombia', TRUE),
(5, '978-9587781005', 'Biologia para todos', 'Panamericana', 2018, 'Libro de texto de biologia para estudiantes de secundaria.', 'Biologia General', TRUE),
(5, '978-9587782012', 'Fisica Conceptual', 'Pearson', 2019, 'Introduccion a los conceptos fundamentales de la fisica.', 'Fisica', TRUE),
(6, '978-9584271003', 'Manual de ingenieria civil', 'Uniandes', 2020, 'Compendio de conocimientos tecnicos para ingenieria civil.', 'Ingenieria Civil', TRUE),
(1, '978-9583005006', 'Enciclopedia de Ciencias', 'Santillana', 2010, 'Enciclopedia general de ciencias para consulta en sala.', 'Enciclopedia', TRUE),
(1, '978-9583005013', 'Atlas Mundial', 'Santillana', 2011, 'Atlas geografico mundial con mapas detallados.', 'Geografia', TRUE);

-- ============================================
-- 7. RELACION LIBROS-AUTORES
-- ============================================
INSERT INTO libros_autores (libro_id, autor_id) VALUES
(1, 1),
(2, 5),
(3, 2),
(4, 3),
(5, 4),
(6, 6),
(7, 7),
(8, 9),
(9, 10),
(10, 10),
(11, 10),
(12, 10);

-- ============================================
-- 8. EJEMPLARES DE PRUEBA
-- ============================================
INSERT INTO ejemplares (libro_id, codigo_barras, estado, es_prestable, ubicacion, activo) VALUES
(1, 'LV-00001', 'disponible', TRUE, 'Estante A-1', TRUE),
(1, 'LV-00002', 'disponible', TRUE, 'Estante A-1', TRUE),
(1, 'LV-00003', 'prestado', TRUE, 'Estante A-1', TRUE),
(2, 'LV-00004', 'disponible', TRUE, 'Estante A-2', TRUE),
(2, 'LV-00005', 'disponible', TRUE, 'Estante A-2', TRUE),
(3, 'LV-00006', 'disponible', TRUE, 'Estante A-3', TRUE),
(3, 'LV-00007', 'prestado', TRUE, 'Estante A-3', TRUE),
(4, 'LV-00008', 'disponible', TRUE, 'Estante A-4', TRUE),
(5, 'LV-00009', 'disponible', TRUE, 'Estante A-5', TRUE),
(5, 'LV-00010', 'disponible', TRUE, 'Estante A-5', TRUE),
(6, 'LV-00011', 'disponible', TRUE, 'Estante B-1', TRUE),
(7, 'LV-00012', 'disponible', TRUE, 'Estante B-2', TRUE),
(8, 'LV-00013', 'disponible', FALSE, 'Sala de Arte - Estante 1', TRUE),
(9, 'LV-00014', 'disponible', TRUE, 'Estante C-1', TRUE),
(10, 'LV-00015', 'disponible', TRUE, 'Estante D-1', TRUE),
(10, 'LV-00016', 'disponible', TRUE, 'Estante D-1', TRUE),
(11, 'LV-00017', 'disponible', TRUE, 'Estante D-2', TRUE),
(12, 'LV-00018', 'disponible', FALSE, 'Sala de Consulta - Estante 3', TRUE),
(13, 'LV-00019', 'disponible', FALSE, 'Sala de Consulta - Estante 1', TRUE),
(14, 'LV-00020', 'disponible', FALSE, 'Sala de Consulta - Estante 2', TRUE);

-- ============================================
-- 9. PRESTAMOS DE PRUEBA
-- ============================================
INSERT INTO prestamos (ejemplar_id, usuario_id, bibliotecario_id, fecha_prestamo, fecha_devolucion_prevista, estado, renovaciones_usadas) VALUES
(3, 3, 2, DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_ADD(NOW(), INTERVAL 10 DAY), 'activo', 0),
(7, 4, 2, DATE_SUB(NOW(), INTERVAL 12 DAY), DATE_ADD(NOW(), INTERVAL 3 DAY), 'activo', 1),
(1, 5, 2, DATE_SUB(NOW(), INTERVAL 20 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY), 'activo', 0);

-- ============================================
-- 10. MULTA DE PRUEBA
-- ============================================
INSERT INTO multas (prestamo_id, usuario_id, dias_retraso, monto, estado) VALUES
(3, 5, 5, 2500.00, 'pendiente');

-- ============================================
-- 11. RESERVAS DE PRUEBA
-- ============================================
INSERT INTO reservas (libro_id, usuario_id, fecha_reserva, fecha_vencimiento, estado, notificacion_enviada) VALUES
(2, 3, DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_ADD(NOW(), INTERVAL 2 DAY), 'activa', FALSE),
(4, 4, DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_ADD(NOW(), INTERVAL 1 DAY), 'activa', FALSE);

-- ============================================
-- 12. RESENAS DE PRUEBA
-- ============================================
INSERT INTO resenas (libro_id, usuario_id, calificacion, comentario, activo) VALUES
(1, 3, 5, 'Una obra maestra de la literatura latinoamericana. Magico realismo en su maxima expresion.', TRUE),
(1, 4, 4, 'Excelente novela, aunque un poco confusa al principio.', TRUE),
(2, 3, 5, 'Hermoso cuento para todas las edades. Muy filosofico.', TRUE),
(3, 5, 5, 'El mejor libro de la literatura espanola. Imprescindible.', TRUE),
(5, 4, 4, 'Tragedia clasica muy conmovedora.', TRUE);

-- ============================================
-- DATOS INICIALES COMPLETADOS (CORREGIDOS)
-- ============================================