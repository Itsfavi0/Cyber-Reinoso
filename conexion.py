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
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            row = cursor.fetchone()
            print("CONEXIÓN EXITOSA!!")
            print(f"Version del servidor: {row}")
            cursor.close()
            conn.close()
            
    def obtener_estaciones(self):
        """Consula la base de datos y retorna una lista de diccionarios con las PCs"""
        conn = self.conectar()
        lista_estaciones = []
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                        SELECT id_estacion, codigo_pc, categoria, estado_actual
                        FROM Estaciones
                    """
                    )
                filas = cursor.fetchall()
                
                for fila in filas:
                    estacion = {
                        "id_estacion" : fila[0],
                        "codigo_pc" : fila[1],
                        "categoria" : fila[2],
                        "estado_actual" : fila[3]
                    }
                    lista_estaciones.append(estacion)
            except pyodbc.Error as e:
                print(f"Error al leer las estaciones: {e}")
            finally:
                cursor.close()
                conn.close()
                
        return lista_estaciones 
    
    def obtener_productos(self):
        """Consulta la base de datos y retorna una lista de diccionarios con los productos"""
        conn = self.conectar()
        lista_productos = []
        if conn:
            try:
                cursor = conn.cursor()
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
                cursor.close()
                conn.close()
                
        return lista_productos
    
    def restar_stock_producto(self, nombre_producto):
        """Resta 1 unidad al stock del producto en la BD siempre que tenga existencia"""
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                consulta = "UPDATE Productos SET stock = stock - 1 WHERE nombre_producto = ? AND stock > 0"
                cursor.execute(consulta, (nombre_producto))
                conn.commit()
                print(f"Inventario actualizado con éxito | Producto: {nombre_producto} (-1 unidades)")
            except pyodbc as e:
                print(f"Error al actualizar el stock: {e}")
            finally:
                cursor.close()
                conn.close()
            
    def actualizar_estado_pc(self, id_estacion, nuevo_estado):
        """Actualiza el estado de la PC en la base de datos"""
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
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
                cursor.close()
                conn.close()
    
    def obtener_todos_los_usuarios(self):
        """Obtiene una lista básica de todos los gamers para el selector de la interfaz"""
        conn = self.conectar()
        lista_usuarios = []
        if conn:
            try:
                cursor = conn.cursor()
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
                cursor.close()
                conn.close()
                
        return lista_usuarios
     
    def obtener_usuario(self, id_usuario):
        """Busca un usuario en la BD por su ID y retorna sus datos"""
        conn = self.conectar()
        datos_usuario = None
        if conn:
            try:
                cursor =  conn.cursor()
                cursor.execute(
                    "SELECT * FROM Usuarios WHERE id_usuario = ?", (id_usuario)
                )
                fila = cursor.fetchone()
                
                if fila:
                    datos_usuario = {
                        "id_usuario": fila[0],
                        "alias_gamer": fila[1],
                        "rango_cuenta": fila[2],
                        "saldo_billetera": float(fila[3])
                    }
                
            except pyodbc.Error as e:
                print(f"Error al leer el usuario: {e}")
            finally:
                cursor.close()
                conn.close()
                
        return datos_usuario
    
    def actualizar_saldo_usuario(self, id_usuario, nuevo_saldo):
        """Actualiza el saldo del usuario en la BD"""
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                
                consulta = "UPDATE Usuarios SET saldo_billetera = ? WHERE id_usuario = ?"
                cursor.execute(consulta, (nuevo_saldo, id_usuario))
                conn.commit()
                print(f"Base de datos actualizada con éxito | id_usuario: {id_usuario} | Nuevo Saldo: {nuevo_saldo:.2f}")
            except pyodbc.Error as e:
                print(f"Error al actualizar saldo: {e}")
            finally:
                cursor.close()
                conn.close()
                
    def registrar_usuario(self, alias_gamer, rango_cuenta, saldo_inicial):
        """Inserta un nuevo gamer a la base de datos y retorna True si tuvo exito"""
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                
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
                cursor.close()
                conn.close()
        return False
                
    def guardar_historial_sesion(self, id_usuario, id_estacion, hora_inicio, hora_fin, monto_cobrado):
        """Inserta el registro final de una sesión terminada para el cuadre de caja"""
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
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
                cursor.close()
                conn.close()
    
    def obtener_reporte_caja_hoy(self):
        conn = self.conectar()
        total_ingresos = 0.0
        
        if conn:
            try:
                cursor = conn.cursor()
                #Usamos CAST(GETDAY() AS DATE)
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
                cursor.close()
                conn.close()
        return total_ingresos
    
    def registrar_venta_tienda(self, id_usuario, id_producto, monto):
        """Guarda el registro de una venta del kiosco en el historial"""
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                consulta = """
                    INSERT INTO Ventas_Kiosco (id_usuario, id_producto, monto)
                    VALUES (?, ?, ?)
                """
                cursor.execute(consulta, (id_usuario, id_producto, monto))
                conn.commit()
                print(f"Venta registrada en historial | ID Prod: {id_producto} | S/ {monto:.2f}")
            except pyodbc.Error as e:
                print(f"Error al registrar la venta en la BD: {e}")
            finally:
                cursor.close()
                conn.close()
                
    def obtener_reporte_tienda_hoy(self):
        """Calcula el total de ingresos por ventas de kiosco en el día actual"""
        conn = self.conectar()
        total_ingresos = 0.0
        
        if conn:
            try:
                cursor = conn.cursor()
                consulta = """
                    SELECT SUM(monto) 
                    FROM Ventas_Kiosco 
                    WHERE CAST(fecha_venta AS DATE) = CAST(GETDATE() AS DATE)
                """
                cursor.execute(consulta)
                resultado = cursor.fetchone()
                
                if resultado and resultado[0] is not None:
                    total_ingresos = float(resultado[0])
                    
            except pyodbc.Error as e:
                print(f"Error al generar reporte de tienda: {e}")
            finally:
                cursor.close()
                conn.close()
                
        return total_ingresos
    
if __name__ == "__main__":
    manager = DBManager()
    #manager.probar_conexion()
    pcs_reales = manager.obtener_estaciones()
    for pc in pcs_reales:
        print(pc)