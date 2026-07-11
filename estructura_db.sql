-- =========================================================
-- CREACION DE LA BASE DE DATOS
-- =========================================================
IF DB_ID('CyberReinoso') IS NULL
BEGIN
    CREATE DATABASE CyberReinoso
END
GO

USE CyberReinoso
GO

-- =========================================================
-- 1. TABLAS MAESTRAS (CATÁLOGOS)
-- =========================================================

CREATE TABLE Roles (
    id_rol INT IDENTITY(1,1) PRIMARY KEY,
    nombre_rol VARCHAR(50) UNIQUE NOT NULL -- 'Administrador', 'Cajero'
)
GO

CREATE TABLE RangosCuenta (
    id_rango INT IDENTITY(1,1) PRIMARY KEY,
    nombre_rango VARCHAR(30) UNIQUE NOT NULL, -- 'Bronce', 'Plata', 'Oro', 'Diamante'
    porcentaje_descuento DECIMAL(4,2) NOT NULL DEFAULT 0.00
)
GO

CREATE TABLE CategoriasEstacion (
    id_categoria INT IDENTITY(1,1) PRIMARY KEY,
    nombre_categoria VARCHAR(50) UNIQUE NOT NULL, -- 'Regular', 'eSports', 'Streaming VIP'
    tarifa_hora DECIMAL(10,2) NOT NULL
)
GO


-- =========================================================
-- 2. TABLAS PRINCIPALES (ENTIDADES)
-- =========================================================

CREATE TABLE Empleados (
    id_empleado INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    clave VARCHAR(50) NOT NULL,
    id_rol INT NOT NULL,

    FOREIGN KEY (id_rol) REFERENCES Roles(id_rol)
)
GO

CREATE TABLE Usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    alias_gamer VARCHAR(50) UNIQUE NOT NULL,
    id_rango INT NOT NULL DEFAULT 1,
    saldo_billetera DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    minutos_acumulados INT NOT NULL DEFAULT 0,

    FOREIGN KEY (id_rango) REFERENCES RangosCuenta(id_rango)
)
GO

CREATE TABLE Productos (
    id_producto INT IDENTITY(1,1) PRIMARY KEY,
    nombre_producto VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL
)
GO

CREATE TABLE Computadoras (
    codigo_pc VARCHAR(20) PRIMARY KEY,
    procesador VARCHAR(100) NOT NULL,
    tarjeta_grafica VARCHAR(100) NOT NULL,
    monitor VARCHAR(100) NOT NULL,
    teclado VARCHAR(100),
    mouse VARCHAR(100),
    microfono VARCHAR(100),
    camara VARCHAR(100)
)
GO

CREATE TABLE Estaciones (
    id_estacion INT IDENTITY(1,1) PRIMARY KEY,
    tipo_estacion VARCHAR(50) NOT NULL, 
    codigo_pc VARCHAR(20) NULL,
    id_categoria INT NOT NULL,
    estado_actual VARCHAR(20) NOT NULL DEFAULT 'Disponible',

    FOREIGN KEY (codigo_pc) REFERENCES Computadoras(codigo_pc),
    FOREIGN KEY (id_categoria) REFERENCES CategoriasEstacion(id_categoria)
)
GO


-- =========================================================
-- 3. TABLAS OPERACIONALES (TRANSACCIONALES)
-- =========================================================

CREATE TABLE Sesiones (
    id_sesion INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_empleado INT NOT NULL,
    id_estacion INT NOT NULL,
    hora_inicio DATETIME NOT NULL DEFAULT GETDATE(),
    hora_fin DATETIME NULL,
    monto_cobrado DECIMAL(10,2) NULL,

    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado),
    FOREIGN KEY (id_estacion) REFERENCES Estaciones(id_estacion)
)
GO

CREATE TABLE Ventas (
    id_venta INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_empleado INT NOT NULL,
    fecha_venta DATETIME NOT NULL DEFAULT GETDATE(),
    monto_total DECIMAL(10,2) NOT NULL, 

    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
)
GO

CREATE TABLE DetalleVentas (
    id_detalle INT IDENTITY(1,1) PRIMARY KEY,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (id_venta) REFERENCES Ventas(id_venta),
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
)
GO

-- =========================================================
-- 4. INSERCIÓN DE DATOS
-- =========================================================

-- Datos semilla para tablas maestras
INSERT INTO Roles (nombre_rol) VALUES ('Administrador'), ('Cajero');

INSERT INTO RangosCuenta (nombre_rango, porcentaje_descuento) 
VALUES 
('Bronce', 0.00),
('Plata', 0.05),
('Oro', 0.10),
('Diamante', 0.15)
GO

INSERT INTO CategoriasEstacion (nombre_categoria, tarifa_hora) 
VALUES 
('Regular', 2.00),
('eSports', 3.00),
('Streaming VIP', 5.00)
GO

-- Personal (FKs: 1 = Admin, 2 = Cajero)
INSERT INTO Empleados (nombre, usuario, clave, id_rol) 
VALUES 
('Favio', 'admin', '1234', 1),
('Renzo', 'renzo_caja', '0000', 2)
GO

-- Gamers (FKs: 1 = Bronce, 2 = Plata, 3 = Oro, 4 = Diamante)
INSERT INTO Usuarios (alias_gamer, id_rango, saldo_billetera, minutos_acumulados) 
VALUES 
('Invitado', 1, 200, 0),
('Maximus_27', 1, 15.50, 120),
('Jojo', 2, 25.00, 1500),
('flamed4rk', 3, 40.00, 4500),
('Dark', 4, 120.00, 7200),
('Wacho', 1, 5.00, 45),
('mzmiguelxd', 2, 30.00, 2100),
('RENZX', 4, 80.00, 6500)
GO

-- Inventario de Kiosco
INSERT INTO Productos (nombre_producto, precio, stock)
VALUES
('KitKat 41.5 g', 2.50, 20),
('Doritos Queso 45 g', 3.00, 25),
('Piqueo Snack 100 g', 2.00, 18),
('Monster Energy 473 ml', 8.00, 12),
('Volt 500 ml', 4.50, 15),
('Coca Cola 600 ml', 3.50, 24),
('Inca Kola 600 ml', 3.50, 24),
('Cuates Picante 50 g', 1.00, 15),
('Cifrut Naranja 500 ml', 2.50, 20);

GO

-- Hardware Físico
INSERT INTO Computadoras (codigo_pc, procesador, tarjeta_grafica, monitor, mouse) 
VALUES 
('PC-001', 'AMD Ryzen 5 8600G', 'Gráficos Integrados Radeon', 'MSI PRO MP243L E14 100Hz FHD', 'Genérico'),
('PC-002', 'AMD Ryzen 5 8600G', 'Gráficos Integrados Radeon', 'MSI PRO MP243L E14 100Hz FHD', 'Genérico'),
('PC-003', 'Intel Core i5', 'RTX 3060', 'ASUS TUF VG249Q5A 165Hz FHD', 'Ajazz AJ179 Apex'),
('PC-004', 'Intel Core i7', 'RTX 4060 Ti', 'LG UltraGear 27G523B-B 200Hz FHD', 'Ajazz AJ179 Apex'),
('PC-005', 'AMD Ryzen 9', 'RTX 4090', 'Samsung Odyssey OLED G8 250Hz 4K', 'Logitech G Pro Superlight')
GO

-- Asignación a los Módulos (FKs Categoría: 1 = Regular, 2 = eSports, 3 = Streaming VIP)
INSERT INTO Estaciones (tipo_estacion, codigo_pc, id_categoria, estado_actual) 
VALUES 
('Módulo 01', 'PC-001', 1, 'Disponible'),
('Módulo 02', 'PC-002', 1, 'Ocupada'),
('Módulo 03', 'PC-003', 2, 'Disponible'),
('Módulo 04', 'PC-004', 2, 'Mantenimiento'),
('Módulo 05', 'PC-005', 3, 'Disponible')
GO

PRINT '¡Base de datos Cyber Reinoso desplegada con éxito!';

--USE master; -- Cambia el contexto fuera de la base de datos que vas a eliminar
--GO

--ALTER DATABASE CyberReinoso SET SINGLE_USER WITH ROLLBACK IMMEDIATE; 
--GO

--DROP DATABASE CyberReinoso; -- Elimina permanentemente la base de datos y sus archivos
--GO