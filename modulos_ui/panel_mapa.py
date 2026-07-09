import tkinter as tk

# --- PALETA MODO OSCURO ---
BG_BASE = "#121212"
BG_PANEL = "#1E1E1E"
TEXTO_MAIN = "#FFFFFF"
TEXTO_SECUNDARIO = "#A0A0A0"
COLOR_DISPONIBLE = "#00E676"
COLOR_OCUPADA = "#FF1744"
COLOR_MANTENIMIENTO = "#FF9100"
BG_BOTON = "#2C2C2C"

class PanelMapa(tk.Frame):
    def __init__(self, parent, controlador, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controlador = controlador # Referencia al main.py
        self.config(bg=BG_BASE)
        self.labels_cronometros = {}
        self.dibujar_mapa_pcs()

    def dibujar_mapa_pcs(self):
        # Limpiamos el frame por si se está refrescando
        for widget in self.winfo_children():
            widget.destroy()

        columnas_maximas = 3
        
        for index, pc in enumerate(self.controlador.lista_pcs):
            fila = index // columnas_maximas
            columna = index % columnas_maximas
            
            if pc.estado == "Disponible":
                color_borde = COLOR_DISPONIBLE
                texto_boton = "Asignar"
                estado_boton = tk.NORMAL
                comando_btn = lambda maquina=pc: self.controlador.iniciar_sesion(maquina)
            elif pc.estado == "Mantenimiento":
                color_borde = COLOR_MANTENIMIENTO
                texto_boton = "En Mantenimiento"
                estado_boton = tk.DISABLED
                comando_btn = lambda: None
            else:
                color_borde = COLOR_OCUPADA
                texto_boton = "Cerrar Sesión"
                estado_boton = tk.NORMAL
                comando_btn = lambda maquina=pc: self.controlador.cerrar_sesion(maquina) 
                
            frame_pc = tk.Frame(self, bg=BG_PANEL, highlightbackground=color_borde, highlightthickness=2, padx=10, pady=10)
            frame_pc.grid(row=fila, column=columna, padx=15, pady=15)
            
            tk.Label(frame_pc, text=pc.codigo_pc, font=("Arial", 12, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack()
            tk.Label(frame_pc, text=pc.categoria, font=("Arial", 9), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack()
            tk.Label(frame_pc, text=pc.estado, font=("Arial", 10, "bold"), bg=BG_PANEL, fg=color_borde).pack(pady=5)
            
            lbl_tiempo = tk.Label(frame_pc, text="", font=("Courier", 11, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN)
            lbl_tiempo.pack(pady=(0, 5))
            self.labels_cronometros[pc.id_estacion] = lbl_tiempo
             
            btn_accion = tk.Button(frame_pc, text=texto_boton, bg=BG_BOTON, fg=TEXTO_MAIN, activebackground=color_borde, activeforeground="black", relief="flat", state=estado_boton, command=comando_btn)
            btn_accion.pack(pady=5)