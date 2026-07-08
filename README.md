# Cyber Reinoso - Smart Center Dashboard

Un sistema integral de escritorio (Desktop App) desarrollado en Python para la gestión operativa, financiera y de inventario de un Lan Center / Cibercafé. El proyecto aplica principios sólidos de Programación Orientada a Objetos (POO) y el patrón arquitectónico DAO para garantizar un bajo acoplamiento con la base de datos.

## Características Principales (MVP)

### Módulo de Gestión de PCs y Sesiones
* **Panel Visual de Estado:** Mapeo en tiempo real de las estaciones de trabajo (Disponible, Ocupada, Mantenimiento).
* **Cronómetro en Vivo:** Monitoreo segundo a segundo del tiempo transcurrido en cada máquina usando eventos de Tkinter.
* **Kill Switch Automático (Seguridad):** Sistema de auditoría en segundo plano que calcula la tarifa dinámica por minuto y cierra la sesión de forma automática si el saldo del usuario se agota, liberando la PC y evitando pérdidas financieras.
* **Tarifario Dinámico:** Aplicación de polimorfismo para calcular costos distintos según la categoría de la estación (`PC_Regular`, `PC_VIP`).

### Módulo de Clientes (Gamers)
* **Gestor de Usuarios:** Ventana modal (Toplevel) para registrar nuevos clientes directamente en la base de datos.
* **Billetera Virtual:** Sistema de prepago con capacidad de recargar saldo y validación de saldo mínimo requerido (costo del primer minuto) para iniciar sesión.
* **Selector Dinámico:** Cambio de usuario activo en caja mediante menú desplegable, refrescando la interfaz y el estado de la billetera en tiempo real.

### Módulo de Kiosco e Inventario
* **Renderizado Dinámico:** Los botones de productos se generan automáticamente leyendo el catálogo de SQL Server (Gaseosas, Snacks, etc.).
* **Control de Stock:** Bloqueo visual automático de botones cuando un producto marca "Agotado".
* **Cobro Integrado:** Descuento directo de la billetera virtual del cliente y reducción de stock en la base de datos tras cada venta.

### Módulo Financiero
* **Auditoría de Sesiones:** Registro histórico de cada sesión finalizada con su respectiva hora de inicio, fin y monto exacto cobrado.
* **Cuadre de Caja (Turno):** Generación de reporte en tiempo real que suma los ingresos totales de alquileres de PC del día actual.

## Stack Tecnológico y Arquitectura
* **Lenguaje:** Python 3.x
* **Interfaz Gráfica:** Tkinter (GUI nativa)
* **Base de Datos:** Microsoft SQL Server (vía `pyodbc`)
* **Arquitectura:** Data Access Object (DAO) para la separación entre la lógica de presentación (`main.py`) y el acceso a datos (`conexion.py`).

## Instalación y Configuración

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/cyber-reinoso.git
   ```

Para ejecutar este proyecto en tu máquina local, necesitas:
2. Instalar el driver de conexión a SQL Server para Python:
   ```bash
   pip install pyodbc
   ```

3. Ejecutar el script estructura_db.sql en tu gestor de SQL Server para crear la base de datos CyberReinoso y sus tablas.

4. Asegurarte de insertar los datos semilla (PCs y usuarios iniciales) mediante consultas SQL.

5. Ejecutar el sistema:
    ```bash
    python main.py
    ```

## Estructura del Proyecto
El sistema aplica principios de Clean Architecture y separación de responsabilidades, dividiendo el monolito inicial en módulos independientes:

```text
Cyber-Reinoso/
┣ 📄 main.py
┣ 📄 modelos.py
┣ 📄 conexion.py
┣ 📂 modulos_ui/
┃ ┣ 📄 panel_kiosco.py
┃ ┗ 📄 ventanas_emergentes.py
┗ 🗄️ estructura_db.sql
```

* **`main.py`:** Actúa como el Orquestador principal. Inicializa el ciclo de Tkinter, maneja el estado de las sesiones concurrentes y el reloj (Kill Switch).
* **`modelos.py`:** Capa de Negocio. Contiene las entidades (Usuario, Sesion) y aplica polimorfismo para las tarifas de `EstacionTrabajo`.
* **`conexion.py`:** Capa de Datos (Patrón DAO). Centraliza y encapsula todas las transacciones hacia SQL Server.
* **`modulos_ui/`:** Componentes visuales desacoplados de la lógica central:
  * `panel_kiosco.py`: Widget personalizado (`LabelFrame`) autónomo que gestiona su propio inventario y lógica de ventas.
  * `ventanas_emergentes.py`: Controladores de las ventanas modales (`Toplevel`) para registro de usuarios, recargas y reportes financieros.
* **`estructura_db.sql`:** Scripts de creación de infraestructura relacional y datos semilla.

## 👨‍💻 Autor
Favio Brañez - Desarrollo y Arquitectura de Software