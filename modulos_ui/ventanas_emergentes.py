"""
CAPA DE PRESENTACIÓN / INTERFAZ GRÁFICA (UI)
MÓDULO AUXILIAR: VENTANAS EMERGENTES OPERATIVAS (MODAL SUB-CONTROLLERS)
Este archivo agrupa los controladores modales que heredan de tk.Toplevel.
Se encargan de capturar entradas del cajero para tareas específicas de corta duración,
asegurando el aislamiento visual y transaccional mediante captura del foco del sistema.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from conexion import DBManager

# --- PALETA COLORES COHERENTE CON EL DASHBOARD ---
BG_BASE = "#121212"
BG_PANEL = "#1E1E1E"
TEXTO_MAIN = "#FFFFFF"
TEXTO_SECUNDARIO = "#A0A0A0"
BG_BOTON = "#2C2C2C"
COLOR_DISPONIBLE = "#00E676" # Verde éxito para transacciones e ingresos

# =========================================================================
# SUB-MODAL 1: REGISTRO DE NUEVOS CLIENTES
# =========================================================================
class VentanaRegistro(tk.Toplevel):
    def __init__(self, parent, callback_actualizar):
        """
        CONSTRUCTOR DE REGISTRO:
        - parent: Ventana desde donde se invoca (PanelUsuario).
        - callback_actualizar: Puntero de función (Delegado) para refrescar la UI principal al guardar.
        """
        super().__init__(parent)
        self.callback_actualizar = callback_actualizar
        self.title("Nuevo Gamer")
        self.geometry("380x420")
        self.config(bg=BG_BASE)
        self.resizable(False, False) # Bloquea la deformación del layout del formulario
        
        # CAPTURA MODAL (GRAB_SET): Secuestra el foco de la pantalla.
        # Impide que el cajero haga clicks accidentales en el mapa de PCs de fondo 
        # mientras llena el nombre del nuevo usuario, manteniendo un flujo de datos limpio.
        self.grab_set()
        
        # Algoritmo de centrado relativo en base a la resolución del monitor
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        """Dibuja el formulario de inscripción con estilo Card UI"""
        card = tk.Frame(self, bg=BG_PANEL, highlightbackground="#2C2C2C", highlightthickness=1, padx=25, pady=25)
        card.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(card, text="Registro de Usuario", font=("Segoe UI", 16, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(pady=(0, 20))
        
        tk.Label(card, text="ALIAS / NICKNAME:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_alias = tk.Entry(card, font=("Segoe UI", 11), bg="#2C2C2C", fg="white", insertbackground="white", relief="flat", bd=5)
        self.entry_alias.pack(fill=tk.X, pady=(5, 15))
        
        # UX FOCUS: Coloca el cursor automáticamente en el campo de texto.
        self.entry_alias.focus_set()

        tk.Label(card, text="SALDO INICIAL (S/):", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_saldo = tk.Entry(card, font=("Segoe UI", 11), bg="#2C2C2C", fg="white", insertbackground="white", relief="flat", bd=5)
        self.entry_saldo.pack(fill=tk.X, pady=(5, 20))
        
        self.btn_guardar = tk.Button(card, text="Guardar Gamer", font=("Segoe UI", 11, "bold"), bg="#6A1B9A", fg="white", relief="flat", activebackground="#4A148C", activeforeground="white", pady=8, cursor="hand2")
        self.btn_guardar.pack(fill=tk.X, pady=(10, 0))
        self.btn_guardar.config(command=self.guardar)
        self.bind("<Return>", lambda event: self.guardar())
        
        # Efecto Hover reactivo para las animaciones del botón
        self.btn_guardar.bind("<Enter>", lambda e: self.btn_guardar.config(bg="#8E24AA"))
        self.btn_guardar.bind("<Leave>", lambda e: self.btn_guardar.config(bg="#6A1B9A"))
        
    def guardar(self):
        """Gatilla la inserción del nuevo gamer en la base de datos aplicando 3FN"""
        # .get().strip() captura el texto digitado y elimina espacios accidentales.
        alias = self.entry_alias.get().strip()
        saldo_txt = self.entry_saldo.get().strip()
        
        # Validación perimetral contra entradas vacías.
        if not alias or not saldo_txt:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos.", parent=self)
            return
            
        try:
            # Si el cajero digita letras en el campo de dinero, 
            # saltará automáticamente la excepción ValueError atrapando el error sin romper la app.
            saldo = float(saldo_txt)
            if saldo < 0:
                raise ValueError() # El dinero no puede ser negativo en la apertura
                
            db = DBManager()
            # ARQUITECTURA AJUSTADA (3FN): Pasamos solo alias y saldo.
            # El motor SQL Server le asignará por defecto el id_rango 1 ('Bronce').
            exito = db.registrar_usuario(alias, saldo)
            if exito:
                messagebox.showinfo("Éxito", f"Usuario {alias} registrado correctamente.", parent=self)
                
                # EJECUCIÓN DEL CALLBACK:
                # Le avisa al panel principal que se acaba de añadir una fila en la BD,
                # forzando a que el Combobox se refresque y muestre al nuevo gamer de inmediato.
                if self.callback_actualizar:
                    self.callback_actualizar()
                self.destroy() # Destruye el objeto modal y libera la memoria RAM
            else:
                messagebox.showerror("Error", "No se pudo registrar el usuario en la Base de Datos.", parent=self)
        except ValueError:
            messagebox.showerror("Error de formato", "El saldo debe ser un número positivo válido.", parent=self)


# =========================================================================
# SUB-MODAL 2: INYECCIÓN DE SALDO PREPAGO
# =========================================================================
class VentanaRecarga(tk.Toplevel):
    def __init__(self, parent, usuario, callback_actualizar):
        """
        CONSTRUCTOR DE RECARGA:
        - usuario: Instancia completa del objeto 'Usuario' que está físicamente parado frente a la caja.
        """
        super().__init__(parent)
        self.usuario = usuario # Agregación de objeto de lógica de negocio
        self.callback_actualizar = callback_actualizar
        self.title("Recarga de Billetera")
        self.geometry("350x300")
        self.config(bg=BG_BASE)
        self.resizable(False, False)
        self.grab_set() # Aislamiento modal absoluto
        
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        card = tk.Frame(self, bg=BG_PANEL, highlightbackground="#2C2C2C", highlightthickness=1, padx=25, pady=25)
        card.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(card, text="Recargar Billetera", font=("Segoe UI", 16, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(pady=(0, 5))
        tk.Label(card, text=f"Gamer: {self.usuario.alias_gamer}", font=("Segoe UI", 11, "bold"), bg=BG_PANEL, fg=COLOR_DISPONIBLE).pack(pady=(0, 20))
        
        tk.Label(card, text="MONTO A RECARGAR (S/):", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_monto = tk.Entry(card, font=("Segoe UI", 12), bg="#2C2C2C", fg="white", insertbackground="white", relief="flat", bd=5)
        self.entry_monto.pack(fill=tk.X, pady=(5, 20))
        self.entry_monto.focus_set()
        
        self.btn_recargar = tk.Button(card, text="Confirmar Recarga", font=("Segoe UI", 11, "bold"), bg="#2E7D32", fg="white", relief="flat", activebackground="#1B5E20", activeforeground="white", pady=8, cursor="hand2")
        self.btn_recargar.pack(fill=tk.X)
        self.btn_recargar.config(command=self.procesar_recarga)
        self.bind("<Return>", lambda event: self.procesar_recarga())
        
        self.btn_recargar.bind("<Enter>", lambda e: self.btn_recargar.config(bg="#388E3C"))
        self.btn_recargar.bind("<Leave>", lambda e: self.btn_recargar.config(bg="#2E7D32"))
        
    def procesar_recarga(self):
        """Modifica el monedero del objeto en RAM y sincroniza mediante UPDATE en SQL Server"""
        try:
            monto_texto = self.entry_monto.get().strip()
            if not monto_texto:
                raise ValueError("El campo está vacío.")
            
            monto = float(monto_texto)
            if monto <= 0:
                raise ValueError("El monto debe ser positivo.")
            
            # PASO 1: Impacta la lógica del modelo en memoria RAM (Aumenta la variable interna de la app)
            self.usuario.recargar_saldo(monto)
                
            # PASO 2: Extrae el nuevo saldo del objeto y lo manda al DAO para persistencia definitiva en disco
            nuevo_saldo = self.usuario.saldo_billetera
            db = DBManager()
            db.actualizar_saldo_usuario(self.usuario.id_usuario, nuevo_saldo)
            
            messagebox.showinfo("Recarga Exitosa", f"Se recargaron S/ {monto:.2f} a {self.usuario.alias_gamer}.\nNuevo saldo: S/ {nuevo_saldo:.2f}", parent=self)
            
            # Ejecuta la señal de actualización para que las tarjetas de usuario en el dashboard pinten el dinero fresco
            if self.callback_actualizar:
                self.callback_actualizar()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error de entrada", f"Por favor ingrese un número válido. ({e})", parent=self)


# =========================================================================
# SUB-MODAL 3: AUDITORÍA FINANCIERA
# =========================================================================
class VentanaReporteCaja(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reporte de Caja")
        self.geometry("380x450")
        self.config(bg=BG_BASE)
        self.resizable(False, False)
        self.grab_set() # Encapsulamiento contable flotante
        
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        """Ejecuta el arqueo contable consolidando métricas cruzadas en tiempo real"""
        tk.Label(self, text="Cierre de Turno", font=("Segoe UI", 16, "bold"), bg=BG_BASE, fg=TEXTO_MAIN).pack(pady=15)
        
        # CONSOLIDADOR DE DATOS FINANCIEROS:
        # Manda dos señales independientes al DAO para calcular los dos centros de costos del negocio:
        # 1. ingresos_pcs: Sumatoria agregada de las sesiones de juego finalizadas hoy (Sesiones de Alquiler).
        # 2. ingresos_kiosco: Sumatoria agregada de las ventas del Punto de Venta (Snacks/Bebidas).
        db = DBManager()
        ingresos_pcs = db.obtener_reporte_caja_hoy()
        ingresos_kiosco = db.obtener_reporte_tienda_hoy()
        
        # Suma matemática lineal directa producida en caliente
        total_absoluto = ingresos_pcs + ingresos_kiosco
        
        # Maquetación del reporte contable visual
        frame_datos = tk.Frame(self, bg=BG_PANEL, bd=1, highlightbackground="#2C2C2C", highlightthickness=1, padx=20, pady=20)
        frame_datos.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        tk.Label(frame_datos, text="Alquiler de PCs:", font=("Segoe UI", 11), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        tk.Label(frame_datos, text=f"S/ {ingresos_pcs:.2f}", font=("Segoe UI", 14, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="e", pady=(0, 15))
        
        tk.Label(frame_datos, text="Ventas de Kiosco:", font=("Segoe UI", 11), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        tk.Label(frame_datos, text=f"S/ {ingresos_kiosco:.2f}", font=("Segoe UI", 14, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="e", pady=(0, 15))
        
        # Separador visual lineal estético (Línea divisoria divisoria)
        separator = tk.Frame(frame_datos, bg="#333333", height=1)
        separator.pack(fill=tk.X, pady=15)
        
        tk.Label(frame_datos, text="TOTAL EN CAJA:", font=("Segoe UI", 12, "bold"), bg=BG_PANEL, fg=COLOR_DISPONIBLE).pack(anchor="w")
        # Muestra la métrica absoluta final del estado financiero del Cyber
        tk.Label(frame_datos, text=f"S/ {total_absoluto:.2f}", font=("Segoe UI", 22, "bold"), bg=BG_PANEL, fg=COLOR_DISPONIBLE).pack(anchor="e")
        
        self.btn_cerrar = tk.Button(self, text="Cerrar Reporte", font=("Segoe UI", 11, "bold"), bg=BG_BOTON, fg=TEXTO_MAIN, relief="flat", activebackground="#424242", activeforeground="white", pady=8, cursor="hand2")
        self.btn_cerrar.pack(fill=tk.X, padx=20, pady=(0, 20))
        self.btn_cerrar.config(command=self.destroy)
        
        self.btn_cerrar.bind("<Enter>", lambda e: self.btn_cerrar.config(bg="#424242"))
        self.btn_cerrar.bind("<Leave>", lambda e: self.btn_cerrar.config(bg=BG_BOTON))
        
# =========================================================================
# SUB-MODAL 4: ALTA DE NUEVA INFRAESTRUCTURA (CON ID AUTOMÁTICO)
# =========================================================================
class VentanaNuevaEstacion(tk.Toplevel):
    def __init__(self, parent, callback_actualizar):
        super().__init__(parent)
        self.callback_actualizar = callback_actualizar
        self.title("Inaugurar Nueva Estación")
        self.geometry("400x560")
        self.config(bg=BG_BASE)
        self.resizable(False, False)
        self.grab_set() 
        
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        # 1. GENERAMOS EL CÓDIGO AUTOMÁTICO ANTES DE DIBUJAR LA INTERFAZ
        db = DBManager()
        self.codigo_autogenerado = db.obtener_siguiente_codigo_pc()
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        card = tk.Frame(self, bg=BG_PANEL, highlightbackground="#2C2C2C", highlightthickness=1, padx=25, pady=20)
        card.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(card, text="Añadir Nueva PC", font=("Segoe UI", 16, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(pady=(0, 15))
        
        # --- CAMPO CÓDIGO PC (AUTOMÁTICO Y BLOQUEADO) ---
        tk.Label(card, text="CÓDIGO DE PC (ASIGNACIÓN AUTOMÁTICA):", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=COLOR_DISPONIBLE).pack(anchor="w")
        
        self.entry_codigo = tk.Entry(card, font=("Segoe UI", 11, "bold"), bg="#1A3320", fg=COLOR_DISPONIBLE, relief="flat", bd=5)
        self.entry_codigo.pack(fill=tk.X, pady=(2, 10))
        
        # Insertamos el código autogenerado y bloqueamos el campo para evitar ediciones
        self.entry_codigo.insert(0, self.codigo_autogenerado)
        self.entry_codigo.config(state="readonly")

        # Selector: Categoría de la mesa
        tk.Label(card, text="CATEGORÍA GAMA:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.combo_categoria = ttk.Combobox(card, values=["1 - Regular", "2 - eSports", "3 - Streaming VIP"], state="readonly", font=("Segoe UI", 10))
        self.combo_categoria.pack(fill=tk.X, pady=(2, 10))
        self.combo_categoria.current(0)

        # Especificaciones Técnicas (Aquí sí ponemos el foco inicial)
        tk.Label(card, text="PROCESADOR (CPU):", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_cpu = tk.Entry(card, font=("Segoe UI", 10), bg="#2C2C2C", fg="white", relief="flat", bd=4)
        self.entry_cpu.pack(fill=tk.X, pady=(2, 8))
        self.entry_cpu.focus_set() # El cursor arranca directo en el CPU

        tk.Label(card, text="MEMORIA RAM:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_ram = tk.Entry(card, font=("Segoe UI", 10), bg="#2C2C2C", fg="white", relief="flat", bd=4)
        self.entry_ram.pack(fill=tk.X, pady=(2, 8))

        tk.Label(card, text="TARJETA GRÁFICA (GPU):", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_gpu = tk.Entry(card, font=("Segoe UI", 10), bg="#2C2C2C", fg="white", relief="flat", bd=4)
        self.entry_gpu.pack(fill=tk.X, pady=(2, 8))

        tk.Label(card, text="MONITOR / PANTALLA:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_monitor = tk.Entry(card, font=("Segoe UI", 10), bg="#2C2C2C", fg="white", relief="flat", bd=4)
        self.entry_monitor.pack(fill=tk.X, pady=(2, 15))
        
        self.btn_guardar = tk.Button(card, text="🖥️ Inaugurar Estación", font=("Segoe UI", 11, "bold"), bg="#1976D2", fg="white", relief="flat", activebackground="#0D47A1", activeforeground="white", pady=8, cursor="hand2", command=self.guardar)
        self.btn_guardar.pack(fill=tk.X)
        self.bind("<Return>", lambda event: self.guardar())
        
        self.btn_guardar.bind("<Enter>", lambda e: self.btn_guardar.config(bg="#1E88E5"))
        self.btn_guardar.bind("<Leave>", lambda e: self.btn_guardar.config(bg="#1976D2"))
        
    def guardar(self):
        # Como el campo es readonly, extraemos el código directamente de nuestra variable de clase
        codigo = self.codigo_autogenerado
        categoria_sel = self.combo_categoria.get()
        cpu = self.entry_cpu.get().strip()
        ram = self.entry_ram.get().strip()
        gpu = self.entry_gpu.get().strip()
        monitor = self.entry_monitor.get().strip()
        
        if not cpu or not ram or not gpu or not monitor:
            messagebox.showwarning("Campos vacíos", "Por favor rellena todas las especificaciones de la máquina.", parent=self)
            return
            
        id_cat = int(categoria_sel.split(" - ")[0])
        
        db = DBManager()
        if db.registrar_nueva_estacion(codigo, id_cat, cpu, ram, gpu, monitor):
            messagebox.showinfo("Inauguración Exitosa", f"¡La estación {codigo} ha sido añadida correctamente a la sala!", parent=self)
            if self.callback_actualizar:
                self.callback_actualizar()
            self.destroy()
        else:
            messagebox.showerror("Error de Inserción", "No se pudo registrar la PC en la base de datos.", parent=self)


# =========================================================================
# SUB-MODAL 5: ALERTA DE CORTE AUTOMÁTICO NO BLOQUEANTE (NON-BLOCKING TOAST)
# =========================================================================
class AlertaCorteAutomatico(tk.Toplevel):
    def __init__(self, parent, usuario_gamer, codigo_pc):
        """
        CONSTRUCTOR DE ALERTA NO BLOQUEANTE:
        A diferencia de un tk.messagebox, esta ventana modal de aviso no utiliza grab_set(),
        lo que permite que el bucle asíncrono y los demás relojes continúen su curso.
        """
        super().__init__(parent)
        self.title("⚡ Corte de Conexión - Cyber Reinoso")
        self.geometry("400x220")
        self.config(bg=BG_BASE)
        self.resizable(False, False)
        
        # Algoritmo de centrado simétrico en pantalla
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        self.construir_interfaz(usuario_gamer, codigo_pc)
        
    def construir_interfaz(self, usuario_gamer, codigo_pc):
        card = tk.Frame(self, bg=BG_PANEL, highlightbackground="#FF1744", highlightthickness=2, padx=20, pady=20)
        card.pack(expand=True, fill=tk.BOTH, padx=12, pady=12)
        
        tk.Label(card, text="⚠️ CORTE AUTOMÁTICO", font=("Segoe UI", 12, "bold"), bg=BG_PANEL, fg="#FF1744").pack(pady=(0, 10))
        
        mensaje = f"Se agotó el saldo del gamer {usuario_gamer} en la {codigo_pc}.\nLa sesión ha sido finalizada automáticamente por el sistema."
        tk.Label(card, text=mensaje, font=("Segoe UI", 10), bg=BG_PANEL, fg=TEXTO_MAIN, justify="center", wraplength=340).pack(pady=(0, 15))
        
        btn_ok = tk.Button(card, text="Entendido", font=("Segoe UI", 10, "bold"), bg="#FF1744", fg="white", relief="flat", pady=6, cursor="hand2", command=self.destroy)
        btn_ok.pack(fill=tk.X)
        btn_ok.bind("<Enter>", lambda e: btn_ok.config(bg="#FF5252"))
        btn_ok.bind("<Leave>", lambda e: btn_ok.config(bg="#FF1744"))