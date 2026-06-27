# Cyber Reinoso - Smart Center Dashboard

Sistema de gestión para Lan Centers y cibercafés, diseñado con Arquitectura Orientada a Objetos y persistencia de datos relacional. Este proyecto maneja la asignación de estaciones de trabajo, control de tiempos y facturación en tiempo real.

## Características (v1.1)
* **Gestión de Estaciones:** Renderizado dinámico del mapa de computadoras (PCs Regulares y VIP) desde la base de datos.
* **Control de Sesiones:** Asignación y liberación de equipos con cambio de estado visual y actualización en base de datos.
* **Sistema de Cobros:** Cálculo automático de tarifas basado en el tiempo de uso y categoría de la PC.
* **Billetera Digital Persistente:** Descuento en vivo del saldo del usuario al cerrar la sesión, guardando el capital real en SQL Server.

## Tecnologías Utilizadas
* **Lenguaje:** Python 3
* **Interfaz Gráfica:** Tkinter
* **Base de Datos:** SQL Server (pyodbc)
* **Paradigma:** Programación Orientada a Objetos (Herencia, Polimorfismo, Encapsulamiento) y Patrón DAO.

## Instalación y Configuración
Para ejecutar este proyecto en tu máquina local, necesitas:
1. Instalar el driver de conexión a SQL Server para Python:
   ```bash
   pip install pyodbc
2. Ejecutar el script 01_crear_esquema_mvp.sql en tu gestor de SQL Server para crear la base de datos CyberReinoso y sus tablas.
3. Asegurarte de insertar los datos semilla (PCs y usuarios iniciales) mediante consultas SQL.
4. Ejecutar el sistema:
    python main.py

## Estructura del Proyecto
* **main.py:** Capa de presentación (Frontend interactivo Tkinter).
* **modelos.py:** Capa de negocio (Lógica, entidades y cálculos matemáticos).
* **conexion.py:** Capa de datos (Gestor DAO para comunicación con SQL Server).
* **01_crear_esquema_mvp.sql:** Scripts de creación de infraestructura relacional.