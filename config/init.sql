DROP DATABASE IF EXISTS scheduleee;
CREATE DATABASE scheduleee CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE scheduleee;

-- 1. PERIODS table (Catalog)
CREATE TABLE periodo (
    id_periodo VARCHAR(20) PRIMARY KEY, -- Example: 'PRIMAVERA-2024'
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    CONSTRAINT check_fechas CHECK (fecha_fin >= fecha_inicio)
);

-- 2. SUBJECTS table
CREATE TABLE materia (
    clave VARCHAR(10) PRIMARY KEY, -- Example: 'LIS-2082'
    titulo VARCHAR(100) NOT NULL
);

-- 3. CLASSROOMS table (Catalog)
CREATE TABLE salon (
    id_salon VARCHAR(10) PRIMARY KEY, -- Example: 'IA104'
    capacidad INT NOT NULL CHECK (capacidad > 0),
    tipo ENUM('Aula', 'Laboratorio', 'Auditorio') NOT NULL
);

-- 4. USERS table (For reservations)
CREATE TABLE usuario (
    id_usuario VARCHAR(20) PRIMARY KEY, -- ID or Registration number
    nombre VARCHAR(100) NOT NULL,
    rol ENUM('Estudiante', 'Profesor', 'Administrador') NOT NULL
);

-- 5. COURSES table (Academic Offering)
CREATE TABLE curso (
    -- The primary key is composite to identify a unique offering
    clave_materia VARCHAR(10),
    seccion INT,
    id_periodo VARCHAR(20),
    profesor VARCHAR(100), -- Name of the assigned professor

    PRIMARY KEY (clave_materia, seccion, id_periodo),

    -- Foreign Keys
    FOREIGN KEY (clave_materia) REFERENCES materia(clave) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_periodo) REFERENCES periodo(id_periodo)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 6. SCHEDULE table (Detail of days and hours)
-- We split the list of days to comply with 1NF
CREATE TABLE horario (
    id_horario INT AUTO_INCREMENT PRIMARY KEY,

    -- FKs to Course (Composite key of 3 parts)
    clave_materia VARCHAR(10),
    seccion_curso INT,
    id_periodo VARCHAR(20),

    -- FK to Classroom
    id_salon VARCHAR(10),

    -- Schedule data
    dia_semana ENUM('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado') NOT NULL,
    hora_inicio TIME NOT NULL,
    duracion_minutos INT NOT NULL CHECK (duracion_minutos > 0),

    -- Relationship definitions
    FOREIGN KEY (clave_materia, seccion_curso, id_periodo) 
        REFERENCES curso(clave_materia, seccion, id_periodo)
        ON DELETE CASCADE,

    FOREIGN KEY (id_salon) REFERENCES salon(id_salon)
);

-- 7. RESERVATION table (One-off events)
CREATE TABLE reservacion (
    id_reservacion INT AUTO_INCREMENT PRIMARY KEY,

    -- FKs
    id_usuario VARCHAR(20) NOT NULL,
    id_salon VARCHAR(10) NOT NULL,
    id_periodo VARCHAR(20) NOT NULL, -- Optional if deduced by date, but useful for reports

    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    duracion_minutos INT NOT NULL,
    motivo VARCHAR(200),

    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_salon) REFERENCES salon(id_salon),
    FOREIGN KEY (id_periodo) REFERENCES periodo(id_periodo)
);

-- Periods
INSERT INTO periodo VALUES 
('OTOÑO-2023', '2023-08-01', '2023-12-10'),
('PRIMAVERA-2024', '2024-01-15', '2024-05-20');

-- Subjects
INSERT INTO materia VALUES 
('LIS-2082', 'Bases de Datos'),
('LIS-3040', 'Ingeniería de Software'),
('MAT-1010', 'Cálculo I');

-- Classrooms
INSERT INTO salon VALUES 
('IA104', 30, 'Laboratorio'),
('CN105', 40, 'Aula'),
('HU202', 100, 'Auditorio');

-- Users
INSERT INTO usuario VALUES 
('U001', 'Dr. Zechinelli', 'Profesor'),
('160000', 'Juan Pérez', 'Estudiante'),
('ADMIN', 'Coordinación', 'Administrador');

-- Courses (We offer Databases in two sections)
INSERT INTO curso VALUES 
('LIS-2082', 1, 'PRIMAVERA-2024', 'Dr. Zechinelli'),
('LIS-2082', 2, 'PRIMAVERA-2024', 'Prof. Sustituto'),
('MAT-1010', 1, 'PRIMAVERA-2024', 'Prof. Matemático');

-- Schedules (Atomicity: 1 row per class block)
-- Section 1 of Databases: Monday and Wednesday in the Laboratory
INSERT INTO horario (clave_materia, seccion_curso, id_periodo, id_salon, dia_semana, hora_inicio, duracion_minutos) VALUES 
('LIS-2082', 1, 'PRIMAVERA-2024', 'IA104', 'Lunes', '09:00:00', 90),
('LIS-2082', 1, 'PRIMAVERA-2024', 'IA104', 'Miercoles', '09:00:00', 90);

-- Reservations (A one-off event)
INSERT INTO reservacion (id_usuario, id_salon, id_periodo, fecha, hora_inicio, duracion_minutos, motivo) VALUES 
('160000', 'HU202', 'PRIMAVERA-2024', '2024-02-14', '16:00:00', 120, 'Evento del Club de Programación');

-- Display the complete schedule in a "readable" way
SELECT 
    h.dia_semana, 
    h.hora_inicio, 
    m.titulo AS materia, 
    c.seccion, 
    h.id_salon,
    c.profesor
FROM horario h
JOIN curso c ON h.clave_materia = c.clave_materia 
             AND h.seccion_curso = c.seccion 
             AND h.id_periodo = c.id_periodo
JOIN materia m ON c.clave_materia = m.clave
ORDER BY h.dia_semana, h.hora_inicio;