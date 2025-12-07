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
('PRIMAVERA-2024', '2024-01-15', '2024-05-20'),
('OTOÑO-2024', '2024-08-01', '2024-12-10'),
('PRIMAVERA-2025', '2025-01-15', '2025-05-20'),
('OTOÑO-2025', '2025-08-01', '2025-12-10'),
('PRIMAVERA-2026', '2026-01-15', '2026-05-20'),
('OTOÑO-2026', '2026-08-01', '2026-12-10'),
('PRIMAVERA-2027', '2027-01-15', '2027-05-20'),
('OTOÑO-2027', '2027-08-01', '2027-12-10'),
('PRIMAVERA-2028', '2028-01-15', '2028-05-20'),
('OTOÑO-2028', '2028-08-01', '2028-12-10');

-- Subjects
INSERT INTO materia VALUES 
('LIS-2082', 'Bases de Datos'),
('LIS-3040', 'Ingeniería de Software'),
('MAT-1010', 'Cálculo I'),
('MAT-1020', 'Teoría de Matrices'),
('MAT-1030', 'Análisis Matemático'),
('MAT-1040', 'Modelos Estocásticos'),
('LEN-1001', 'Italiano'),
('LIS-4050', 'Redes Neuronales');

-- Classrooms
INSERT INTO salon VALUES 
('IA104', 30, 'Laboratorio'),
('IA105', 25, 'Aula'),
('IA106', 20, 'Aula'),
('IA201', 35, 'Laboratorio'),
('IA202', 25, 'Aula'),

('CN101', 45, 'Aula'),
('CN102', 40, 'Aula'),
('CN103', 50, 'Auditorio'),
('CN104', 35, 'Aula'),
('CN105', 40, 'Aula'),

('HU201', 90, 'Auditorio'),
('HU202', 100, 'Auditorio'),
('HU203', 55, 'Aula'),
('HU204', 30, 'Aula'),

('NE101', 20, 'Laboratorio'),
('NE102', 30, 'Laboratorio'),
('NE201', 40, 'Aula'),
('NE202', 15, 'Aula'),

('LA101', 40, 'Aula'),
('LA102', 45, 'Aula'),
('LA103', 32, 'Laboratorio'),
('LA201', 28, 'Aula');

-- Users
INSERT INTO usuario VALUES 
('100100', 'Dr. Zechinelli', 'Profesor'),
('160000', 'Juan Pérez', 'Estudiante'),
('100000', 'Coordinación', 'Administrador');

-- Courses (We offer Databases in two sections)
INSERT INTO curso VALUES 
('LIS-2082', 1, 'PRIMAVERA-2024', 'Dr. Zechinelli'),
('LIS-2082', 2, 'PRIMAVERA-2024', 'Prof. Sustituto'),
('MAT-1010', 1, 'PRIMAVERA-2024', 'Prof. Matemático'),
('MAT-1020', 1, 'PRIMAVERA-2024', 'Dra. Matriciana'),
('LEN-1001', 1, 'PRIMAVERA-2024', 'Prof. Linguini'),
('LIS-4050', 1, 'PRIMAVERA-2024', 'Dra. Neuman');

-- Schedules (Atomicity: 1 row per class block)
-- Section 1 of Databases: Monday and Wednesday in the Laboratory
INSERT INTO horario (clave_materia, seccion_curso, id_periodo, id_salon, dia_semana, hora_inicio, duracion_minutos) VALUES 
('LIS-2082', 1, 'PRIMAVERA-2024', 'IA104', 'Lunes', '09:00:00', 90),
('LIS-2082', 1, 'PRIMAVERA-2024', 'IA104', 'Miercoles', '09:00:00', 90),
('LIS-2082', 2, 'PRIMAVERA-2024', 'IA105', 'Martes', '10:30:00', 90),
('LIS-2082', 2, 'PRIMAVERA-2024', 'IA105', 'Jueves', '10:30:00', 90),
('MAT-1010', 1, 'PRIMAVERA-2024', 'HU201', 'Lunes', '12:00:00', 120),
('LEN-1001', 1, 'PRIMAVERA-2024', 'LA101', 'Viernes', '08:00:00', 60),
('LIS-4050', 1, 'PRIMAVERA-2024', 'CN103', 'Miercoles', '14:00:00', 110);

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