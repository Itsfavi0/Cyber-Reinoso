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
                print(f"Base de datos actualizada con éxito | id_usuario: {id_usuario} Nuevo Saldo: {nuevo_saldo:.2f}")
            except pyodbc.Error as e:
                print(f"Error al actualizar saldo: {e}")
            finally:
                cursor.close()
                conn.close()
    
if __name__ == "__main__":
    manager = DBManager()
    #manager.probar_conexion()
    pcs_reales = manager.obtener_estaciones()
    for pc in pcs_reales:
        print(pc)