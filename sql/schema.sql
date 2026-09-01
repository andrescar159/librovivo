-- ============================================
-- LIBROVIVO - Esquema de Base de Datos MySQL
-- ============================================

CREATE DATABASE IF NOT EXISTS librovivo 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE librovivo;

-- ============================================
-- 1. CATEGORIAS DEWEY
-- ============================================
CREATE TABLE IF NOT EXISTS categorias_dewey (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_dewey VARCHAR(10) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. AUTORES
-- ============================================
CREATE TABLE IF NOT EXISTS autores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    nacionalidad VARCHAR(50),
    biografia TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. LIBROS
-- ============================================
CREATE TABLE IF NOT EXISTS libros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    categoria_id INT NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    titulo VARCHAR(200) NOT NULL,
    editorial VARCHAR(100),
    anio_publicacion INT,
    descripcion TEXT,
    portada_url VARCHAR(255),
    area_conocimiento VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias_dewey(id)
);

-- ============================================
-- 4. LIBROS_AUTORES (RELACION N:M)
-- ============================================
CREATE TABLE IF NOT EXISTS libros_autores (
    libro_id INT NOT NULL,
    autor_id INT NOT NULL,
    PRIMARY KEY (libro_id, autor_id),
    FOREIGN KEY (libro_id) REFERENCES libros(id) ON DELETE CASCADE,
    FOREIGN KEY (autor_id) REFERENCES autores(id) ON DELETE CASCADE
);

-- ============================================
-- 5. EJEMPLARES
-- ============================================
CREATE TABLE IF NOT EXISTS ejemplares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    libro_id INT NOT NULL,
    codigo_barras VARCHAR(50) UNIQUE,
    estado ENUM('disponible','prestado','en_reparacion','dado_de_baja') DEFAULT 'disponible',
    es_prestable BOOLEAN DEFAULT TRUE,
    ubicacion VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (libro_id) REFERENCES libros(id)
);

-- ============================================
-- 6. USUARIOS
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('admin','bibliotecario','estudiante') NOT NULL,
    documento VARCHAR(20) UNIQUE,
    telefono VARCHAR(20),
    foto_perfil VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 7. PRESTAMOS
-- ============================================
CREATE TABLE IF NOT EXISTS prestamos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ejemplar_id INT NOT NULL,
    usuario_id INT NOT NULL,
    bibliotecario_id INT NOT NULL,
    fecha_prestamo DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_devolucion_prevista DATETIME NOT NULL,
    fecha_devolucion_real DATETIME,
    estado ENUM('activo','devuelto','vencido','perdido') DEFAULT 'activo',
    renovaciones_usadas INT DEFAULT 0,
    observaciones TEXT,
    FOREIGN KEY (ejemplar_id) REFERENCES ejemplares(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (bibliotecario_id) REFERENCES usuarios(id)
);

-- ============================================
-- 8. MULTAS
-- ============================================
CREATE TABLE IF NOT EXISTS multas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prestamo_id INT NOT NULL,
    usuario_id INT NOT NULL,
    dias_retraso INT NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    estado ENUM('pendiente','pagada','condonada') DEFAULT 'pendiente',
    fecha_pago DATETIME,
    observaciones TEXT,
    FOREIGN KEY (prestamo_id) REFERENCES prestamos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ============================================
-- 9. RESERVAS
-- ============================================
CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    libro_id INT NOT NULL,
    usuario_id INT NOT NULL,
    fecha_reserva DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATETIME NOT NULL,
    estado ENUM('activa','completada','vencida','cancelada') DEFAULT 'activa',
    notificacion_enviada BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (libro_id) REFERENCES libros(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ============================================
-- 10. RESENAS
-- ============================================
CREATE TABLE IF NOT EXISTS resenas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    libro_id INT NOT NULL,
    usuario_id INT NOT NULL,
    calificacion INT NOT NULL CHECK (calificacion BETWEEN 1 AND 5),
    comentario TEXT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (libro_id) REFERENCES libros(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ============================================
-- 11. NOTIFICACIONES
-- ============================================
CREATE TABLE IF NOT EXISTS notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo ENUM('recordatorio','reserva_disponible','vencimiento') NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    leida BOOLEAN DEFAULT FALSE,
    email_enviado BOOLEAN DEFAULT FALSE,
    relacion_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ============================================
-- INDICES PARA MEJORAR RENDIMIENTO
-- ============================================
CREATE INDEX idx_libros_categoria ON libros(categoria_id);
CREATE INDEX idx_libros_activo ON libros(activo);
CREATE INDEX idx_ejemplares_libro ON ejemplares(libro_id);
CREATE INDEX idx_ejemplares_estado ON ejemplares(estado);
CREATE INDEX idx_prestamos_usuario ON prestamos(usuario_id);
CREATE INDEX idx_prestamos_estado ON prestamos(estado);
CREATE INDEX idx_prestamos_fecha ON prestamos(fecha_devolucion_prevista);
CREATE INDEX idx_multas_usuario ON multas(usuario_id);
CREATE INDEX idx_multas_estado ON multas(estado);
CREATE INDEX idx_reservas_usuario ON reservas(usuario_id);
CREATE INDEX idx_reservas_estado ON reservas(estado);
CREATE INDEX idx_reservas_libro ON reservas(libro_id);
CREATE INDEX idx_resenas_libro ON resenas(libro_id);
CREATE INDEX idx_notificaciones_usuario ON notificaciones(usuario_id);
CREATE INDEX idx_notificaciones_leida ON notificaciones(leida);