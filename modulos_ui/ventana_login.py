"""
CAPA DE PRESENTACIÓN / INTERFAZ GRÁFICA (UI)
MÓDULO DE SEGURIDAD: VENTANA LOGIN (AUTHENTICATION & ACCESS GATEKEEPER)
Este componente visual hereda de tk.Toplevel para comportarse como una ventana emergente autónoma.
Implementa un bloqueo de seguridad modal que oculta y congela el orquestador principal (main.py)
hasta que un empleado (Administrador o Cajero) valide su identidad contra la base de datos relacional.
"""

import tkinter as tk
import os
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from conexion import DBManager

class VentanaLogin(tk.Toplevel):
    def __init__(self, parent):
        """
        CONSTRUCTOR DE SEGURIDAD MODAL:
        - parent: Recibe la instancia de AppCyberReinoso (main.py), la cual se encuentra oculta en este instante.
        """
        super().__init__(parent)
        self.parent = parent
        self.title("🔒 Login - Cyber Reinoso")
        self.geometry("420x600")
        self.config(bg="#121212") # Fondo oscuro corporativo
        
        # BLOQUEO DE REDIMENSIÓN: Evita que el usuario deforme las proporciones de los campos de entrada
        self.resizable(False, False)
        
        # ---------------------------------------------------------------------
        # ALGORITMO DE CENTRADO SIMÉTRICO DE ALTA PRECISIÓN
        # ---------------------------------------------------------------------
        # update_idletasks() obliga al motor gráfico de Windows a calcular el tamaño 
        # real en píxeles de los bordes y la barra de título antes de posicionarla en la pantalla.
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        # ---------------------------------------------------------------------
        # BLINDAJE DE SEGURIDAD (ANTI-EVASIÓN DE LOGIN)
        # ---------------------------------------------------------------------
        # PROTOCOLO DE CIERRE SECUESTRADO: Si el usuario presiona la 'X' roja de la ventana de login
        # para intentar saltarse la clave y entrar al software, ejecutamos self.cerrar_todo,
        # lo que destruye la aplicación entera por completo. Cero puertas traseras.
        self.protocol("WM_DELETE_WINDOW", self.cerrar_todo)
        
        # CAPTURA MODAL ABSOLUTA (GRAB_SET):
        # Monopoliza todos los eventos de clic del mouse y teclado del sistema operativo hacia esta ventana.
        # Es imposible hacer clic en ninguna otra parte del programa hasta autenticarse.
        self.grab_set()
        
        # Renderizado de los widgets visuales
        self.construir_interfaz()

    def construir_interfaz(self):
        """Construye el diseño de tarjeta flotante (Card UI) con identidad de marca y campos de formulario"""
        
        # Contenedor principal estilizado como tarjeta flotante con bordes sutiles
        card = tk.Frame(
            self, 
            bg="#1E1E1E", 
            highlightbackground="#2C2C2C", 
            highlightthickness=1, 
            padx=30, 
            pady=30
        )
        card.pack(expand=True, fill=tk.BOTH, padx=25, pady=25)
        
        # Intenta cargar el ícono (.ico) de la barra de título
        try:
            self.iconbitmap("assets/logo.ico")
        except Exception:
            pass  # Si no encuentra el .ico, usa el ícono por defecto de Tkinter sin crashear
        
        # ---------------------------------------------------------------------
        # RENDERIZADO DE LOGOTIPO CORPORATIVO
        # ---------------------------------------------------------------------
        ruta_logo = "assets/logo.png"
        if os.path.exists(ruta_logo):
            try:
                img_orig = Image.open(ruta_logo)
                # Remuestreo Lanczos: Algoritmo de interpolación de alta calidad para evitar que el logo se vea pixelado o borroso
                img_res = img_orig.resize((140, 140), Image.Resampling.LANCZOS)
                
                # Guardar en 'self.foto_logo' como atributo de clase es obligatorio.
                # Si se guardara en una variable local normal, Python la borraría al terminar la función y el logo saldría en blanco.
                self.foto_logo = ImageTk.PhotoImage(img_res) 
                
                lbl_logo = tk.Label(card, image=self.foto_logo, bg="#1E1E1E")
                lbl_logo.pack(pady=(10, 5))
            except Exception as e:
                print(f"No se pudo renderizar el logo del login: {e}")
        
        # Encabezados de bienvenida y rol operativo
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
        
        # ---------------------------------------------------------------------
        # CAMPO DE ENTRADA: USUARIO
        # ---------------------------------------------------------------------
        tk.Label(
            card, 
            text="USUARIO", 
            font=("Segoe UI", 9, "bold"), 
            bg="#1E1E1E", 
            fg="#A0A0A0"
        ).pack(anchor="w", pady=(5, 2))
        
        # insertbackground="white" cambia el color de la rayita parpadeante del cursor 
        # para que sea claramente visible sobre el fondo oscuro #2C2C2C.
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
        
        # focus_set() coloca el cursor del teclado automáticamente dentro del casillero de usuario al abrir la app.
        # El cajero puede empezar a escribir su nombre inmediatamente sin necesidad de agarrar el mouse para hacer clic.
        self.entry_usuario.focus_set()
        
        # ---------------------------------------------------------------------
        # CAMPO DE ENTRADA: CONTRASEÑA
        # ---------------------------------------------------------------------
        tk.Label(
            card, 
            text="CONTRASEÑA", 
            font=("Segoe UI", 9, "bold"), 
            bg="#1E1E1E", 
            fg="#A0A0A0"
        ).pack(anchor="w", pady=(5, 2))
        
        # show="*" enmascara cada carácter digitado con un asterisco,
        # protegiendo las credenciales contra la mirada de curiosos alrededor del mostrador (Shoulder Surfing).
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
        
        # ---------------------------------------------------------------------
        # BOTÓN DE INGRESO Y EVENTOS ASÍNCRONOS
        # ---------------------------------------------------------------------
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
        
        # ACCESIBILIDAD (KEYBOARD BINDING): 
        # Permite al cajero presionar la tecla 'Enter' (<Return>) desde cualquier parte de la ventana para loguearse,
        # agilizando el inicio de turno sin tener que mover el puntero hasta el botón verde.
        self.bind("<Return>", lambda event: self.procesar_login())
        
        # EFECTO HOVER INTERACTIVO: Ilumina el botón al pasar el cursor por encima
        self.btn_ingresar.bind("<Enter>", lambda e: self.btn_ingresar.config(bg="#2E7D32"))
        self.btn_ingresar.bind("<Leave>", lambda e: self.btn_ingresar.config(bg="#27ae60"))

    def procesar_login(self):
        """
        MOTOR DE AUTENTICACIÓN Y DESBLOQUEO:
        Captura, limpia y valida las credenciales introducidas. Si el DAO autoriza el acceso,
        transfiere la sesión al orquestador principal y destruye el escudo modal.
        """
        # .get().strip() es fundamental en seguridad de formularios. 
        # Elimina espacios en blanco accidentales copiados y pegados al inicio o final del texto.
        usuario = self.entry_usuario.get().strip()
        clave = self.entry_clave.get().strip()
        
        # Evita enviar consultas SQL inútiles al servidor si el cajero dejó campos en blanco
        if not usuario or not clave:
            messagebox.showwarning("Campos vacíos", "Por favor ingrese usuario y contraseña.", parent=self)
            return
            
        # CONSULTA AL DAO (TRANSACTION GATEWAY):
        # Invoca la verificación en la BD normalizada en 3FN haciendo INNER JOIN entre Empleados y Roles.
        db = DBManager()
        empleado = db.validar_login(usuario, clave)
        
        if empleado:
            # FEEDBACK DE ACCESO
            messagebox.showinfo("Acceso Permitido", f"Bienvenido, {empleado['nombre']}.\nRol: {empleado['rol']}", parent=self)
            
            # Guardamos los datos del empleado activo en el orquestador (main.py)
            # para que todas las boletas y ventas de kiosco queden auditadas con el nombre de este cajero.
            self.parent.empleado_actual = empleado 
            
            # LIBERACIÓN DE RECURSOS: Destruye físicamente la ventana modal de login de la memoria RAM
            self.destroy() 
            
            # DEICONIFY: 
            # Le ordena a Tkinter que haga reaparecer y muestre en pantalla la ventana principal (AppCyberReinoso)
            # que se había ocultado al arrancar con self.withdraw() en main.py.
            self.parent.deiconify() 
        else:
            # RECHAZO DE SEGURIDAD
            messagebox.showerror("Acceso Denegado", "Credenciales incorrectas o el usuario no existe.", parent=self)

    def cerrar_todo(self):
        """
        MÉTODO DE CIERRE DE EMERGENCIA (KILL SWITCH INTERFAZ):
        Si el usuario intenta cerrar la ventana emergente con la 'X', se invoca este método que destruye
        a la ventana padre (self.parent.destroy()), terminando el proceso de Python por completo.
        """
        self.parent.destroy()