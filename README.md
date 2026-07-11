# 🎮 Cyber Reinoso - Smart Center Dashboard

Un sistema empresarial integral (ERP/POS) de misión crítica, diseñado específicamente para la administración moderna, monitoreo en tiempo real y facturación de Lan Centers y arenas de eSports. Desarrollado en Python bajo el paradigma de Programación Orientada a Objetos (POO) y respaldado por una base de datos relacional altamente normalizada en SQL Server.

## Características Principales

* **🗺️ Dashboard de Monitoreo Responsivo (UI/UX):** Panel visual interactivo construido sobre un lienzo dinámico (`Canvas`) con barras de desplazamiento (`Scrollbar`), capaz de adaptarse sin cortes visuales a pantallas de laptops o monitores amplios. Mapea en tiempo real el estado de cada estación mediante codificación por color (Disponible, Ocupada, Mantenimiento) y maneja de forma elegante los módulos vacíos o sin hardware asignado.
* **⏱️ Billetera Virtual y Cortes Automáticos:** Sistema de cobro prepago con cálculo micro-transaccional. Los cronómetros nativos en tipografía monoespaciada auditan el consumo por minuto; si el saldo del cliente se agota, el motor del sistema ejecuta un corte automático de la sesión y libera la máquina de inmediato.
* **💎 Motor de Fidelización Normalizado (VIP Engine):** Algoritmo de progresión de rangos (*Bronce, Plata, Oro, Diamante*) impulsado por minutos acumulados. Gracias a la estructura relacional, los porcentajes de descuento se consultan dinámicamente desde catálogos maestros, reflejando el ahorro real del cliente directamente en su boleta final.
* **🛒 Kiosco POS Transaccional:** Módulo de punto de venta para snacks y bebidas con carrito de compras interactivo. Opera bajo una estricta arquitectura de facturación *Cabecera-Detalle* con descuento de stock en tiempo real y protección transaccional.
* **🔧 Gestión de Infraestructura e ITSM:** Separación lógica entre el módulo físico (la mesa) y el hardware (la computadora). El módulo de administración permite realizar actualizaciones parciales de componentes (CPU/Monitor) y eliminaciones seguras sin destruir la continuidad de las estaciones en el mapa.
* **🔒 Control de Acceso y Branding:** Sistema de seguridad con ventana de inicio de sesión (*Login*) en formato modal flotante, bloqueo emergente, validación de roles (*Administrador/Cajero*), íconos nativos (`.ico`) y renderizado de identidad visual corporativa.

## Arquitectura y Tecnologías

El sistema está diseñado bajo el paradigma de Programación Orientada a Objetos (POO), aplicando principios de Clean Code, Programación Defensiva y el patrón de diseño DAO (Data Access Object) para la persistencia.

### Backend y Lógica de Negocio (Python 3)
* **POO Avanzada:** Uso de Abstracción (clases base abstractas `ABC` y `@abstractmethod`) y Polimorfismo en las subclases de hardware (`PC_Regular`, `PC_eSports`, `PC_StreamingVIP`) para el cálculo diferenciado de tarifas de alquiler por hora.
* **Encapsulamiento:** Protección de datos financieros y de saldo mediante decoradores `@property`.
* **Manejo de Errores y Seguridad:** Creación de excepciones personalizadas (ej. `SaldoInsuficienteError`) y sobrecarga de operadores mágicos (`__add__`, `__str__`). Protección estricta de usuarios del sistema (ej. *Invitado_General ID 1*) contra borrados accidentales para evitar caídas en la inicialización.

### Frontend y Presentación
* **Tkinter & ttk:** Diseño modular estructurado en clases independientes (`AppCyberReinoso`, `PanelMapa`, `PanelUsuario`, `PanelAdministrador`, `VentanaLogin`) con tema oscuro nativo (*Dark Mode*).
* **Pillow (PIL):** Procesamiento de imágenes en memoria RAM para el catálogo del kiosco y hardware del mapa. Incorpora un sistema de **Fallback Dinámico**: si la fotografía específica de una PC no existe en `assets/`, el sistema procesa automáticamente una imagen genérica basada en su categoría, evitando quiebres en la interfaz.

### Persistencia y Base de Datos Relacional (Microsoft SQL Server)
* **Tercera Forma Normal (3FN):** Estructura refactorizada y libre de redundancias. Uso de tablas maestras de catálogo (`Roles`, `RangosCuenta`, `CategoriasEstacion`) que alimentan a las tablas transaccionales mediante llaves foráneas (`FK`) e índices optimizados.
* **Integridad Referencial Híbrida:** * *Borrado en Cascada (`ON DELETE CASCADE`):* Implementado en tablas de detalle como `DetalleVentas` para la limpieza automática de registros transaccionales dependientes.
  * *Desvinculación Lógica (`SET NULL`):* Implementado en el hardware; al eliminar una computadora física de la BD, su estación lógica queda en estado `NULL` ("Módulo Vacío") en lugar de ser eliminada, preservando el mapa física del local.
* **SQL Dinámico y Subconsultas:** Consultas parametrizadas al vuelo en `conexion.py` para realizar `UPDATES` parciales de hardware sin sobrescribir datos existentes, y subconsultas en línea para traducir nombres de rangos a llaves foráneas en la lógica de fidelización.
* **Transacciones ACID:** Bloques de ejecución atómicos utilizando `COMMIT` y `ROLLBACK` en las ventas del kiosco. Si una operación de venta falla a mitad de proceso, la base de datos revierte automáticamente los cobros y el inventario para evitar descuadres contables.

## Stack Tecnológico y Arquitectura

* **Lenguaje:** Python 3.x
* **Interfaz Gráfica:** Tkinter (GUI nativa)
* **Base de Datos:** Microsoft SQL Server (vía `pyodbc`)
* **Arquitectura:** Modelo DAO y Modularización de UI.

## 📋 Requisitos Previos

Para desplegar el sistema en un entorno local o de producción, se requiere:
* **Python 3.10** o superior.
* **Microsoft SQL Server** (2019/2022) y **SQL Server Management Studio (SSMS)**.
* **ODBC Driver 17 for SQL Server** instalado en el sistema operativo.

### Librerías de Python
Ejecuta el siguiente comando para instalar las dependencias necesarias:
```bash
pip install pyodbc Pillow
```

## Instalación y Configuración

1. **Obtener el código fuente:**
   
   * **Opción A:** Clonar el repositorio vía Git:
     ```bash
     git clone https://github.com/Itsfavi0/cyber-reinoso.git
     cd cyber-reinoso
     ```
   * **Opción B (Descarga directa):** Si no tienes Git instalado, puedes descargar el código fuente en formato comprimido. 
     Haz clic en el botón verde **"<> Code"** en la parte superior derecha de este repositorio y selecciona **"Download ZIP"**. Luego, extrae el archivo y abre la carpeta desde tu terminal.

2. Desplegar la Base de Datos:

  * Abre SQL Server Management Studio (SSMS).
  * Ejecuta el script `estructura_db.sql` ubicado en el repositorio para generar la arquitectura relacional normalizada y poblar los datos de prueba.

3. Abre SSMS y ejecuta el script `estructura_db.sql`
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

  Lanza la aplicación principal desde tu terminal o IDE:

    ```bash
    python main.py
    ```

## 📁 Estructura del Proyecto
El sistema aplica principios de Clean Architecture y separación de responsabilidades, dividiendo el monolito inicial en módulos independientes:

```text
cyber-reinoso/
├── assets/                    # Identidad visual (.ico, .png), logotipos y fotos de hardware
├── modulos_ui/                # Componentes modulares de la interfaz gráfica
│   ├── panel_kiosco.py        # POS, carrito de compras y control de stock
│   ├── panel_mapa.py          # Renderizado responsivo de grilla y tooltips de hardware
│   ├── panel_usuario.py       # Tarjeta de cliente, saldos y fidelización VIP
│   ├── panel_administrador.py # ITSM, CRUD de hardware y gestión de usuarios
│   └── ventana_login.py       # Modal flotante de seguridad y autenticación
├── conexion.py                # Data Access Object (DAO), JOINs 3FN y transacciones ACID
├── modelos.py                 # Clases abstractas (POO), reglas de negocio y excepciones
├── estructura_db.sql          # Script de despliegue SQL Server (Tablas 3FN y Seed Data)
└── main.py                    # Orquestador principal y bucle de cronómetros
```

El proyecto sigue una arquitectura limpia y desacoplada en capas, dividiendo de forma estricta la interfaz gráfica, la lógica de negocio y la persistencia de datos:

* **`main.py`:** Actúa como el Orquestador principal de la aplicación. Inicializa el ciclo de Tkinter, gestiona el estado de las sesiones concurrentes de los gamers y controla el hilo del reloj global para los cortes automáticos de tiempo.
* **`modelos.py`:** Capa de Negocio (Domain Model). Contiene las entidades puras de la aplicación (`Usuario`, `Sesion`) y aplica polimorfismo para calcular las tarifas dinámicas según las subclases especializadas de `EstacionTrabajo`.
* **`conexion.py`:** Capa de Datos (Patrón DAO). Centraliza, encapsula y blinda todas las transacciones SQL hacia Microsoft SQL Server, abstrayendo los `INNER JOINs` y subconsultas de la lógica de presentación.
* **`estructura_db.sql`:** Scripts relacionales normalizados en Tercera Forma Normal (3FN). Contiene las restricciones de integridad, llaves primarias/foráneas, automatización transaccional y los datos semilla esenciales.
* **`assets/`:** Repositorio centralizado de recursos estáticos del sistema. Almacena la identidad visual corporativa de la marca (`logo.ico`, `logo_cyber.png`) y el catálogo fotográfico dinámico para el hardware del mapa de PCs.
* **`modulos_ui/`:** Componentes visuales y pantallas del frontend, completamente desacoplados de la lógica central del backend:
  * `panel_mapa.py`: Renderizado responsivo de la grilla de estaciones de juego. Implementa un canvas scrolleable y lógica tolerante a fallos para módulos vacíos (hardware desvinculado).
  * `panel_usuario.py`: Panel lateral derecho que gestiona la información en tiempo real del gamer activo, saldos de billetera y progresión de rangos de fidelización.
  * `panel_kiosco.py`: Widget personalizado (`LabelFrame`) autónomo que opera como punto de venta (POS), gestionando su propio inventario de snacks, stock y pasarela del carrito de compras.
  * `panel_administrador.py`: Módulo de gestión interna (ITSM) que centraliza las operaciones avanzadas del CRUD para la actualización dinámica de hardware físico y eliminación segura de registros.
  * `ventana_login.py`: Pantalla de inicio de sesión de seguridad en formato modal flotante (`Toplevel`), encargada de la autenticación de credenciales y asignación de roles operativos.
  * `ventanas_emergentes.py`: Controladores modales auxiliares para el registro rápido de nuevos usuarios, recargas de saldo y visualización de reportes financieros de caja.

## Credenciales de Acceso (Entorno de Desarrollo)
Para iniciar sesión en el entorno de pruebas, utiliza los siguientes usuarios preconfigurados:

```text
Administrador: admin | Clave: 1234
Cajero: renzo_caja | Clave: 0000
```

## 👨‍💻 Autor
Favio Brañez - Desarrollo y Arquitectura de Software
