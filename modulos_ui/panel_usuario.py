import tkinter as tk
from tkinter import ttk
from conexion import DBManager
from modulos_ui.ventanas_emergentes import VentanaRegistro, VentanaRecarga, VentanaReporteCaja
from modulos_ui.panel_kiosco import VentanaTienda

# --- PALETA MODO OSCURO ---
BG_PANEL = "#1E1E1E"
TEXTO_MAIN = "#FFFFFF"
TEXTO_SECUNDARIO = "#A0A0A0"
COLOR_DISPONIBLE = "#00E676"

class PanelUsuario(tk.LabelFrame):
    def __init__(self, parent, controlador, *args, **kwargs):
        super().__init__(parent, text="Módulo del Cliente", font=("Segoe UI", 12, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN, padx=20, pady=20, *args, **kwargs)
        self.controlador = controlador
        self.dibujar_panel()

    def dibujar_panel(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        usuario = self.controlador.usuario_activo
        
        frame_seleccion = tk.Frame(self, bg=BG_PANEL)
        frame_seleccion.pack(fill=tk.X, pady=(0,15))
        
        tk.Label(frame_seleccion, text="Seleccionar Cliente:", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="w")
        
        db = DBManager()
        todos_los_usuarios = db.obtener_todos_los_usuarios()
        
        lista_nombres = [f"{u['id_usuario']} - {u['alias_gamer']}" for u in todos_los_usuarios]
        self.combo_usuarios = ttk.Combobox(frame_seleccion, values=lista_nombres, state="readonly", font=("Segoe UI", 11))
        self.combo_usuarios.pack(fill=tk.X, pady=5)
        self.combo_usuarios.set(f"{usuario.id_usuario} - {usuario.alias_gamer}") 
        
        self.combo_usuarios.bind("<<ComboboxSelected>>", self.controlador.cambiar_usuario_activo)
        
        tk.Label(self, text="Gamer:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        tk.Label(self, text=usuario.alias_gamer, font=("Segoe UI", 14, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="w", pady=(0, 15))
        
        tk.Label(self, text="Rango:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        
        colores_rango = {
            "Bronce": "#CD7F32",     # Color cobre/bronce
            "Plata": "#E0E0E0",      # Gris plateado brillante
            "Oro": "#FFD700",        # Dorado intenso
            "Global VIP": "#B388FF"  # Morado neón (Premium)
        }
        color_rango = colores_rango.get(usuario.rango_cuenta, TEXTO_MAIN)
        
        tk.Label(self, text=usuario.rango_cuenta, font=("Segoe UI", 14, "bold"), bg=BG_PANEL, fg=color_rango).pack(anchor="w", pady=(0, 15))
        
        tk.Label(self, text="Saldo Disponible:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        tk.Label(self, text=f"S/ {usuario.saldo_billetera:.2f}", font=("Segoe UI", 18, "bold"), bg=BG_PANEL, fg=COLOR_DISPONIBLE).pack(anchor="w", pady=(0, 20))
        
        # --- BOTONES MODERNOS CON HOVER ---
        
        # Botón 1: Recargar Billetera
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
            command=lambda: VentanaRecarga(self.controlador, self.controlador.usuario_activo, callback_actualizar=self.controlador.refrescar_interfaz)
        )
        self.btn_recargar.pack(fill=tk.X, pady=(0, 15))
        self.btn_recargar.bind("<Enter>", lambda e: self.btn_recargar.config(bg="#388E3C"))
        self.btn_recargar.bind("<Leave>", lambda e: self.btn_recargar.config(bg="#2E7D32"))
        
        # Botón 2: Abrir Tienda / Snacks
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
            command=lambda: VentanaTienda(self.controlador, usuario, callback_actualizar_panel=self.controlador.refrescar_interfaz)
        )
        self.btn_tienda.pack(fill=tk.X, pady=(0, 20))
        self.btn_tienda.bind("<Enter>", lambda e: self.btn_tienda.config(bg="#1E88E5"))
        self.btn_tienda.bind("<Leave>", lambda e: self.btn_tienda.config(bg="#1565C0"))
        
        # Botón 3: Registrar nuevo Usuario
        self.btn_registro = tk.Button(
            self, 
            text="➕ Registrar nuevo Usuario", 
            font=("Segoe UI", 10, "bold"), 
            bg="#6A1B9A", 
            fg="white", 
            relief="flat", 
            activebackground="#4A148C", 
            activeforeground="white",
            pady=6,
            cursor="hand2",
            command=lambda: VentanaRegistro(self.controlador, callback_actualizar=self.controlador.refrescar_interfaz)
        )
        self.btn_registro.pack(fill=tk.X, pady=(0, 15))
        self.btn_registro.bind("<Enter>", lambda e: self.btn_registro.config(bg="#8E24AA"))
        self.btn_registro.bind("<Leave>", lambda e: self.btn_registro.config(bg="#6A1B9A"))
        
        # Botón 4: Reporte de Caja
        self.btn_reporte = tk.Button(
            self, 
            text="📊 Reporte de Caja (Hoy)", 
            font=("Segoe UI", 10, "bold"), 
            bg="#E65100", 
            fg="white", 
            relief="flat", 
            activebackground="#BF360C", 
            activeforeground="white",
            pady=6,
            cursor="hand2",
            command=lambda: VentanaReporteCaja(self.controlador)
        )
        self.btn_reporte.pack(fill=tk.X)
        self.btn_reporte.bind("<Enter>", lambda e: self.btn_reporte.config(bg="#F57C00"))
        self.btn_reporte.bind("<Leave>", lambda e: self.btn_reporte.config(bg="#E65100"))
