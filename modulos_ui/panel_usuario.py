"""
CAPA DE PRESENTACIÓN / INTERFAZ GRÁFICA (UI)
MÓDULO DE ATENCIÓN: PANEL USUARIO (CLIENT CRM & CONTROLLER PANEL)
Este componente visual hereda de tk.LabelFrame para aislar perimetralmente el perfil del gamer activo.
Actúa como la pasarela de control financiero del cajero, permitiendo orquestar recargas, compras en tienda,
inscripción de nuevos usuarios y visualización de auditorías de caja diaria.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from conexion import DBManager
from modulos_ui.ventanas_emergentes import VentanaRecarga
from modulos_ui.panel_kiosco import VentanaTienda

# --- PALETA MODO OSCURO COHERENTE ---
BG_PANEL = "#1E1E1E"
TEXTO_MAIN = "#FFFFFF"
TEXTO_SECUNDARIO = "#A0A0A0"
COLOR_DISPONIBLE = "#00E676" # Verde para indicar saldo positivo disponible

class PanelUsuario(tk.LabelFrame):
    def __init__(self, parent, controlador, *args, **kwargs):
        """
        CONSTRUCTOR DEL PANEL: Enlaza el marco contenedor y el mediador central.
        """
        super().__init__(parent, text="Módulo del Cliente", font=("Segoe UI", 12, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN, padx=20, pady=20, *args, **kwargs)
        self.controlador = controlador # Referencia al main.py (Orquestador)
        self.dibujar_panel()

    def dibujar_panel(self):
        """
        ALGORITMO DE REFRESCO DINÁMICO DE PERFIL:
        Barre todos los elementos visuales antiguos para reconstruir la tarjeta con los 
        datos frescos del objeto Gamer activo guardado en el orquestador principal.
        """
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recuperamos el objeto Usuario puro que está seleccionado actualmente en la RAM
        usuario = self.controlador.usuario_activo
        
        # ---------------------------------------------------------------------
        # SECCIÓN DE SELECCIÓN (CRM SELECTOR)
        # ---------------------------------------------------------------------
        frame_seleccion = tk.Frame(self, bg=BG_PANEL)
        frame_seleccion.pack(fill=tk.X, pady=(0,15))
        
        tk.Label(frame_seleccion, text="Seleccionar Cliente:", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="w")
        
        # Conexión rápida al DAO para listar los clientes registrados en SQL Server
        db = DBManager()
        todos_los_usuarios = db.obtener_todos_los_usuarios()
        
        # COMPRENSIÓN DE LISTAS: Formatea las tuplas de SQL a cadenas legibles ("1 - Maximus_27") para el Combobox
        lista_nombres = [f"{u['id_usuario']} - {u['alias_gamer']}" for u in todos_los_usuarios]
        self.combo_usuarios = ttk.Combobox(frame_seleccion, values=lista_nombres, state="readonly", font=("Segoe UI", 11))
        self.combo_usuarios.pack(fill=tk.X, pady=5)
        self.combo_usuarios.set(f"{usuario.id_usuario} - {usuario.alias_gamer}") # Pinta el usuario activo actual
        
        # Captura el evento virtual <<ComboboxSelected>> (cambio de opción con el mouse)
        # y delega la reconstrucción del usuario al orquestador central (main.py) de forma asíncrona.
        self.combo_usuarios.bind("<<ComboboxSelected>>", self.controlador.cambiar_usuario_activo)
        
        # ---------------------------------------------------------------------
        # SECCIÓN DE RENDERIZADO DE PERFIL Y FIDELIZACIÓN (GAMER CARD)
        # ---------------------------------------------------------------------
        tk.Label(self, text="Gamer:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        tk.Label(self, text=usuario.alias_gamer, font=("Segoe UI", 14, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="w", pady=(0, 15))
        
        tk.Label(self, text="Rango:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        
        # MAPEO CROMÁTICO:
        # Utiliza una estructura asociativa (Diccionario) para pintar la etiqueta del rango con su color oficial de marca.
        # Mejora la UX permitiendo diferenciar los niveles VIP a un solo golpe de vista del cajero.
        colores_rango = {
            "Bronce": "#CD7F32",     # Color cobre/bronce tradicional
            "Plata": "#E0E0E0",      # Gris plateado brillante
            "Oro": "#FFD700",        # Dorado metálico intenso
            "Diamante": "#01FFFF"    # Celeste/Cyan Neón de alta fidelidad (Catálogo actualizado)
        }
        # N.get() busca la llave en el diccionario. Si el rango es corrupto o no existe, usa TEXTO_MAIN por defecto.
        color_rango = colores_rango.get(usuario.rango_cuenta, TEXTO_MAIN)
        
        tk.Label(self, text=usuario.rango_cuenta, font=("Segoe UI", 14, "bold"), bg=BG_PANEL, fg=color_rango).pack(anchor="w", pady=(0, 15))
        
        tk.Label(self, text="Estado del Gamer:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        
        if usuario.estado == 1:
            texto_estado = "CUENTA ACTIVA"
            color_estado = "#00E676"  # Verde neón brillante
        else:
            texto_estado = "INHABILITADA / SUSPENDIDA"
            color_estado = "#FF1744"  # Rojo de alerta
            
        tk.Label(self, text=texto_estado, font=("Segoe UI", 11, "bold"), bg=BG_PANEL, fg=color_estado).pack(anchor="w", pady=(0, 15))
        
        tk.Label(self, text="Saldo Disponible:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        # ':.2f' formatea el float de la billetera a dos decimales exactos en la pantalla para una lectura contable clara.
        tk.Label(self, text=f"S/ {usuario.saldo_billetera:.2f}", font=("Segoe UI", 18, "bold"), bg=BG_PANEL, fg=COLOR_DISPONIBLE).pack(anchor="w", pady=(0, 20))
        
        # ---------------------------------------------------------------------
        # ACCIONES DIRECTAS DEL CLIENTE SELECCIONADO
        # ---------------------------------------------------------------------
        
        # --- Botón 1: Recargar Billetera ---
        # Usamos una función anónima (lambda) en el parámetro command para instanciar la clase VentanaRecarga
        # al vuelo únicamente cuando el cajero presiona el botón, evitando que el modal se dispare solo al arrancar la app.
        self.btn_recargar = tk.Button(
            self, 
            text="Recargar Billetera", 
            font=("Segoe UI", 10, "bold"), 
            bg="#2E7D32", 
            fg="white", 
            relief="flat", 
            activebackground="#1B5E20", 
            activeforeground="white",
            pady=6,
            cursor="hand2",
            command=self.abrir_recarga
        )
        self.btn_recargar.pack(fill=tk.X, pady=(0, 15))
        # ANIMACIÓN HOVER: Enlaza eventos nativos del cursor del mouse para crear dinamismo visual
        self.btn_recargar.bind("<Enter>", lambda e: self.btn_recargar.config(bg="#388E3C"))
        self.btn_recargar.bind("<Leave>", lambda e: self.btn_recargar.config(bg="#2E7D32"))
        
        # --- Botón 2: Abrir Tienda / Snacks ---
        # Dispara el Punto de Venta (POS) transaccional pasándole la función refrescar_interfaz como callback.
        self.btn_tienda = tk.Button(
            self, 
            text="🛒 Abrir Tienda / Snacks", 
            font=("Segoe UI", 11, "bold"), 
            bg="#1565C0", 
            fg="white", 
            pady=10, 
            relief="flat", 
            activebackground="#0D47A1", 
            activeforeground="white",
            cursor="hand2",
            command=self.abrir_tienda
        )
        self.btn_tienda.pack(fill=tk.X, pady=(0, 20))
        self.btn_tienda.bind("<Enter>", lambda e: self.btn_tienda.config(bg="#1E88E5"))
        self.btn_tienda.bind("<Leave>", lambda e: self.btn_tienda.config(bg="#1565C0"))
        
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
        
    def abrir_recarga(self):
        """Verifica si el usuario está activo antes de instanciar la VentanaRecarga"""
        usuario = self.controlador.usuario_activo
        if usuario.estado == 0:
            messagebox.showwarning(
                "Acción denegada",
                f"El gamer '{usuario.alias_gamer}' está inhabilitado y no puede recargar saldo.",
                parent=self
            )
            return
        VentanaRecarga(self.controlador, usuario, callback_actualizar=self.controlador.refrescar_interfaz)

    def abrir_tienda(self):
        """Verifica si el usuario está activo antes de instanciar la VentanaTienda"""
        usuario = self.controlador.usuario_activo
        if usuario.estado == 0:
            messagebox.showwarning(
                "Acción denegada",
                f"El gamer '{usuario.alias_gamer}' está inhabilitado y no puede abrir la tienda.",
                parent=self
            )
            return
        VentanaTienda(self.controlador, usuario, callback_actualizar_panel=self.controlador.refrescar_interfaz)
     
        
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