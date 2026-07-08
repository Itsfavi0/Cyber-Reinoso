import tkinter as tk
from tkinter import ttk, messagebox
from conexion import DBManager

class VentanaLogin(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("🔒 Login - Cyber Reinoso")
        self.geometry("400x350")
        self.config(bg="#2c3e50") 
        self.resizable(False, False)
        
        self.protocol("WM_DELETE_WINDOW", self.cerrar_todo)
        self.grab_set()
        
        self.construir_interfaz()

    def construir_interfaz(self):
        tk.Label(self, text="CYBER REINOSO", font=("Arial", 20, "bold"), bg="#2c3e50", fg="white").pack(pady=(30, 10))
        tk.Label(self, text="Control de Acceso", font=("Arial", 12), bg="#2c3e50", fg="#bdc3c7").pack(pady=(0, 20))
        
        tk.Label(self, text="Usuario:", font=("Arial", 10, "bold"), bg="#2c3e50", fg="white").pack(anchor="w", padx=50)
        self.entry_usuario = ttk.Entry(self, font=("Arial", 12))
        self.entry_usuario.pack(fill=tk.X, padx=50, pady=5)
        
        tk.Label(self, text="Contraseña:", font=("Arial", 10, "bold"), bg="#2c3e50", fg="white").pack(anchor="w", padx=50, pady=(10, 0))
        self.entry_clave = ttk.Entry(self, font=("Arial", 12), show="*")
        self.entry_clave.pack(fill=tk.X, padx=50, pady=5)
        
        btn_ingresar = tk.Button(self, text="INICIAR TURNO", font=("Arial", 12, "bold"), bg="#27ae60", fg="white", command=self.procesar_login)
        btn_ingresar.pack(fill=tk.X, padx=50, pady=30)

    def procesar_login(self):
        usuario = self.entry_usuario.get()
        clave = self.entry_clave.get()
        
        if not usuario or not clave:
            messagebox.showwarning("Campos vacíos", "Por favor ingrese usuario y contraseña.", parent=self)
            return
            
        db = DBManager()
        empleado = db.validar_login(usuario, clave)
        
        if empleado:
            messagebox.showinfo("Acceso Permitido", f"Bienvenido, {empleado['nombre']}.\nRol: {empleado['rol']}", parent=self)
            self.parent.empleado_actual = empleado 
            self.destroy() 
            self.parent.deiconify() 
        else:
            messagebox.showerror("Acceso Denegado", "Credenciales incorrectas o el usuario no existe.", parent=self)

    def cerrar_todo(self):
        self.parent.destroy()