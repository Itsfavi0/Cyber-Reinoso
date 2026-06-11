import pyodbc

class DBManager:
    def __init__(self):
        # Cadena de conexión estándar para SQL Server Express o LocalDB
        # Usamos Autenticación de Windows (Trusted_Connection=yes) para mayor seguridad local
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost;"  # Cambia por tu servidor si usas otra instancia
            "Database=CyberReinoso;"       # El nombre que le diste a tu base de datos
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
            
if __name__ == "__main__":
    manager = DBManager()
    manager.probar_conexion()