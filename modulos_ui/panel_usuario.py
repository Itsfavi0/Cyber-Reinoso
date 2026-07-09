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
        super().__init__(parent, text="Módulo del Cliente", font=("Arial", 12, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN, padx=20, pady=20, *args, **kwargs)
        self.controlador = controlador
        self.dibujar_panel()

    def dibujar_panel(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        usuario = self.controlador.usuario_prueba
        
        frame_seleccion = tk.Frame(self, bg=BG_PANEL)
        frame_seleccion.pack(fill=tk.X, pady=(0,15))
        
        tk.Label(frame_seleccion, text="Seleccionar Cliente:", font=("Arial", 10, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="w")
        
        db = DBManager()
        todos_los_usuarios = db.obtener_todos_los_usuarios()
        
        lista_nombres = [f"{u['id_usuario']} - {u['alias_gamer']}" for u in todos_los_usuarios]
        self.combo_usuarios = ttk.Combobox(frame_seleccion, values=lista_nombres, state="readonly", font=("Arial", 11))
        self.combo_usuarios.pack(fill=tk.X, pady=5)
        self.combo_usuarios.set(f"{usuario.id_usuario} - {usuario.alias_gamer}") 
        
        self.combo_usuarios.bind("<<ComboboxSelected>>", self.controlador.cambiar_usuario_activo)
        
        tk.Label(self, text="Gamer:", font=("Arial", 10), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        tk.Label(self, text=usuario.alias_gamer, font=("Arial", 14, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="w", pady=(0, 15))
        
        tk.Label(self, text="Rango:", font=("Arial", 10), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        color_rango = "#B388FF" if usuario.rango_cuenta == "VIP" else "#82B1FF"
        tk.Label(self, text=usuario.rango_cuenta, font=("Arial", 14, "bold"), bg=BG_PANEL, fg=color_rango).pack(anchor="w", pady=(0, 15))
        
        tk.Label(self, text="Saldo Disponible:", font=("Arial", 10), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        tk.Label(self, text=f"S/ {usuario.saldo_billetera:.2f}", font=("Arial", 16, "bold"), bg=BG_PANEL, fg=COLOR_DISPONIBLE).pack(anchor="w", pady=(0, 20))
        
        tk.Button(self, text="Recargar Billetera", font=("Arial", 10, "bold"), bg="#2E7D32", fg="white", relief="flat", activebackground="#1B5E20", activeforeground="white", command=lambda: VentanaRecarga(self.controlador, self.controlador.usuario_prueba, callback_actualizar=self.controlador.refrescar_interfaz)).pack(anchor="w", pady=(0, 15))
        tk.Button(self, text="Abrir Tienda / Snacks", font=("Arial", 12, "bold"), bg="#1565C0", fg="white", pady=10, relief="flat", activebackground="#0D47A1", activeforeground="white", command=lambda: VentanaTienda(self.controlador, usuario, callback_actualizar_panel=self.controlador.refrescar_interfaz)).pack(fill=tk.X, padx=10, pady=20)
        tk.Button(self, text="Registrar nuevo Usuario", font=("Arial", 10, "bold"), bg="#6A1B9A", fg="white", relief="flat", activebackground="#4A148C", activeforeground="white", command=lambda: VentanaRegistro(self.controlador, callback_actualizar=self.controlador.refrescar_interfaz)).pack(fill=tk.X, pady=(15,0))
        tk.Button(self, text="Reporte de Caja (Hoy)", font=("Arial", 10, "bold"), bg="#E65100", fg="white", relief="flat", activebackground="#BF360C", activeforeground="white", command=lambda: VentanaReporteCaja(self.controlador)).pack(fill=tk.X, pady=(10, 0))