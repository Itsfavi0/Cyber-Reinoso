-- Creación de la base de datos
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'CyberReinoso')
BEGIN
    CREATE DATABASE CyberReinoso;
END
GO

-- Usamos a la base de datos correcto
USE CyberReinoso;
GO

-- Creamos las Tablas
IF OBJECT_ID('dbo.Usuarios', 'U') IS NULL
BEGIN
    CREATE TABLE Usuarios (
        id_usuario INT IDENTITY(1,1) PRIMARY KEY,
        alias_gamer VARCHAR(50) NOT NULL,
        rango_cuenta VARCHAR(20) DEFAULT 'Nuevo',
        saldo_billetera DECIMAL(8,2) DEFAULT 0.0
    );
    PRINT 'Tabla Usuarios creada correctamente.';
END
GO

IF OBJECT_ID('dbo.Estaciones', 'U') IS NULL
BEGIN
    CREATE TABLE Estaciones (
        id_estacion INT IDENTITY(1,1) PRIMARY KEY,
        codigo_pc VARCHAR(10) NOT NULL,
        categoria VARCHAR(20) NOT NULL,
        estado_actual VARCHAR(20) DEFAULT 'Disponible'
    );
    PRINT 'Tabla Estaciones creada correctamente.';
END
GO

IF OBJECT_ID('dbo.Sesiones', 'U') IS NULL
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
    PRINT 'Tabla Sesiones creada correctamente.';
END
GO