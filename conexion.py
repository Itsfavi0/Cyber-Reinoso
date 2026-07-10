import pyodbc

class DBManager:
    def __init__(self):
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost;"
            "Database=CyberReinoso;"
            "Trusted_Connection=yes;"
        )
        
    def conectar(self):
        """Intenta abrir una conexion con la base de datos"""
        try:
            conexion = pyodbc.connect(self.connection_string)
            return conexion
        except pyodbc.Error as e:
            print(f"ERROR DE CONEXIÓN: No se pudo conectar a SQL Server. Detalles: {e}")
            return None
    
    def probar_conexion(self):
        """Método de diagnóstico para verificar que las tuberías funcionan"""
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT @@VERSION")
                    row = cursor.fetchone()
                    print("CONEXIÓN EXITOSA!!")
                    print(f"Version del servidor: {row}")
            except pyodbc.Error as e:
                print(f"Error en diagnóstico de conexión: {e}")
            finally:
                conn.close()
            
    def obtener_estaciones(self):
        """Consula la base de datos y retorna una lista de diccionarios con las PCs"""
        conn = self.conectar()
        lista_estaciones = []
        if conn:
            try:
                with conn.cursor() as cursor:
                    # Aplicamos el LEFT JOIN para unir el módulo lógico con la PC física
                    consulta = """
                        SELECT e.id_estacion, e.codigo_pc, e.categoria, e.estado_actual,
                               c.procesador, c.tarjeta_grafica, c.monitor, c.mouse
                        FROM Estaciones e
                        LEFT JOIN Computadoras c ON e.codigo_pc = c.codigo_pc
                    """
                    cursor.execute(consulta)
                    filas = cursor.fetchall()
                    
                    for fila in filas:
                        estacion = {
                            "id_estacion" : fila[0],
                            "codigo_pc" : fila[1],
                            "categoria" : fila[2],
                            "estado_actual" : fila[3],
                            "specs" : {
                                "procesador" : fila[4],
                                "tarjeta_grafica" : fila[5],
                                "monitor" : fila[6],
                                "mouse" : fila[7]
                            }
                        }
                        lista_estaciones.append(estacion)
            except pyodbc.Error as e:
                print(f"Error al leer las estaciones: {e}")
            finally:
                conn.close()
                
        return lista_estaciones 
    
    def obtener_productos(self):
        """Consulta la base de datos y retorna una lista de diccionarios con los productos"""
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
                            "precio" : float(fila[2]),
                            "stock" : fila[3]
                        }
                        lista_productos.append(producto)
            except pyodbc.Error as e:
                print(f"Error al leer los productos: {e}")
            finally:
                conn.close()
                
        return lista_productos
            
    def actualizar_estado_pc(self, id_estacion, nuevo_estado):
        """Actualiza el estado de la PC en la base de datos"""
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = """
                        UPDATE Estaciones
                        SET estado_actual = ? WHERE id_estacion = ?        
                    """
                    cursor.execute(consulta, (nuevo_estado, id_estacion))
                    conn.commit()
                    print(f"Base de datos actualizada con éxito | PC: {id_estacion} Estado: {nuevo_estado}")
            except pyodbc.Error as e:
                print(f"Error al actualizar la base de datos: {e}")
            finally:
                conn.close()
    
    def obtener_todos_los_usuarios(self):
        """Obtiene una lista básica de todos los gamers para el selector de la interfaz"""
        conn = self.conectar()
        lista_usuarios = []
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id_usuario, alias_gamer FROM Usuarios ORDER BY alias_gamer ASC"
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
        """Busca un usuario en la BD por su ID y retorna sus datos"""
        conn = self.conectar()
        datos_usuario = None
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = "SELECT id_usuario, alias_gamer, rango_cuenta, saldo_billetera, minutos_acumulados FROM Usuarios WHERE id_usuario = ?"
                    cursor.execute(consulta, (id_usuario,))
                    fila = cursor.fetchone()
                    
                    if fila:
                        datos_usuario = {
                            "id_usuario": fila[0],
                            "alias_gamer": fila[1],
                            "rango_cuenta": fila[2],
                            "saldo_billetera": float(fila[3]),
                            "minutos_acumulados" : fila[4]
                        }
            except pyodbc.Error as e:
                print(f"Error al leer el usuario: {e}")
            finally:
                conn.close()
                
        return datos_usuario
    
    def actualizar_saldo_usuario(self, id_usuario, nuevo_saldo):
        """Actualiza el saldo del usuario en la BD"""
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
        """Guarda el saldo actual, el rango y los minutos jugados tras finalizar una sesión"""
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = "UPDATE Usuarios SET saldo_billetera = ?, rango_cuenta = ?, minutos_acumulados = ? WHERE id_usuario = ?"
                    cursor.execute(consulta, (saldo, rango, minutos, id_usuario))
                    conn.commit()
            except pyodbc.Error as e:
                print(f"Error al actualizar progreso del usuario: {e}")
            finally:
                conn.close()
                
    def registrar_usuario(self, alias_gamer, rango_cuenta, saldo_inicial):
        """Inserta un nuevo gamer a la base de datos y retorna True si tuvo exito"""
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = """
                        INSERT INTO Usuarios (alias_gamer, rango_cuenta, saldo_billetera)
                        VALUES (?, ?, ?)
                    """
                    cursor.execute(consulta, (alias_gamer, rango_cuenta, saldo_inicial))
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
        """Inserta el registro final de una sesión terminada para el cuadre de caja"""
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
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
        conn = self.conectar()
        total_ingresos = 0.0
        
        if conn:
            try:
                with conn.cursor() as cursor:
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
        """Ïnserta el inicio de una sesión en la BD asociando al cajero de turno"""
        conn = self.conectar()
        id_sesion = None
        if conn:
            try:
                with conn.cursor() as cursor:
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
        """Completa el registro de una sesión existente al finalizarla"""
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
    
    def obtener_sesiones_activas(self):
        """Busca todas las sesiones en la BD que no tienen hora_fin (activas antes de una caída)"""
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
        """Registra cabecera, detalle y descuenta stock en una sola transacción segura (ACID)"""
        conn = self.conectar()
        exito = False
        if conn:
            try:
                with conn.cursor() as cursor:
                    # 1. Insertamos la Cabecera (Ventas) y capturamos el ID generado
                    consulta_cabecera = """
                        INSERT INTO Ventas (id_usuario, id_empleado, monto_total)
                        OUTPUT INSERTED.id_venta
                        VALUES (?, ?, ?)
                    """
                    cursor.execute(consulta_cabecera, (id_usuario, id_empleado, total_venta))
                    id_venta = cursor.fetchone()[0]
                    
                    # 2. Preparamos las consultas para el bucle
                    consulta_detalle = """
                        INSERT INTO DetalleVentas (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    consulta_stock = "UPDATE Productos SET stock = stock - ? WHERE id_producto = ?"
                    
                    # 3. Iteramos el carrito: Insertamos en el Detalle y restamos el Stock
                    for id_prod, datos in carrito.items():
                        subtotal = datos["precio"] * datos["cantidad"]
                        cursor.execute(consulta_detalle, (id_venta, id_prod, datos["cantidad"], datos["precio"], subtotal))
                        cursor.execute(consulta_stock, (datos["cantidad"], id_prod))
                    
                    # 4. Si todo salió bien, sellamos la transacción (El martillazo final)
                    conn.commit()
                    exito = True
                    print(f"Transacción exitosa | Ticket #{id_venta} | Cajero ID: {id_empleado}")
            except pyodbc.Error as e:
                # ¡MAGIA SENIOR! Si cualquier cosa falla, deshacemos todos los cambios
                conn.rollback() 
                print(f"Error crítico en Kiosco. Se aplicó ROLLBACK de seguridad: {e}")
            finally:
                conn.close()
        return exito
                
    def obtener_reporte_tienda_hoy(self):
        """Calcula el total de ingresos por ventas de kiosco en el día actual"""
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
        """Busca las credenciales en la BD y retorna los datos del empleado si son correctas"""
        conn = self.conectar()
        datos_empleado = None
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = "SELECT id_empleado, nombre, rol FROM Empleados WHERE usuario = ? AND clave = ?"
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
    
    def actualizar_hardware_pc(self, codigo_pc, procesador, monitor):
        """CRUD: Update - Modifica los componentes de una PC física"""
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = "UPDATE Computadoras SET procesador = ?, monitor = ? WHERE codigo_pc = ?"
                    cursor.execute(consulta, (procesador, monitor, codigo_pc))
                    conn.commit()
                    return True
            except pyodbc.Error as e:
                print(f"Error CRUD Update PC: {e}")
            finally:
                conn.close()
        return False

    def eliminar_pc_fisica(self, codigo_pc):
        """CRUD: Delete - Elimina un registro de hardware de la BD"""
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = "DELETE FROM Computadoras WHERE codigo_pc = ?"
                    cursor.execute(consulta, (codigo_pc,))
                    conn.commit()
                    return True
            except pyodbc.Error as e:
                print(f"Error CRUD Delete PC: {e}")
            finally:
                conn.close()
        return False

    def eliminar_usuario_gamer(self, id_usuario):
        """CRUD: Delete - Elimina una cuenta de usuario gamer de la BD"""
        conn = self.conectar()
        if conn:
            try:
                with conn.cursor() as cursor:
                    consulta = "DELETE FROM Usuarios WHERE id_usuario = ?"
                    cursor.execute(consulta, (id_usuario,))
                    conn.commit()
                    return True
            except pyodbc.Error as e:
                print(f"Error CRUD Delete Usuario: {e}")
            finally:
                conn.close()
        return False
    
if __name__ == "__main__":
    manager = DBManager()
    pcs_reales = manager.obtener_estaciones()
    for pc in pcs_reales:
        print(pc)
