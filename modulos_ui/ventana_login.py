import tkinter as tk
import os
from tkinter import messagebox
from conexion import DBManager
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class VentanaLogin(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("🔒 Login - Cyber Reinoso")
        self.geometry("420x600")
        self.config(bg="#121212") 
        self.resizable(False, False)
        
        # Centrar la ventana en la pantalla
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        self.protocol("WM_DELETE_WINDOW", self.cerrar_todo)
        self.grab_set()
        
        self.construir_interfaz()

    def construir_interfaz(self):
        # Contenedor principal con diseño flotante (tarjeta)
        card = tk.Frame(
            self, 
            bg="#1E1E1E", 
            highlightbackground="#2C2C2C", 
            highlightthickness=1, 
            padx=30, 
            pady=30
        )
        card.pack(expand=True, fill=tk.BOTH, padx=25, pady=25)
        
        try:
            self.iconbitmap("assets/logo.ico")
        except Exception:
            pass  # Ignoramos el error si no se encuentra el archivo .ico
        
        ruta_logo = "assets/logo.png"
        if os.path.exists(ruta_logo):
            try:
                img_orig = Image.open(ruta_logo)
                # Redimensionamos a un tamaño elegante (ej. 85x85 píxeles)
                img_res = img_orig.resize((140, 140), Image.Resampling.LANCZOS)
                self.foto_logo = ImageTk.PhotoImage(img_res) # ¡Clave! Guardar referencia en self
                
                lbl_logo = tk.Label(card, image=self.foto_logo, bg="#1E1E1E") # Usa el color de fondo de tu login
                lbl_logo.pack(pady=(10, 5))
            except Exception as e:
                print(f"No se pudo renderizar el logo del login: {e}")
        
        # Título del Centro de Control
        tk.Label(
            card, 
            text="CYBER REINOSO", 
            font=("Segoe UI", 18, "bold"), 
            bg="#1E1E1E", 
            fg="#FFFFFF"
        ).pack(pady=(10, 2))
        
        tk.Label(
            card, 
            text="Control de Acceso • Cajero", 
            font=("Segoe UI", 10), 
            bg="#1E1E1E", 
            fg="#A0A0A0"
        ).pack(pady=(0, 25))
        
        # Campo: Usuario
        tk.Label(
            card, 
            text="USUARIO", 
            font=("Segoe UI", 9, "bold"), 
            bg="#1E1E1E", 
            fg="#A0A0A0"
        ).pack(anchor="w", pady=(5, 2))
        
        self.entry_usuario = tk.Entry(
            card, 
            font=("Segoe UI", 11), 
            bg="#2C2C2C", 
            fg="white", 
            insertbackground="white", 
            relief="flat", 
            bd=5
        )
        self.entry_usuario.pack(fill=tk.X, pady=(0, 15))
        self.entry_usuario.focus_set()
        
        # Campo: Contraseña
        tk.Label(
            card, 
            text="CONTRASEÑA", 
            font=("Segoe UI", 9, "bold"), 
            bg="#1E1E1E", 
            fg="#A0A0A0"
        ).pack(anchor="w", pady=(5, 2))
        
        self.entry_clave = tk.Entry(
            card, 
            font=("Segoe UI", 11), 
            show="*", 
            bg="#2C2C2C", 
            fg="white", 
            insertbackground="white", 
            relief="flat", 
            bd=5
        )
        self.entry_clave.pack(fill=tk.X, pady=(0, 25))
        
        # Botón de Ingreso
        self.btn_ingresar = tk.Button(
            card, 
            text="INICIAR TURNO", 
            font=("Segoe UI", 11, "bold"), 
            bg="#27ae60", 
            fg="white", 
            activebackground="#219653", 
            activeforeground="white", 
            relief="flat", 
            pady=8,
            cursor="hand2"
        )
        self.btn_ingresar.pack(fill=tk.X, pady=(10, 10))
        self.btn_ingresar.config(command=self.procesar_login)
        
        # Vincular tecla Enter para ingresar rápidamente
        self.bind("<Return>", lambda event: self.procesar_login())
        
        # Efecto Hover
        self.btn_ingresar.bind("<Enter>", lambda e: self.btn_ingresar.config(bg="#2E7D32"))
        self.btn_ingresar.bind("<Leave>", lambda e: self.btn_ingresar.config(bg="#27ae60"))

    def procesar_login(self):
        usuario = self.entry_usuario.get().strip()
        clave = self.entry_clave.get().strip()
        
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
