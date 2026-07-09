import tkinter as tk

# --- PALETA MODO OSCURO COHERENTE ---
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
        
        # Configurar columnas para que se expandan proporcionalmente
        for col in range(columnas_maximas):
            self.columnconfigure(col, weight=1)
        
        # Agrupar por filas para configurar sus pesos también
        total_pcs = len(self.controlador.lista_pcs)
        total_filas = (total_pcs + columnas_maximas - 1) // columnas_maximas
        for fila_idx in range(total_filas):
            self.rowconfigure(fila_idx, weight=1)

        for index, pc in enumerate(self.controlador.lista_pcs):
            fila = index // columnas_maximas
            columna = index % columnas_maximas
            
            if pc.estado == "Disponible":
                color_borde = COLOR_DISPONIBLE
                texto_boton = "Asignar PC"
                estado_boton = tk.NORMAL
                bg_btn_color = "#1B5E20"  # Verde oscuro para asignar
                hover_btn_color = COLOR_DISPONIBLE
                comando_btn = lambda maquina=pc: self.controlador.iniciar_sesion(maquina)
            elif pc.estado == "Mantenimiento":
                color_borde = COLOR_MANTENIMIENTO
                texto_boton = "En Soporte"
                estado_boton = tk.DISABLED
                bg_btn_color = BG_BOTON
                hover_btn_color = BG_BOTON
                comando_btn = lambda: None
            else:
                color_borde = COLOR_OCUPADA
                texto_boton = "Finalizar Turno"
                estado_boton = tk.NORMAL
                bg_btn_color = "#B71C1C"  # Rojo oscuro para terminar
                hover_btn_color = COLOR_OCUPADA
                comando_btn = lambda maquina=pc: self.controlador.cerrar_sesion(maquina) 
                
            # Frame de la PC individual (Tarjeta) con sticky="nsew" para tamaño homogéneo
            frame_pc = tk.Frame(
                self, 
                bg=BG_PANEL, 
                highlightbackground=color_borde, 
                highlightthickness=2, 
                padx=15, 
                pady=15
            )
            frame_pc.grid(row=fila, column=columna, padx=12, pady=12, sticky="nsew")
            
            # Etiquetas informativas
            tk.Label(frame_pc, text=pc.codigo_pc, font=("Segoe UI", 13, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(pady=(0, 2))
            tk.Label(frame_pc, text=pc.categoria.upper(), font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack()
            tk.Label(frame_pc, text=pc.estado, font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=color_borde).pack(pady=8)
            
            # Cronómetro con fuente monoespaciada moderna
            lbl_tiempo = tk.Label(frame_pc, text="", font=("Segoe UI Mono", 11, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN)
            lbl_tiempo.pack(pady=(0, 10))
            self.labels_cronometros[pc.id_estacion] = lbl_tiempo
             
            # Botón de acción con estilo y hover moderno
            btn_accion = tk.Button(
                frame_pc, 
                text=texto_boton, 
                bg=bg_btn_color, 
                fg=TEXTO_MAIN, 
                activebackground=hover_btn_color, 
                activeforeground="black", 
                relief="flat", 
                state=estado_boton, 
                font=("Segoe UI", 10, "bold"),
                pady=6,
                cursor="hand2" if estado_boton == tk.NORMAL else "arrow",
                command=comando_btn
            )
            btn_accion.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
            
            # Efectos de hover interactivos
            if estado_boton == tk.NORMAL:
                btn_accion.bind("<Enter>", lambda e, b=btn_accion, h=hover_btn_color: b.config(bg=h, fg="black"))
                btn_accion.bind("<Leave>", lambda e, b=btn_accion, n=bg_btn_color: b.config(bg=n, fg=TEXTO_MAIN))
