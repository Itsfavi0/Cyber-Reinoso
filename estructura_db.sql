-- =========================================================
-- CREACION DE LA BASE DE DATOS
-- =========================================================
IF DB_ID('CyberReinoso') IS NULL
BEGIN
    CREATE DATABASE CyberReinoso
END
GO

-- Usamos base de datos correcta
USE CyberReinoso
GO

-- =========================================================
-- CREACION DE LAS TABLAS
-- =========================================================

CREATE TABLE Empleados (
    id_empleado INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    clave VARCHAR(50) NOT NULL,
    rol VARCHAR(50) NOT NULL
)
GO

CREATE TABLE Usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    alias_gamer VARCHAR(50) UNIQUE NOT NULL,
    rango_cuenta VARCHAR(20) NOT NULL DEFAULT 'Bronce',
    saldo_billetera DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    minutos_acumulados INT NOT NULL DEFAULT 0
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
    codigo_pc VARCHAR(20) PRIMARY KEY, -- Ej: 'PC-01'
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
    tipo_estacion VARCHAR(50) NOT NULL, -- Ej: 'Módulo 01'
    codigo_pc VARCHAR(20) NULL,
    categoria VARCHAR(50) NOT NULL, -- 'Regular', 'eSports', 'Streaming VIP'
    estado_actual VARCHAR(20) NOT NULL DEFAULT 'Disponible',

    FOREIGN KEY (codigo_pc) REFERENCES Computadoras(codigo_pc)
)
GO

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
);

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
-- INSERCIÓN DE DATOS DE PRUEBA
-- =========================================================

-- Personal
INSERT INTO Empleados (nombre, usuario, clave, rol) VALUES 
('Favio', 'admin', '1234', 'Administrador'),
('Renzo', 'renzo_caja', '0000', 'Cajero Junior');

-- Gamers (Con diferentes rangos para probar el sistema)
INSERT INTO Usuarios (alias_gamer, rango_cuenta, saldo_billetera, minutos_acumulados) VALUES 
('Maximus_27', 'Bronce', 15.50, 120),
('Jojo', 'Plata', 25.00, 1500),
('flamed4rk', 'Oro', 40.00, 4500),
('Dark', 'Global VIP', 120.00, 7200),
('Wacho', 'Bronce', 5.00, 45),
('mzmiguelxd', 'Plata', 30.00, 2100),
('RENZX', 'Global VIP', 80.00, 6500);

-- Inventario de Kiosco
INSERT INTO Productos (nombre_producto, precio, stock) VALUES 
('Inca Kola Personal', 3.50, 40),
('Cuates Picantes', 1.50, 50),
('Gaseosa Gordita', 2.50, 30),
('Pizza Personal', 8.00, 15),
('Galletas', 2.00, 20);

-- Hardware Físico
INSERT INTO Computadoras (codigo_pc, procesador, tarjeta_grafica, monitor, mouse) VALUES 
('PC-001', 'AMD Ryzen 5 8600G', 'Gráficos Integrados Radeon', 'MSI PRO MP243L E14 100Hz FHD', 'Genérico'),
('PC-002', 'AMD Ryzen 5 8600G', 'Gráficos Integrados Radeon', 'MSI PRO MP243L E14 100Hz FHD', 'Genérico'),
('PC-003', 'Intel Core i5', 'RTX 3060', 'ASUS TUF VG249Q5A 165Hz FHD', 'Ajazz AJ179 Apex'),
('PC-004', 'Intel Core i7', 'RTX 4060 Ti', 'LG UltraGear 27G523B-B 200Hz FHD', 'Ajazz AJ179 Apex'),
('PC-005', 'AMD Ryzen 9', 'RTX 4090', 'Samsung Odyssey OLED G8 250Hz 4K', 'Logitech G Pro Superlight');

-- Asignación a los Módulos (Espacio Lógico)
INSERT INTO Estaciones (tipo_estacion, codigo_pc, categoria, estado_actual) VALUES 
('Módulo 01', 'PC-001', 'Regular', 'Disponible'),
('Módulo 02', 'PC-002', 'Regular', 'Ocupada'),
('Módulo 03', 'PC-003', 'eSports', 'Disponible'),
('Módulo 04', 'PC-004', 'eSports', 'Mantenimiento'),
('Módulo 05', 'PC-005', 'Streaming VIP', 'Disponible');
GO

PRINT '¡Base de datos Cyber Reinoso desplegada con éxito!';