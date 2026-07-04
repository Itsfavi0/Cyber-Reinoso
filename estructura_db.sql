-- Creación de la base de datos
IF DB_ID('CyberReinoso') IS NULL
BEGIN
    CREATE DATABASE CyberReinoso
	PRINT 'Base de datos creada exitosamente.'
END
ELSE
BEGIN
	PRINT 'Base de datos ya existe.'
END
GO

-- Usamos base de datos correcta
USE CyberReinoso
GO

-- Creamos las Tablas
IF OBJECT_ID('Usuarios', 'U') IS NULL
BEGIN
    CREATE TABLE Usuarios (
        id_usuario INT IDENTITY(1,1) PRIMARY KEY,
        alias_gamer VARCHAR(50) NOT NULL,
        rango_cuenta VARCHAR(20) DEFAULT 'Nuevo',
        saldo_billetera DECIMAL(8,2) DEFAULT 0.0
    );
    PRINT 'Tabla Usuarios creada correctamente.'
END
GO

IF OBJECT_ID('Estaciones', 'U') IS NULL
BEGIN
    CREATE TABLE Estaciones (
        id_estacion INT IDENTITY(1,1) PRIMARY KEY,
        codigo_pc VARCHAR(10) NOT NULL,
        categoria VARCHAR(20) NOT NULL,
        estado_actual VARCHAR(20) DEFAULT 'Disponible'
    );
    PRINT 'Tabla Estaciones creada correctamente.'
END
GO

IF OBJECT_ID('Sesiones', 'U') IS NULL
BEGIN
    CREATE TABLE Sesiones (
        id_sesion INT IDENTITY(1,1) PRIMARY KEY,
        id_usuario INT NOT NULL,
        id_estacion INT NOT NULL,
        hora_inicio DATETIME NOT NULL,
        hora_fin DATETIME NULL,
        monto_cobrado DECIMAL(8,2) NULL,

        CONSTRAINT FK_Sesion_Usuario FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
        CONSTRAINT FK_Sesion_Estacion FOREIGN KEY (id_estacion) REFERENCES Estaciones(id_estacion)
    );
    PRINT 'Tabla Sesiones creada correctamente.'
END
GO

IF OBJECT_ID('Productos', 'U') IS NULL
BEGIN
    CREATE TABLE Productos (
        id_producto INT IDENTITY(1,1) PRIMARY KEY,
        nombre_producto VARCHAR(50) NOT NULL,
        precio DECIMAL(8,2) NOT NULL,
        stock INT NOT NULL DEFAULT 0
    )
    PRINT 'Tabla Productos creada correctamente.'
END
GO

INSERT INTO Usuarios (alias_gamer, rango_cuenta, saldo_billetera)
VALUES ('Itsfavi0', 'VIP', 50.00)
GO

INSERT INTO Estaciones (codigo_pc, categoria, estado_actual)
VALUES 
    ('PC-001', 'Regular', 'Disponible'),
    ('PC-002', 'Regular', 'Disponible'),
    ('PC-003', 'Regular', 'Mantenimiento'),
    ('VIP-001', 'VIP', 'Disponible'),
    ('VIP-002', 'VIP', 'Disponible');
GO

INSERT INTO Productos (nombre_producto, precio, stock)
VALUES
('Gaseosa Inka Cola 600ml', 3.50, 24),
('Cuate Picante', 1.00, 15),
('Recarga 1 Hora', 2.00, 9999)
GO