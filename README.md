# 🎮 Cyber Reinoso - Smart Center Dashboard

![Status](https://img.shields.io/badge/Status-Under%20Development-FFA000?style=for-the-badge)
![Python Version](https://img.shields.io/badge/Python-3.10%2B-1565C0?style=for-the-badge&logo=python&logoColor=white)
![SQL Server](https://img.shields.io/badge/Database-SQL%20Server%203FN-CC292B?style=for-the-badge&logo=microsoftsqlserver&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-MVC%20%7C%20DAO%20%7C%20Mediator-8E24AA?style=for-the-badge)

**Cyber Reinoso** es un sistema empresarial de administración moderna, monitoreo en tiempo real, control de inventario y facturación (POS) diseñado específicamente para Lan Centers y arenas de eSports.

El software está construido bajo el paradigma de **Programación Orientada a Objetos (POO)** y aplica principios estrictos de **Clean Code**, **Diseño Guiado por el Dominio (DDD)** y una base de datos relacional altamente normalizada en **Microsoft SQL Server**.

---

## ✨ Características Principales (UI/UX & Negocio)

* **🗺️ Dashboard de Monitoreo Responsivo:** Panel visual interactivo construido sobre un lienzo dinámico (`Canvas`) con barras de desplazamiento (`Scrollbar`). Mapea en tiempo real el estado operativo de cada estación mediante codificación por color (*Disponible, Ocupada, Mantenimiento*) y gestiona con elegancia los módulos vacíos o sin hardware asignado.
* **⏱️ Billetera Virtual y Kill Switch Automático:** Sistema prepago con auditoría micro-transaccional en tiempo real. Cronómetros nativos calculan el consumo minuto a minuto; si el monedero del cliente se agota (`S/ 0.00`), el motor ejecuta un corte de sesión inmediato, liberando la máquina de forma autónoma.
* **💎 Motor de Fidelización Normalizado (VIP Engine):** Algoritmo de progresión de rangos (*Bronce, Plata, Oro, Diamante*) impulsado por la acumulación histórica de tiempo de juego. Los porcentajes de descuento se calculan proporcionalmente reflejándose en el ahorro real del cliente dentro de su boleta de consumo.
* **🛒 Kiosco POS Transaccional:** Módulo de punto de venta para snacks y bebidas con carrito de compras interactivo (*Card-Based*). Opera bajo una estricta arquitectura de facturación *Cabecera-Detalle*, con descuento de stock en caliente y protección transaccional.
* **🔒 Gatekeeper de Seguridad y Branding:** Autenticación de usuarios mediante ventana modal flotante (`Toplevel`), bloqueo contra evasión de cierre (`grab_set`), validación por roles (*Administrador / Cajero*) y renderizado dinámico de identidad visual corporativa vía `Pillow (PIL)`.

---

## 🚀 Correcciones y Optimizaciones Recientes (Julio 2026)

Se han implementado mejoras críticas de consistencia, robustez y estabilidad en el sistema:

* **⚡ Cierre de Sesión Atómico (ACID):** Se unificó la actualización del progreso del usuario (minutos acumulados y rango de cuenta) junto con el sellado de la sesión en un único bloque de transacción atómica (`finalizar_sesion_transaccional` en `conexion.py`), garantizando la integridad de datos contables y de fidelización ante cualquier interrupción o caída de red.
* **🛍️ Consistencia Financiera en Kiosco:** Se reestructuró el orquestador de pagos de snacks en el POS para validar y persistir la compra en SQL Server *antes* de impactar las finanzas en la memoria RAM de la aplicación. Si el commit de la base de datos falla, el saldo del gamer se mantiene intacto, eliminando la posibilidad de discrepancias de saldo.
* **⏱️ Tarifación VIP Dinámica:** Se corrigió el bug de cálculo en el motor del Kill Switch (`actualizar_cronometros` en `main.py`). Ahora proyecta y evalúa correctamente el costo del próximo minuto aplicando el porcentaje de descuento VIP según el rango del cliente, previniendo desconexiones forzadas prematuras.
* **🚫 Control de Acceso y Validaciones de Estado:** Se corrigieron los callbacks de los botones en [panel_usuario.py](file:///home/favio/Proyectos/cyber-reinoso/modulos_ui/panel_usuario.py) (`command=self.abrir_recarga` y `command=self.abrir_tienda`) para invocar adecuadamente las validaciones de acceso. Ahora, si un usuario está inhabilitado (`estado = 0`), el sistema bloquea preventivamente las opciones de recarga y compras del kiosco mostrando una alerta de "Acción denegada". Además, se ajustó la reconstrucción de sesiones activas en [main.py](file:///home/favio/Proyectos/cyber-reinoso/main.py) tras caídas de energía para preservar correctamente el valor del bit `estado` recuperado de la base de datos en lugar de asumir por defecto el valor activo (1).
* **🔔 Alertas de Corte No Bloqueantes:** Se reemplazó el uso de diálogos modales restrictivos por `AlertaCorteAutomatico` en `ventanas_emergentes.py`, el cual no captura de forma absoluta el foco del mouse y teclado (`grab_set` desactivado). Esto evita que el ciclo de eventos asíncrono y los contadores de tiempo de las demás computadoras activas se congelen al dispararse un corte de energía o saldo.

---

## 🏛️ Arquitectura de Software y Patrones de Diseño

El código fuente implementa patrones de diseño esenciales para garantizar el bajo acoplamiento:

* **Patrón Mediador (Mediator):** El archivo `main.py` actúa como orquestador centralizador (`AppCyberReinoso`), coordinando la comunicación asíncrona entre paneles (`PanelMapa`, `PanelUsuario`, `PanelAdministrador`) para garantizar un **bajo acoplamiento (Loose Coupling)**.
* **Patrón DAO (Data Access Object):** La persistencia está encapsulada en `DBManager` (`conexion.py`). La capa visual desconoce por completo la sintaxis SQL, consumiendo únicamente métodos de servicio limpios y transaccionales.
* **Polimorfismo en Tiempo Real:** El cálculo de tarifas por minuto varía dinámicamente en RAM según la subclase instanciada (`PC_Regular`, `PC_eSports`, `PC_StreamingVIP`), eliminando sentencias condicionales redundantes.
* **Diseño Guiado por el Dominio (DDD):** Interfaz semántica enfocada en transiciones de estado e infraestructura (*"🛠️ Enviar a Mantenimiento"*, *"🔄 Alternar Estado Operativo"*) en lugar de comandos genéricos destructivos.

---

## ⚙️ Innovaciones Técnicas y Seguridad (Evolución del Backend)

### 🛡️ Concurrencia Asíncrona sin Threads
* **Motor de Eventos No Bloqueante:** Gestión del tiempo impulsada por el bucle de eventos nativo de Tkinter (`self.after(1000)`). Esto permite auditar más de 12 sesiones activas en paralelo, verificar stocks en el POS y refrescar indicadores visuales sin congelar la interfaz ni generar interbloqueos de memoria RAM.
* **Tolerancia a Fallos (Fault Tolerance):** Sistema de recuperación ante caídas eléctricas o cierres forzados, preservando el estado transaccional en la base de datos.

### 💾 Persistencia Relacional Avanzada (3FN, ACID & Toggles ITSM)
* **Transacciones ACID y Bloques ROLLBACK:** Operaciones críticas como la facturación por lote en el Kiosco y el alta simultánea de infraestructura ejecutan múltiples sentencias `INSERT` en un solo bloque atómico. Si una consulta falla (ej. código duplicado o error de restricción), la base de datos revierte automáticamente toda la transacción (`ROLLBACK`), evitando descuadres contables o registros huérfanos.
* **Borrado Lógico (Soft Delete) y Preservación de Estado:** Prohibición de la instrucción `DELETE` en transacciones comerciales e inventario. Se implementó el atributo semántico `estado` en usuarios y el retiro a `Mantenimiento` en hardware, ocultando elementos inhabilitados en el frontend mientras se custodia el 100% de la metadata en la base de datos para auditorías contables.
* **Toggles ITSM Bi-direccionales:** Los botones de control ejecutan sentencias SQL optimizadas con `CASE WHEN` (`SET activa = CASE WHEN activa = 1 THEN 0 ELSE 1 END`). La evaluación de alternancia se realiza atómicamente dentro del motor SQL Server, eliminando la latencia de red y previniendo condiciones de carrera (*Race Conditions*).
* **Autogeneración Alfanumérica de IDs:** Algoritmo en la capa DAO que consulta mediante subcadenas matemáticas (`CAST(SUBSTRING(...) AS INT)`) el código de hardware más alto registrado, le suma una unidad y formatea la nueva cadena con ceros a la izquierda (`PC-013`) para inyectarla automáticamente en el formulario en modo `readonly`.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología / Librería | Descripción |
| :--- | :--- | :--- |
| **Lenguaje Core** | Python 3.10+ | Lógica de negocio, POO avanzada y manejo de eventos. |
| **Interfaz Gráfica** | Tkinter & `ttk` | Renderizado nativo de ventanas modales, Canvas y grillas Dark Mode. |
| **Base de Datos** | Microsoft SQL Server | Motor relacional de misión crítica normalizado en 3FN. |
| **Conectividad DB** | `pyodbc` (ODBC Driver 17/18) | Puente de comunicación y ejecución de consultas parametrizadas. |
| **Procesamiento de Assets** | `Pillow (PIL)` | Carga, redimensionamiento y fallback dinámico de imágenes en RAM. |
| **Generación de Documentos** | `reportlab` | Motor de exportación de reportes de caja e informes de cierre en PDF. |

---

## 📋 Requisitos Previos

Para desplegar el sistema en un entorno local o de producción, se requiere:
* **Python 3.10** o superior.
* **Microsoft SQL Server** (2019/2022) y **SQL Server Management Studio (SSMS)**.
* **ODBC Driver 17 or 18 for SQL Server** instalado en el sistema operativo.

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

El software se divide estructuralmente por capas funcionales:

```text
cyber-reinoso/
│
├── assets/                    # Identidad visual (.ico, .png), logotipos y fotos de hardware
├── modulos_ui/                # Capa de Presentación (Vistas modulares desacopladas)
│   ├── panel_mapa.py          # Renderizado responsivo de grilla y tooltips de hardware
│   ├── panel_usuario.py       # CRM de atención al cliente, monedero y estado de cuenta
│   ├── panel_kiosco.py        # POS transaccional, carrito Card-Based y control de stock
│   ├── panel_administrador.py # ITSM, Toggles de estado, alta de hardware y CRUD
│   ├── ventana_login.py       # Gatekeeper modal de seguridad y autenticación de roles
│   └── ventanas_emergentes.py # Modales para altas rápidas, recargas y reportes financieros
│
├── conexion.py                # Capa DAO (Conexión pyodbc, JOINs 3FN, ACID y Soft Delete)
├── modelos.py                 # Capa de Negocio (Clases POO, Polimorfismo y Excepciones)
├── estructura_db.sql          # Script DDL/DML para SQL Server (Tablas 3FN y Seed Data)
└── main.py                    # Orquestador principal y bucle de cronómetros

El proyecto sigue una arquitectura limpia y desacoplada en capas, dividiendo de forma estricta la interfaz gráfica, la lógica de negocio y la persistencia de datos:

* **`main.py`:** Punto de entrada del sistema. Inicializa el ciclo de eventos de Tkinter, gestiona el estado transaccional de las sesiones y ejecuta la vigilancia del reloj global para los cortes prepago.
* **`modelos.py`:** Contiene las entidades puras del dominio (`Usuario`, `Sesion`) y aplica jerarquía de clases con sobrecarga de operadores mágicos (`__add__`, `__str__`).
* **`conexion.py`:** Encapsula la persistencia SQL, blindando el sistema contra inyecciones y gestionando cursores, `JOINs` condicionales y reversiones automáticas ante errores en tiempo de ejecución.
* **`estructura_db.sql`:** Script relacional autoejecutable. Crea las tablas maestras, índices, restricciones de llave foránea (`FK`) con borrado en cascada para detalles de venta y desvinculación lógica (`SET NULL`) para infraestructura retiradas.
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
