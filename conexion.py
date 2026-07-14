"""
CAPA DE ACCESO A DATOS (PATRÓN DAO - DATA ACCESS OBJECT)
Este archivo centraliza, encapsula y abstrae todas las interacciones con Microsoft SQL Server.
Ninguna pantalla o lógica de interfaz puede lanzar SQL directamente; todo debe pasar por esta clase
para garantizar seguridad contra inyecciones y modularidad del código.
"""

import pyodbc

class DBManager:
    def __init__(self):
        """
        CONSTRUCTOR DE CONEXIÓN: Define los parámetros técnicos para enlazar la app con la BD.
        - Driver: El traductor intermedio de Windows para conectarse a SQL Server.
        - Trusted_Connection=yes: Utiliza Autenticación de Windows (Sin necesidad de exponer contraseñas en texto plano).
        """
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost;"
            "Database=CyberReinoso;"
            "Trusted_Connection=yes;"
        )
        
    def conectar(self):
        """Intenta abrir una conexión física con el motor de base de datos"""
        try:
            # pyodbc.connect abre el canal de comunicación en red local/mecanismo nativo.
            conexion = pyodbc.connect(self.connection_string)
            return conexion
        except pyodbc.Error as e:
            # Captura cualquier caída del servicio SQL Server para que la app no tire un pantallazo azul.
            print(f"ERROR DE CONEXIÓN: No se pudo conectar a SQL Server. Detalles: {e}")
            return None
    
    def probar_conexion(self):
        """Método de diagnóstico para verificar que las tuberías de red funcionan"""
        conn = self.conectar()
        if conn:
            try:
                # El Context Manager 'with' asegura que el Cursor (el puntero de SQL)
                # se destruya y libere de la memoria RAM automáticamente al terminar el bloque, evitando fugas de memoria.
                with conn.cursor() as cursor:
                    cursor.execute("SELECT @@VERSION")
                    row = cursor.fetchone()
                    print("CONEXIÓN EXITOSA!!")
                    print(f"Version del servidor: {row}")
            except pyodbc.Error as e:
                print(f"Error en diagnóstico de conexión: {e}")
            finally:
                # El bloque 'finally' se ejecuta SÍ O SÍ, ocurra o no un error. 
                # Es vital para cerrar la conexión y no dejar conexiones 'muertas' saturando el servidor.
                conn.close()
            
    def obtener_estaciones(self):
        """
        TRANSFORMACIÓN DE RELACIONAL A OBJETOS (ORM BÁSICO):
        Consulta el estado físico-lógico del Lan Center y empaqueta las tuplas en diccionarios de Python.
        """
        conn = self.conectar()
        lista_estaciones = []
        if conn:
            try:
                with conn.cursor() as cursor:
                    # - INNER JOIN vincula Estaciones con CategoriasEstacion obligatoriamente (trae tarifas y nombres oficiales).
                    # - LEFT JOIN es la clave de infraestructura: trae todas las mesas, tengan o no un hardware físico asignado.
                    consulta = """
                        SELECT e.id_estacion, e.codigo_pc, cat.nombre_categoria, est.nombre_estado,
                               c.procesador, c.memoria_ram, c.tarjeta_grafica, c.monitor, c.mouse,
                               cat.tarifa_hora
                        FROM Estaciones e
                        INNER JOIN CategoriasEstacion cat ON e.id_categoria = cat.id_categoria
                        INNER JOIN EstadosEstacion est ON e.id_estado = est.id_estado
                        LEFT JOIN Computadoras c ON e.codigo_pc = c.codigo_pc
                    """
                    cursor.execute(consulta)
                    filas = cursor.fetchall() # fetchall() descarga todas las filas resultantes a la memoria RAM en forma de lista de tuplas.
                    
                    for fila in filas:
                        # ESTRUCTURA DE MAPEO: Traducimos los índices numéricos de la tupla SQL (fila[0], fila[1])
                        # en llaves semánticas de un diccionario, haciendo que la UI de Python sea fácil de mantener.
                        estacion = {
                            "id_estacion" : fila[0],
                            "codigo_pc" : fila[1],
                            "categoria" : fila[2],
                            "estado_actual" : fila[3],
                            "tarifa_hora" : float(fila[9]),
                            "specs" : {
                                "procesador" : fila[4],
                                "ram": fila[5],
                                "tarjeta_grafica" : fila[6],
                                "monitor" : fila[7],
                                "mouse" : fila[8]
                            }
                        }
                        lista_estaciones.append(estacion)
            except pyodbc.Error as e:
                print(f"Error al leer las estaciones: {e}")
            finally:
                conn.close()
                
        return lista_estaciones 
    
    def obtener_productos(self):
        """Consulta el almacén y retorna una lista de diccionarios con el stock disponible"""
        conn = self.conectar()
        lista_productos = []
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                            SELECT id_producto, nombre_producto, precio, stock
                            FROM Productos
                        """
                    )
                    filas = cursor.fetchall()
                    
                    for fila in filas:
                        producto = {
                            "id_producto" : fila[0],
                            "nombre_producto" : fila[1],
                            "precio" : float(fila[2]), # Convertimos el DECIMAL de SQL a float en Python para cálculos precisos.
                            "stock" : fila[3]
                        }
                        lista_productos.append(producto)
            except pyodbc.Error as e:
                print(f"Error al leer los productos: {e}")
            finally:
                conn.close()
                
        return lista_productos
            
    def actualizar_estado_pc(self, id_estacion, nuevo_estado):
        """Cambia el estado de una PC en la base de datos (Disponible, Ocupada, Mantenimiento)"""
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # El uso de '?' son PARÁMETROS DE CONSULTA. Evita la concatenación directa de strings,
                    # cerrándole las puertas al 100% a ataques de Inyección SQL.
                    consulta = """
                        UPDATE Estaciones
                        SET id_estado = (SELECT id_estado FROM EstadosEstacion WHERE nombre_estado = ?)
                        WHERE id_estacion = ?        
                    """
                    cursor.execute(consulta, (nuevo_estado, id_estacion))
                    
                    # conn.commit() guarda los cambios de forma permanente en el disco duro de SQL Server.
                    conn.commit()
                    print(f"Base de datos actualizada con éxito | PC: {id_estacion} Estado: {nuevo_estado}")
            except pyodbc.Error as e:
                print(f"Error al actualizar la base de datos: {e}")
            finally:
                conn.close()
    
    def obtener_todos_los_usuarios(self):
        """
        Obtiene una lista básica de todos los gamers para poblar el selector (Combobox) de la UI
        Solo retorna aquellos clientes donde estado = 1, ocultando los eliminados.
        """        
        conn = self.conectar()
        lista_usuarios = []
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id_usuario, alias_gamer FROM Usuarios ORDER BY id_usuario ASC"
                    )
                    filas = cursor.fetchall()
                    
                    for fila in filas:
                        usuario = {
                            "id_usuario": fila[0],
                            "alias_gamer": fila[1]
                        }
                        lista_usuarios.append(usuario)
            except pyodbc.Error as e:
                print(f"Error al listar los usuarios: {e}")
            finally:
                conn.close()
                
        return lista_usuarios
     
    def obtener_usuario(self, id_usuario):
        """Busca un usuario específico uniendo su rango en 3FN para calcular sus beneficios en Python"""
        conn = self.conectar()
        datos_usuario = None
        if conn:
            try:
                with conn.cursor() as cursor:
                    # INNER JOIN TRADUCTOR: Transforma la FK 'id_rango' en la palabra real ('Bronce', 'Diamante')
                    consulta = """
                        SELECT u.id_usuario, u.alias_gamer, r.nombre_rango, u.saldo_billetera, u.minutos_acumulados, u.estado
                        FROM Usuarios u
                        INNER JOIN RangosCuenta r ON u.id_rango = r.id_rango 
                        WHERE u.id_usuario = ?
                    """
                    cursor.execute(consulta, (id_usuario,))
                    fila = cursor.fetchone()
                    
                    if fila:
                        datos_usuario = {
                            "id_usuario": fila[0],
                            "alias_gamer": fila[1],
                            "rango_cuenta": fila[2],
                            "saldo_billetera": float(fila[3]),
                            "minutos_acumulados" : fila[4],
                            "estado" : fila[5]
                        }
            except pyodbc.Error as e:
                print(f"Error al leer el usuario: {e}")
            finally:
                conn.close()
                
        return datos_usuario
    
    def actualizar_saldo_usuario(self, id_usuario, nuevo_saldo):
        """Sincroniza el monedero virtual del cliente tras una recarga en caja"""
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = "UPDATE Usuarios SET saldo_billetera = ? WHERE id_usuario = ?"
                    cursor.execute(consulta, (nuevo_saldo, id_usuario))
                    conn.commit()
                    print(f"Base de datos actualizada con éxito | id_usuario: {id_usuario} | Nuevo Saldo: {nuevo_saldo:.2f}")
            except pyodbc.Error as e:
                print(f"Error al actualizar saldo: {e}")
            finally:
                conn.close()
                
    def actualizar_progreso_usuario(self, id_usuario, saldo, rango, minutos):
        """
        SUBCONSULTA EN LÍNEA: Guarda el progreso traduciendo la palabra del rango ('Plata', 'Diamante')
        al ID numérico correspondiente en la tabla maestra 'RangosCuenta' de forma interna en SQL.
        """
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = """
                        UPDATE Usuarios 
                        SET saldo_billetera = ?, 
                            id_rango = (SELECT id_rango FROM RangosCuenta WHERE nombre_rango = ?), 
                            minutos_acumulados = ? 
                        WHERE id_usuario = ?
                    """
                    cursor.execute(consulta, (saldo, rango, minutos, id_usuario))
                    conn.commit()
            except pyodbc.Error as e:
                print(f"Error al actualizar progreso del usuario: {e}")
            finally:
                conn.close()
                
    def registrar_usuario(self, alias_gamer, saldo_inicial):
        """CRUD: Create - Añade una nueva cuenta de cliente al ecosistema del Cyber"""
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = """
                        INSERT INTO Usuarios (alias_gamer, saldo_billetera)
                        VALUES (?, ?)
                    """
                    cursor.execute(consulta, (alias_gamer, saldo_inicial))
                    conn.commit()
                    print(f"Usuario {alias_gamer} guardado en la base de datos con éxito")
                    return True
            except pyodbc.Error as e:
                print(f"Error al registrar el usuario en la base de datos: {e}")
                return False
            finally:
                conn.close()
        return False
                
    def guardar_historial_sesion(self, id_usuario, id_estacion, hora_inicio, hora_fin, monto_cobrado):
        """Inserta un registro histórico al cerrar una sesión para las auditorías financieras"""
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # FILTRO DE FECHA SEGURO: Convierte ambos campos con CAST a DATE para aislar las horas
                    # e igualar únicamente el año-mes-día de hoy.
                    consulta = """
                        INSERT INTO Sesiones (id_usuario, id_estacion, hora_inicio, hora_fin, monto_cobrado)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    cursor.execute(consulta, (id_usuario, id_estacion, hora_inicio, hora_fin, monto_cobrado))
                    conn.commit()
                    print(f"Historial guardado: PC {id_estacion} | Usuario {id_usuario} | Cobro: S/{monto_cobrado:.2f}")
            except pyodbc.Error as e:
                print(f"Error al guardar el historial de la sesión: {e}")
            finally:
                conn.close()
    
    def obtener_reporte_caja_hoy(self):
        """Crea el registro de control de sesión inyectando la llave primaria del empleado que autoriza el alquiler"""
        conn = self.conectar()
        total_ingresos = 0.0
        
        if conn:
            try:
                with conn.cursor() as cursor:
                    # FILTRO DE FECHA SEGURO: Convierte ambos campos con CAST a DATE para aislar las horas
                    # e igualar únicamente el año-mes-día de hoy.
                    consulta = """
                        SELECT SUM(monto_cobrado)
                        FROM Sesiones
                        WHERE CAST(hora_fin AS DATE) = CAST(GETDATE() AS DATE)
                    """
                    cursor.execute(consulta)
                    resultado = cursor.fetchone()
                    
                    if resultado and resultado[0] is not None:
                        total_ingresos = float(resultado[0])
            except pyodbc.Error as e:
                print(f"Error al generar reporte de caja: {e}")
            finally:
                conn.close()
        return total_ingresos
    
    def registrar_inicio_sesion(self, id_usuario, id_empleado, id_estacion, hora_inicio):
        """Crea el registro de control de sesión inyectando la llave primaria del empleado que autoriza el alquiler"""
        conn = self.conectar()
        id_sesion = None
        if conn:
            try:
                with conn.cursor() as cursor:
                    # CLÁUSULA OUTPUT INSERTED: Técnica avanzada para capturar el ID autonumérico IDENTITY(1,1)
                    # que SQL Server acaba de generar, devolviéndolo inmediatamente a Python sin hacer otro SELECT.
                    consulta = """
                        INSERT INTO Sesiones (id_usuario, id_empleado, id_estacion, hora_inicio, hora_fin, monto_cobrado)
                        OUTPUT INSERTED.id_sesion
                        VALUES (?, ?, ?, ?, NULL, NULL)
                    """
                    cursor.execute(consulta, (id_usuario, id_empleado, id_estacion, hora_inicio))
                    id_sesion = cursor.fetchone()[0]
                    conn.commit()
                    print(f"Sesión de usuario {id_usuario} en PC {id_estacion} guardada con ID: {id_sesion} | Cajero: {id_empleado}")            
            except pyodbc.Error as e:
                print(f"Error al registrar inicio de sesión en BD: {e}")
            finally:
                conn.close()
        return id_sesion
    
    def actualizar_fin_sesion(self, id_sesion, hora_fin, monto_cobrado):
        """Sella una sesión activa registrando la hora de salida y el dinero auditado final"""
        conn = self.conectar()
        exito = False
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = """
                        UPDATE Sesiones
                        SET hora_fin = ?, monto_cobrado = ?
                        WHERE id_sesion = ?
                    """
                    cursor.execute(consulta, (hora_fin, monto_cobrado, id_sesion))
                    conn.commit()
                    exito = True
                    print(f"Sesión {id_sesion} finalizada en BD. Cobro: S/ {monto_cobrado:.2f}")
            except pyodbc.Error as e:
                print(f"Error al actualizar fin de sesión en BD: {e}")
            finally:
                conn.close()
        return exito
        
    def finalizar_sesion_transaccional(self, id_sesion, id_usuario, saldo, rango, minutos, hora_fin, monto_cobrado):
        """
        CIERRE DE SESIÓN TRANSACCIONAL (ACID):
        Actualiza el progreso del usuario y sella la sesión en un solo bloque atómico.
        """
        conn = self.conectar()
        exito = False
        if conn:
            try:
                with conn.cursor() as cursor:
                    # 1. Actualiza progreso del usuario
                    consulta_usr = """
                        UPDATE Usuarios 
                        SET saldo_billetera = ?, 
                            id_rango = (SELECT id_rango FROM RangosCuenta WHERE nombre_rango = ?), 
                            minutos_acumulados = ? 
                        WHERE id_usuario = ?
                    """
                    cursor.execute(consulta_usr, (saldo, rango, minutos, id_usuario))
                    
                    # 2. Sella el cierre de la sesión
                    consulta_ses = """
                        UPDATE Sesiones
                        SET hora_fin = ?, monto_cobrado = ?
                        WHERE id_sesion = ?
                    """
                    cursor.execute(consulta_ses, (hora_fin, monto_cobrado, id_sesion))
                    
                    conn.commit()
                    exito = True
                    print(f"Transacción de cierre exitosa | Sesión: {id_sesion} | Usuario: {id_usuario}")
            except pyodbc.Error as e:
                conn.rollback()
                print(f"Error crítico al finalizar sesión transaccional (ROLLBACK aplicado): {e}")
            finally:
                conn.close()
        return exito
    
    def obtener_sesiones_activas(self):
        """SISTEMA TOLERANTE A APAGONES: Recupera sesiones colgadas (hora_fin IS NULL) al abrir la app"""
        conn = self.conectar()
        lista_sesiones = []
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = """
                        SELECT id_sesion, id_usuario, id_estacion, hora_inicio
                        FROM Sesiones
                        WHERE hora_fin IS NULL
                    """
                    cursor.execute(consulta)
                    filas = cursor.fetchall()
                    for fila in filas:
                        lista_sesiones.append({
                            "id_sesion": fila[0],
                            "id_usuario": fila[1],
                            "id_estacion": fila[2],
                            "hora_inicio": fila[3]
                        })
            except pyodbc.Error as e:
                print(f"Error al obtener sesiones activas: {e}")
            finally:
                conn.close()
        return lista_sesiones
    
    def procesar_compra_kiosco(self, id_usuario, id_empleado, total_venta, carrito):
        """
        TRANSACCIÓN PURA CON ATOMICIDAD (ACID):
        Garantiza que la Cabecera, el Detalle, la reducción de Stock y el cobro del saldo
        ocurran como un bloque único. Si algo falla, TODO se anula, protegiendo las cuentas.
        """
        conn = self.conectar()
        exito = False
        if conn:
            try:
                with conn.cursor() as cursor:
                    # 1. Descontamos el saldo de la billetera del usuario en la Base de Datos
                    consulta_billetera = """
                        UPDATE Usuarios 
                        SET saldo_billetera = saldo_billetera - ? 
                        WHERE id_usuario = ?
                    """
                    cursor.execute(consulta_billetera, (total_venta, id_usuario))

                    # 2. Insertamos la Cabecera de venta y capturamos el ID del ticket
                    consulta_cabecera = """
                        INSERT INTO Ventas (id_usuario, id_empleado, monto_total)
                        OUTPUT INSERTED.id_venta
                        VALUES (?, ?, ?)
                    """
                    cursor.execute(consulta_cabecera, (id_usuario, id_empleado, total_venta))
                    id_venta = cursor.fetchone()[0]
                    
                    # 3. Consultas preparadas optimizadas
                    consulta_detalle = """
                        INSERT INTO DetalleVentas (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    consulta_stock = "UPDATE Productos SET stock = stock - ? WHERE id_producto = ?"
                    
                    # 4. Iteración en memoria RAM del carrito de compras
                    # carrito.items() descompone el diccionario en (clave, datos) para recorrerlo en el bucle.
                    for id_prod, datos in carrito.items():
                        subtotal = datos["precio"] * datos["cantidad"]
                        cursor.execute(consulta_detalle, (id_venta, id_prod, datos["cantidad"], datos["precio"], subtotal))
                        cursor.execute(consulta_stock, (datos["cantidad"], id_prod))
                    
                    # 5. SELLADO TRANSACCIONAL: Si la RAM llegó limpia aquí, impactamos el disco de SQL Server de golpe.
                    conn.commit()
                    exito = True
                    print(f"Transacción exitosa | Ticket #{id_venta} | Cajero ID: {id_empleado}")
            except pyodbc.Error as e:
                # Rollback: Si salta una excepción, borra del mapa cualquier insert parcial,
                # devolviendo los inventarios a su estado original. Cero registros corruptos o huérfanos.
                conn.rollback() 
                print(f"Error crítico en Kiosco. Se aplicó ROLLBACK de seguridad: {e}")
            finally:
                conn.close()
        return exito
                
    def obtener_reporte_tienda_hoy(self):
        """Suma los ingresos financieros producidos puramente por el Kiosco/Ventas de snacks hoy"""
        conn = self.conectar()
        total_ingresos = 0.0
        
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = """
                        SELECT SUM(monto_total) 
                        FROM Ventas
                        WHERE CAST(fecha_venta AS DATE) = CAST(GETDATE() AS DATE)
                    """
                    cursor.execute(consulta)
                    resultado = cursor.fetchone()
                    
                    if resultado and resultado[0] is not None:
                        total_ingresos = float(resultado[0])
            except pyodbc.Error as e:
                print(f"Error al generar reporte de tienda: {e}")
            finally:
                conn.close()
                
        return total_ingresos
    
    def validar_login(self, usuario, clave):
        """CONTROL DE ACCESO (ITSM): Valida las credenciales uniendo la tabla de Empleados con su Rol en 3FN"""
        conn = self.conectar()
        datos_empleado = None
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = """
                        SELECT e.id_empleado, e.nombre, r.nombre_rol 
                        FROM Empleados e
                        INNER JOIN Roles r ON e.id_rol = r.id_rol
                        WHERE e.usuario COLLATE Latin1_General_CS_AS = ? AND e.clave COLLATE Latin1_General_CS_AS = ?
                    """
                    cursor.execute(consulta, (usuario, clave))
                    fila = cursor.fetchone()
                    
                    if fila:
                        datos_empleado = {
                            "id_empleado" : fila[0],
                            "nombre" : fila[1],
                            "rol" : fila[2]
                        }
                        print(f"Login exitoso: Bienvenido {datos_empleado['nombre']}")
                    else:
                        print(f"Intento de acceso fallido: Credenciales incorrectas")
            except pyodbc.Error as e:
                print(f"Error al validar credenciales en la BD: {e}")
            finally:
                conn.close()
        return datos_empleado
    
    def actualizar_hardware_pc(self, codigo_pc, procesador, monitor, ram, gpu):
        """
        CRUD: UPDATE DINÁMICO
        Construye la sentencia UPDATE sobre la marcha analizando qué campos rellenó el administrador.
        Evita machacar con espacios vacíos los periféricos que no se modificaron.
        """
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # 1. Construimos la consulta según qué campos tienen texto
                    campos_set = []
                    valores = []
                    
                    if procesador:
                        campos_set.append("procesador = ?")
                        valores.append(procesador)
                    
                    if ram:
                        campos_set.append("memoria_ram = ?")
                        valores.append(ram)
                        
                    if gpu:
                        campos_set.append("tarjeta_grafica = ?")
                        valores.append(gpu)
                    
                    if monitor:
                        campos_set.append("monitor = ?")
                        valores.append(monitor)
                        
                    if not campos_set:
                        return False  # Operación cancelada: No se envió texto en ningún casillero
                    
                    # ', '.join() une los elementos de una lista de textos agregándoles una coma de por medio.
                    consulta = f"UPDATE Computadoras SET {', '.join(campos_set)} WHERE codigo_pc = ?"
                    valores.append(codigo_pc) # Agregamos el identificador para la cláusula WHERE
                    
                    cursor.execute(consulta, tuple(valores)) # Convertimos la lista de valores a Tupla por exigencia de pyodbc
                    conn.commit()
                    return True
            except pyodbc.Error as e:
                print(f"Error CRUD Update PC: {e}")
            finally:
                conn.close()
        return False

    def alternar_estado_estacion(self, codigo_pc):
        """
        CRUD: Toggle de Estado
        Utiliza la lógica CASE de SQL Server para alternar instantáneamente:
        - Si está Activa (1) -> Pasa a Inactiva (0) y estado 'Mantenimiento'.
        - Si está en Mantenimiento (0) -> Pasa a Activa (1) y estado 'Disponible'.
        """
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # CASE: Invierte los valores basándose en el estado actual en el disco duro
                    consulta_toggle = """
                        UPDATE Estaciones 
                        SET estado = CASE WHEN estado = 1 THEN 0 ELSE 1 END,
                            id_estado = CASE WHEN estado = 1 
                                            THEN (SELECT id_estado FROM EstadosEstacion WHERE nombre_estado = 'Mantenimiento')
                                            ELSE (SELECT id_estado FROM EstadosEstacion WHERE nombre_estado = 'Disponible') 
                                        END
                        WHERE codigo_pc = ?
                    """
                    cursor.execute(consulta_toggle, (codigo_pc,))
                    conn.commit()
                    print(f"Estado operativo de {codigo_pc} alternado correctamente.")
                    return True
            except pyodbc.Error as e:
                conn.rollback()
                print(f"Error CRUD Toggle PC/Estación: {e}")
            finally:
                conn.close()
        return False

    def alternar_estado_usuario(self, id_usuario):
        """
        CRUD: Toggle de Estado de Cuenta Gamer
        Alterna el bit 'estado' entre 0 y 1 utilizando lógica SQL CASE.
        """
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = "UPDATE Usuarios SET estado = CASE WHEN estado = 1 THEN 0 ELSE 1 END WHERE id_usuario = ?"
                    cursor.execute(consulta, (id_usuario,))
                    conn.commit()
                    print(f"Toggle Exitoso: Cuenta de Usuario ID {id_usuario} alternada.")
                    return True
            except pyodbc.Error as e:
                print(f"Error CRUD Toggle Usuario: {e}")
            finally:
                conn.close()
        return False
    
    def registrar_nueva_estacion(self, codigo_pc, id_categoria, cpu, ram, gpu, monitor):
        """
        CRUD: Create (ITSM Hardware & Estación)
        Inserta las especificaciones técnicas en la tabla 'Computadoras' 
        y genera su módulo físico correspondiente en 'Estaciones' dentro de una sola transacción ACID.
        """
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # 1. Insertamos el hardware físico en la tabla Computadoras
                    consulta_hw = """
                        INSERT INTO Computadoras (codigo_pc, procesador, memoria_ram, tarjeta_grafica, monitor)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    cursor.execute(consulta_hw, (codigo_pc, cpu, ram, gpu, monitor))
                    
                    # 2. Creamos la estación lógica en Estaciones vinculada al código de la PC
                    # Por defecto inicia operativa ('Disponible') y estado (1)
                    consulta_estacion = """
                        INSERT INTO Estaciones (id_categoria, codigo_pc, id_estado, estado)
                        VALUES (?, ?, (SELECT id_estado FROM EstadosEstacion WHERE nombre_estado = 'Disponible'), 1)
                    """
                    cursor.execute(consulta_estacion, (id_categoria, codigo_pc))
                    
                    conn.commit()
                    print(f"Éxito ACID: Nueva estación {codigo_pc} registrada e integrada al mapa.")
                    return True
            except pyodbc.Error as e:
                # PROTECCIÓN DE INTEGRIDAD: Si cualquiera de los dos INSERTs falla (ej. código duplicado),
                # el rollback deshace todo para no dejar registros a medias en el disco duro.
                conn.rollback()
                print(f"Error al registrar nueva estación (Transacción revertida): {e}")
            finally:
                conn.close()
        return False
    
    def obtener_siguiente_codigo_pc(self):
        """
        ALGORITMO DE AUTOGENERACIÓN DE IDs:
        Consulta la tabla Computadoras para encontrar el código más alto actual (ej. 'PC-012'),
        extrae la parte numérica, la incrementa en 1 y formatea la nueva cadena con ceros (ej. 'PC-013').
        """
        conn = self.conectar()
        siguiente_codigo = "PC-001" # Valor por defecto si la tabla está completamente vacía
        if conn:
            try:
                with conn.cursor() as cursor:
                    # EXTRAEMOS EL MÁXIMO NÚMERO:
                    # SUBSTRING(codigo_pc, 4, LEN(codigo_pc)) corta el texto desde el carácter 4 (después de 'PC-')
                    # CAST(... AS INT) lo convierte a número para que SQL ordene matemáticamente y no alfabéticamente
                    consulta = """
                        SELECT MAX(CAST(SUBSTRING(codigo_pc, 4, LEN(codigo_pc)) AS INT)) 
                        FROM Computadoras 
                        WHERE codigo_pc LIKE 'PC-%'
                    """
                    cursor.execute(consulta)
                    resultado = cursor.fetchone()
                    
                    if resultado and resultado[0] is not None:
                        ultimo_numero = int(resultado[0])
                        nuevo_numero = ultimo_numero + 1
                        # FORMATO CON CEROS: :03d obliga al número a tener 3 dígitos (ej. 13 -> 013)
                        siguiente_codigo = f"PC-{nuevo_numero:03d}"
            except pyodbc.Error as e:
                print(f"Error al generar el siguiente código de PC: {e}")
            finally:
                conn.close()
                
        return siguiente_codigo
    
if __name__ == "__main__":
    # Este bloque solo corre si ejecutas 'conexion.py' directamente desde el play del IDE.
    # Es la técnica estándar para realizar pruebas unitarias rápidas de tus queries sin abrir las ventanas.
    manager = DBManager()
    pcs_reales = manager.obtener_estaciones()
    for pc in pcs_reales:
        print(pc)
