# Cyber Reynoso - Smart Center Dashboard

Sistema de gestión para Lan Centers y cibercafés, diseñado con Arquitectura Orientada a Objetos (POO). Este proyecto maneja la asignación de estaciones de trabajo, control de tiempos y facturación en tiempo real.

## Características (MVP v1.0)
* **Gestión de Estaciones:** Renderizado dinámico del mapa de computadoras (PCs Regulares y VIP).
* **Control de Sesiones:** Asignación y liberación de equipos con cambio de estado visual.
* **Sistema de Cobros:** Cálculo automático de tarifas basado en el tiempo de uso y categoría de la PC.
* **Billetera Digital:** Descuento en vivo del saldo del usuario al cerrar la sesión.

## Tecnologías Utilizadas
* **Lenguaje:** Python 3
* **Interfaz Gráfica:** Tkinter
* **Paradigma:** Programación Orientada a Objetos (Herencia, Polimorfismo, Encapsulamiento)
* **Control de Versiones:** Git & GitHub

## Estructura del Proyecto
* `main.py`: Capa de presentación (Frontend interactivo).
* `modelos.py`: Capa de negocio (Lógica, entidades y cálculos matemáticos).
* `01_crear_esquema_mvp.sql`: Capa de datos (Esquema relacional).