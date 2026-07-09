# Cyber Reinoso - Smart Center Dashboard

Un sistema integral de escritorio (Desktop App) desarrollado en Python para la gestión operativa, financiera y de inventario de un Lan Center / Cibercafé. El proyecto aplica principios sólidos de Programación Orientada a Objetos (POO), arquitectura modular (Clean Architecture) y el patrón DAO para garantizar un bajo acoplamiento con la base de datos relacional.

## Características Principales

* **Dashboard de Monitoreo en Tiempo Real:** Panel de control interactivo (UI) que mapea visualmente la distribución del Lan Center. Incluye cronómetros dinámicos, cambio de estados por color (Disponible, Ocupada, Mantenimiento) y tooltips con especificaciones de hardware.
* **Billetera Virtual y Cortes Automáticos:** Sistema de prepago donde los clientes recargan saldo. El sistema calcula en tiempo real el consumo y realiza el corte automático de la sesión cuando los fondos del jugador se agotan.
* **Motor de Fidelización (VIP System):** Algoritmo de progresión automatizado. Los usuarios acumulan minutos de juego para subir de rango (Bronce, Plata, Oro, Global VIP), lo que desbloquea automáticamente porcentajes de descuento en sus sesiones.
* **Punto de Venta Integrado (Kiosco POS):** Módulo de venta de snacks y bebidas con carrito de compras interactivo, validación de inventario/stock en tiempo real y facturación conjunta.
* **Contabilidad y Auditoría de Caja:** Reporte diario de caja unificado que suma los ingresos por alquiler de hardware y las ventas del kiosco. Todas las transacciones económicas quedan selladas con el ID del empleado que inició el turno para evitar fugas de dinero.
* **Gestión Modular de Hardware:** Separación lógica entre los módulos físicos (las mesas) y los componentes (PCs, monitores, periféricos), permitiendo intercambiar equipos averiados sin perder la continuidad del negocio ni alterar los registros contables.

## Arquitectura y Tecnologías

El sistema está diseñado bajo el paradigma de Programación Orientada a Objetos (POO), aplicando principios de Clean Code, Programación Defensiva y el patrón de diseño DAO (Data Access Object) para la persistencia.

* **Lógica de Negocio (Backend):** * **Python 3:** Lenguaje principal del ecosistema.
  * **POO Avanzada:** Implementación estricta de Abstracción (uso de `ABC` y `@abstractmethod`), Herencia (Subclases especializadas por categoría de PC) y Encapsulamiento (decoradores `@property` para proteger variables sensibles como saldos).
  * **Manejo de Errores:** Creación de Excepciones Personalizadas (ej. `SaldoInsuficienteError`) y sobrecarga de operadores mágicos (ej. `__add__` y `__str__`) para operaciones matemáticas limpias entre objetos.
* **Interfaz Gráfica (Frontend):** * **Tkinter & ttk:** Construcción de una interfaz modular, responsive y estructurada en clases independientes (`AppCyberReinoso`, `PanelMapa`, `VentanaTienda`).
  * **Pillow (PIL):** Procesamiento de imágenes en memoria para el catálogo de productos y las tarjetas de las estaciones, implementando un sistema de *fallback* para cargar imágenes genéricas si la foto específica del hardware no está disponible.
* **Persistencia y Base de Datos:** * **Microsoft SQL Server:** Motor relacional de base de datos. Arquitectura altamente normalizada para facturación (Cabecera y Detalle) y control de personal.
  * **pyodbc:** Librería puente para la ejecución de consultas SQL desde Python.
  * **Transacciones ACID:** Uso de bloques atómicos con `COMMIT` y `ROLLBACK` durante el procesamiento masivo de ventas de kiosco, garantizando la integridad de los datos financieros ante posibles caídas de red o fallos de ejecución.

## Estructura del Proyecto
El sistema aplica principios de Clean Architecture y separación de responsabilidades, dividiendo el monolito inicial en módulos independientes:

```text
cyber-reinoso/
├── assets/                      # Iconos y fotografías del hardware dinámico
├── modulos_ui/
│   ├── panel_kiosco.py          # Módulo POS y transacciones de tienda
│   ├── panel_mapa.py            # Renderizado de grilla y tooltips de hardware
│   ├── panel_usuario.py         # Tarjeta de cliente y fidelización
│   ├── ventana_login.py         # Control de acceso y bloqueo de seguridad
│   └── ventanas_emergentes.py   # Recargas, registros y cierres de caja
├── conexion.py                  # Data Access Object (Transacciones SQL)
├── modelos.py                   # Lógica de negocio (Usuario, Sesion, Estacion)
└── main.py                      # Orquestador principal de la aplicación
```

* **`main.py`:** Actúa como el Orquestador principal. Inicializa el ciclo de Tkinter, maneja el estado de las sesiones concurrentes y el reloj (Kill Switch).
* **`modelos.py`:** Capa de Negocio. Contiene las entidades (Usuario, Sesion) y aplica polimorfismo para las tarifas de `EstacionTrabajo`.
* **`conexion.py`:** Capa de Datos (Patrón DAO). Centraliza y encapsula todas las transacciones hacia SQL Server.
* **`modulos_ui/`:** Componentes visuales desacoplados de la lógica central:
  * `panel_kiosco.py`: Widget personalizado (`LabelFrame`) autónomo que gestiona su propio inventario y lógica de ventas.
  * `ventanas_emergentes.py`: Controladores de las ventanas modales (`Toplevel`) para registro de usuarios, recargas y reportes financieros.
* **`estructura_db.sql`:** Scripts de creación de infraestructura relacional y datos semilla.

## Stack Tecnológico y Arquitectura
* **Lenguaje:** Python 3.x
* **Interfaz Gráfica:** Tkinter (GUI nativa)
* **Base de Datos:** Microsoft SQL Server (vía `pyodbc`)
* **Arquitectura:** Modelo DAO y Modularización de UI.

## Instalación y Configuración

1. **Obtener el código fuente:**
   
   * **Opción A:** Clonar el repositorio vía Git:
     ```bash
     git clone https://github.com/Itsfavi0/cyber-reinoso.git
     cd cyber-reinoso
     ```
   * **Opción B (Descarga directa):** Si no tienes Git instalado, puedes descargar el código fuente en formato comprimido. 
     Haz clic en el botón verde **"<> Code"** en la parte superior derecha de este repositorio y selecciona **"Download ZIP"**. Luego, extrae el archivo y abre la carpeta desde tu terminal.

Para ejecutar este proyecto en tu máquina local, necesitas:
2. Instalar el driver de conexión a SQL Server para Python:
   ```bash
   pip install pyodbc
   pip install Pillow
   ```

3. Configurar la Base de Datos:

Abre SSMS y ejecuta el script `estructura_db.sql`
Verifica que la cadena de conexión en conexion.py coincida con tu instancia local:

```text
self.connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=CyberReinoso;"
    "Trusted_Connection=yes;"
)
```
4. Ejecutar el sistema:
    ```bash
    python main.py
    ```

## Credenciales de Acceso (Entorno de Desarrollo)
Para iniciar sesión en el entorno de pruebas, utiliza los siguientes usuarios preconfigurados:

```text
Administrador: admin | Clave: 1234
Cajero: renzo_caja | Clave: 0000
```

## 👨‍💻 Autor
Favio Brañez - Desarrollo y Arquitectura de Software