import tkinter as tk
from tkinter import *

# Importando la logica del negocio de modelos.py
from modelos import Usuario, PC_Regular, PC_VIP, Sesion, SaldoInsuficienteError

# Clase app que hereda de la ventana de tk
class AppCyberReinoso(tk.Tk):
    def __init__(self):
        super().__init__()

        # Ventana básica
        self.title("Cyber Reinoso - Smart Center Dashboard")
        self.geometry("900x600")
        self.config(bg="#f4f4f9")
        
        # inicializar base de datos simulada en memoria por ahora
        self.cargar_datos_prueba()
        
        # Construccion de la interfaz
        self.crear_interfaz()
        
    def cargar_datos_prueba(self):
        """Simulacion de lo que luego se traerá con un SELECT desde SQL Server"""
        self.usuario_prueba = Usuario(id_usuario=1, alias_gamer="Itsfavi0", rango_cuenta="VIP", saldo_inicial=10.20)
        
        self.lista_pcs = [
            PC_Regular(id_estacion=1, codigo_pc="PC-001"),
            PC_Regular(id_estacion=2, codigo_pc="PC-002"),
            PC_Regular(id_estacion=3, codigo_pc="PC-003"),
            PC_Regular(id_estacion=4, codigo_pc="PC-004"),
            PC_VIP(id_estacion=5, codigo_pc="VIP-001"),
            PC_VIP(id_estacion=6, codigo_pc="VIP-002")
        ]
        
    def crear_interfaz(self):
        """Aquí maquetaremos los frames usando el gestor Grid o Pack"""
        # Titulo Principal
        lbl_titulo = tk.Label(self, text="Panel de Control - Cyber Reinoso",
                              font=("Arial", 18, "bold"), bg="#f4f4f9", fg="#333333")
        lbl_titulo.pack(pady=10)
        
        # Contenedor del mapa de computadoras
        self.frame_mapa = tk.Frame(self, bg="#e0e0eb", bd=3, relief="groove")
        self.frame_mapa.pack(expand=True, fill="both", padx=20, pady=10)
        
if __name__ == "__main__":
    app = AppCyberReinoso()
    app.mainloop()