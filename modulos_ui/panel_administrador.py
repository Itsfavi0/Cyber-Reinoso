"""
CAPA DE PRESENTACIÓN / INTERFAZ GRÁFICA (UI)
MÓDULO INTERNO: PANEL ADMINISTRADOR (ITSM / CRUD CONTROLLER)
Este componente visual hereda de tk.LabelFrame para encapsular de manera aislada las herramientas 
de mantenimiento físico de hardware y depuración de registros en la base de datos de SQL Server.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from conexion import DBManager
from modulos_ui.ventanas_emergentes import VentanaRegistro, VentanaReporteCaja

# --- PALETA DE COLORES ---
BG_PANEL = "#1E1E1E"
TEXTO_MAIN = "#FFFFFF"
TEXTO_SECUNDARIO = "#A0A0A0"
COLOR_ELIMINAR = "#D32F2F"

class PanelAdministrador(tk.LabelFrame):
    def __init__(self, parent, controlador, *args, **kwargs):
        """
        CONSTRUCTOR DEL PANEL: Enlaza el contenedor padre y guarda el controlador principal.
        - *args y **kwargs: Permiten recibir cualquier parámetro extra de Tkinter (como width, height o padding)
          y pasárselos de manera flexible al constructor padre de la interfaz sin romper el código.
        """
        super().__init__(parent, text="Módulo Administrador", font=("Segoe UI", 12, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN, padx=15, pady=15, *args, **kwargs)
        self.controlador = controlador # Referencia al Mediador central (main.py)
        self.dibujar_panel()

    def dibujar_panel(self):
        """
        ALGORITMO DE RECONSTRUCCIÓN GRÁFICA:
        Recorre todos los widgets hijos que existan dentro del panel y los destruye uno por uno.
        Esto limpia por completo la memoria RAM gráfica de Windows antes de volver a dibujar las cajas,
        evitando fugas de memoria o duplicados visuales al refrescar.
        """
        # NOTA BÁSICA: self.winfo_children() devuelve una lista con todas las cajas, etiquetas y botones internos actuales.
        for widget in self.winfo_children():
            widget.destroy()

        db = DBManager()
        
        # =========================================================================
        # SECCIÓN 1: GESTIÓN OPERATIVA Y CAJA
        # =========================================================================
        tk.Label(self, text="📊 Operaciones de Caja:", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="w", pady=(0, 5))

        # Botón: Registrar Nuevo Usuario
        self.btn_registro = tk.Button(
            self, 
            text="➕ Registrar Nuevo Gamer", 
            font=("Segoe UI", 10, "bold"), 
            bg="#6A1B9A", 
            fg="white", 
            relief="flat", 
            pady=6, 
            cursor="hand2",
            command=lambda: VentanaRegistro(self.controlador, callback_actualizar=self.controlador.refrescar_interfaz)
        )
        self.btn_registro.pack(fill=tk.X, pady=(0, 8))
        self.btn_registro.bind("<Enter>", lambda e: self.btn_registro.config(bg="#8E24AA"))
        self.btn_registro.bind("<Leave>", lambda e: self.btn_registro.config(bg="#6A1B9A"))

        # Botón: Reporte de Caja
        self.btn_reporte = tk.Button(
            self, 
            text="📈 Reporte de Caja (Hoy)", 
            font=("Segoe UI", 10, "bold"), 
            bg="#E65100", 
            fg="white", 
            relief="flat", 
            pady=6, 
            cursor="hand2",
            command=lambda: VentanaReporteCaja(self.controlador)
        )
        self.btn_reporte.pack(fill=tk.X, pady=(0, 15))
        self.btn_reporte.bind("<Enter>", lambda e: self.btn_reporte.config(bg="#F57C00"))
        self.btn_reporte.bind("<Leave>", lambda e: self.btn_reporte.config(bg="#E65100"))

        # Separador visual
        tk.Frame(self, bg="#333333", height=1).pack(fill=tk.X, pady=(0, 15))
        # =========================================================================
        # SECCIÓN U (UPDATE): ACTUALIZAR COMPONENTES DE COMPUTADORAS
        # =========================================================================
        tk.Label(self, text="⚙️ Actualizar Hardware:", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="w", pady=(0, 5))
        
        # COMPRENSIÓN DE LISTAS (List Comprehension):
        # Filtra de manera hiper-eficiente la lista global de objetos en memoria RAM, extrayendo los códigos
        # de las computadoras válidas y saltándose aquellas mesas vacías o sin hardware asociado ("None").
        pcs_validas = [pc.codigo_pc for pc in self.controlador.lista_pcs if pc.codigo_pc and pc.codigo_pc != "None"]
        
        # Selector desplegable de máquinas
        # state="readonly" bloquea el Combobox para que el cajero no pueda escribir textos raros con el teclado.
        self.combo_pcs = ttk.Combobox(self, values=pcs_validas, state="readonly", font=("Segoe UI", 10))
        self.combo_pcs.pack(fill=tk.X, pady=(0, 10))
        
        # LÓGICA DEFENSIVA: Si existen computadoras registradas, selecciona por defecto el primer elemento del Combobox.
        if pcs_validas:
            self.combo_pcs.current(0)

        # Creación secuencial de las cajas de texto (Entries) para los 4 componentes críticos del Lan Center
        tk.Label(self, text="Procesador:", font=("Segoe UI", 9), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_cpu = tk.Entry(self, font=("Segoe UI", 10), bg="#2C2C2C", fg="white", relief="flat", bd=4)
        self.entry_cpu.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(self, text="Memoria Ram:", font=("Segoe UI", 9), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_ram = tk.Entry(self, font=("Segoe UI", 10), bg="#2C2C2C", fg="white", relief="flat", bd=4)
        self.entry_ram.pack(fill=tk.X, pady=(0, 8))

        tk.Label(self, text="GPU:", font=("Segoe UI", 9), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_gpu = tk.Entry(self, font=("Segoe UI", 10), bg="#2C2C2C", fg="white", relief="flat", bd=4)
        self.entry_gpu.pack(fill=tk.X, pady=(0, 8))

        tk.Label(self, text="Monitor:", font=("Segoe UI", 9), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_monitor = tk.Entry(self, font=("Segoe UI", 10), bg="#2C2C2C", fg="white", relief="flat", bd=4)
        self.entry_monitor.pack(fill=tk.X, pady=(0, 15))

        # Botón de envío que conecta la UI con el evento de actualización
        # cursor="hand2" cambia la flecha del mouse a una manito para mejorar la experiencia de usuario (UX).
        self.btn_update = tk.Button(self, text="Actualizar Hardware", font=("Segoe UI", 10, "bold"), bg="#1976D2", fg="white", relief="flat", pady=5, cursor="hand2", command=self.ejecutar_actualizacion_pc)
        self.btn_update.pack(fill=tk.X, pady=(0, 20))

        # =========================================================================
        # SECCIÓN D (DELETE): GESTIÓN DE ESTADO Y SOPORTE
        # =========================================================================
        tk.Label(self, text="🛠️ Gestión de Estado y Soporte:", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="w", pady=(10, 5))

        # Botón para enviar a mantenimiento o recuperar maquina
        self.btn_toggle_pc = tk.Button(
            self, 
            text="Cambiar Estado PC (Mantenimiento/Disponible)", 
            font=("Segoe UI", 9, "bold"), 
            bg="#00838F", # Cyan
            fg="white", 
            relief="flat", 
            pady=6, 
            cursor="hand2", 
            command=self.ejecutar_toggle_pc
        )
        self.btn_toggle_pc.pack(fill=tk.X, pady=(0, 10))
        self.btn_toggle_pc.bind("<Enter>", lambda e: self.btn_toggle_pc.config(bg="#0097A7"))
        self.btn_toggle_pc.bind("<Leave>", lambda e: self.btn_toggle_pc.config(bg="#00838F"))

        # Botón para activar o desactivar usuario gamer
        self.btn_toggle_user = tk.Button(
            self, 
            text="Activar / Desactivar Gamer", 
            font=("Segoe UI", 9, "bold"), 
            bg="#AD1457", # Magenta
            fg="white", 
            relief="flat", 
            pady=6, 
            cursor="hand2", 
            command=self.ejecutar_toggle_usuario
        )
        self.btn_toggle_user.pack(fill=tk.X)
        self.btn_toggle_user.bind("<Enter>", lambda e: self.btn_toggle_user.config(bg="#C2185B"))
        self.btn_toggle_user.bind("<Leave>", lambda e: self.btn_toggle_user.config(bg="#AD1457"))

    def ejecutar_actualizacion_pc(self):
        """Captura los datos del formulario de hardware y gatilla el UPDATE parcial en la BD"""
        
        # .get().strip() extrae el texto escrito por el administrador y borra los espacios en blanco 
        # accidentales que haya puesto al inicio o al final, limpiando la cadena antes de que viaje a SQL.
        pc_codigo = self.combo_pcs.get()
        cpu = self.entry_cpu.get().strip()
        ram = self.entry_ram.get().strip()
        gpu = self.entry_gpu.get().strip()
        monitor = self.entry_monitor.get().strip()

        # CONTROL DE ENTRADA: Si el administrador no escribió nada en ninguna de las 4 cajas, 
        # frena el proceso mediante una advertencia flotante, evitando enviar una consulta vacía.
        if not cpu and not ram and not gpu and not monitor:
            messagebox.showwarning("Campos Vacíos", "Por favor rellene los nuevos componentes.", parent=self)
            return

        db = DBManager()
        # Invocamos el método dinámico del DAO pasándole las variables capturadas de la UI
        if db.actualizar_hardware_pc(pc_codigo, cpu, monitor, ram, gpu):
            messagebox.showinfo("CRUD: Update", f"Componentes de {pc_codigo} actualizados con éxito.", parent=self)
            # .delete(0, tk.END) vacía por completo el contenido de la caja de texto 
            # desde la posición cero hasta el final, dejándola limpia para la siguiente operación.
            self.entry_cpu.delete(0, tk.END)
            self.entry_ram.delete(0, tk.END)
            self.entry_gpu.delete(0, tk.END)
            self.entry_monitor.delete(0, tk.END)
            
            # FLUJO COMPLETO: Obligamos al orquestador a recargar los objetos de SQL y redibujar el mapa de inmediato
            self.controlador.cargar_datos_iniciales()
            self.controlador.refrescar_interfaz()

    def ejecutar_toggle_pc(self):
        """Alterna una estación entre 'Mantenimiento' (Inactiva) y 'Disponible' (Activa)"""
        pc_codigo = self.combo_pcs.get()
        if not pc_codigo: return

        confirmar = messagebox.askyesno(
            "Gestión de Infraestructura", 
            f"¿Desea cambiar el estado operativo de la {pc_codigo}?\n\n• Si está operativa, pasará a MANTENIMIENTO.\n• Si está en soporte, se REACTIVARÁ en el mapa.", 
            parent=self
        )
        if confirmar:
            db = DBManager()
            if db.alternar_estado_estacion(pc_codigo):
                messagebox.showinfo("ITSM: Transición Exitoso", f"El estado de la {pc_codigo} ha sido alternado correctamente.", parent=self)
                self.controlador.cargar_datos_iniciales()
                self.controlador.refrescar_interfaz()

    def ejecutar_toggle_usuario(self):
        """Alterna el estado de una cuenta entre Activa e Inhabilitada"""
        usuario = self.controlador.usuario_activo
        if usuario.id_usuario == 1:
            messagebox.showwarning("Acción denegada", "El usuario base por defecto (Invitado) debe permanecer siempre activo.", parent=self)
            return

        confirmar = messagebox.askyesno(
            "Control de Cuenta", 
            f"¿Desea alternar el estado de acceso para el gamer '{usuario.alias_gamer}'?\n\n• Si está activo, quedará inhabilitado.\n• Si estaba desactivado, volverá a estar disponible para alquileres.", 
            parent=self
        )
        if confirmar:
            db = DBManager()
            if db.alternar_estado_usuario(usuario.id_usuario):
                messagebox.showinfo("Éxito", f"El estado de la cuenta de '{usuario.alias_gamer}' fue alternado con éxito.", parent=self)
                self.controlador.cargar_datos_iniciales()
                self.controlador.refrescar_interfaz()




