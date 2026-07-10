import tkinter as tk
import os
from tkinter import ttk
from PIL import Image, ImageTk

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

    # Canvas y barras de desplazamiento
        self.canvas = tk.Canvas(self, bg=BG_BASE, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        
        # Vincular el Canvas con el Scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Empaquetar widgets
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Contenedor INTERIOR (Donde se dibujarán las tarjetas)
        self.frame_interior = tk.Frame(self.canvas, bg=BG_BASE)
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.frame_interior, anchor="nw")

        # Eventos para redimensionar y calcular scroll
        self.frame_interior.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_frame_id, width=e.width))

        # Rueda del mouse (MouseWheel): Asegura el foco para que funcione bien
        self.canvas.bind("<Enter>", lambda _: self.canvas.focus_set())
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.dibujar_mapa_pcs()

    def dibujar_mapa_pcs(self):
        # Limpiamos el frame por si se está refrescando
        for widget in self.frame_interior.winfo_children():
            widget.destroy()

        self.imagenes_referecia = [] # Lista para mantener referencias a las imágenes y evitar que se recojan por el GC

        columnas_maximas = 3
        
        # Configurar columnas para que se expandan proporcionalmente
        for col in range(columnas_maximas):
            self.frame_interior.columnconfigure(col, weight=1)
        
        # Agrupar por filas para configurar sus pesos también
        total_pcs = len(self.controlador.lista_pcs)
        total_filas = (total_pcs + columnas_maximas - 1) // columnas_maximas
        for fila_idx in range(total_filas):
            self.frame_interior.rowconfigure(fila_idx, weight=1)

        for index, pc in enumerate(self.controlador.lista_pcs):
            fila = index // columnas_maximas
            columna = index % columnas_maximas
            
            # 1. COLORES POR CATEGORÍA (Para el borde y el título)
            if pc.categoria == "Streaming VIP":
                color_categoria = "#FFCA28"  # Dorado VIP
            elif pc.categoria == "eSports":
                color_categoria = "#B388FF"  # Morado Neón
            else:
                color_categoria = "#29B6F6"  # Azul Regular
            
            # 2. LÓGICA DE ESTADOS (Para el texto de estado y los botones)
            if pc.estado == "Disponible":
                color_estado = COLOR_DISPONIBLE
                texto_boton = "Asignar PC"
                estado_boton = tk.NORMAL
                bg_btn_color = "#1B5E20"
                hover_btn_color = COLOR_DISPONIBLE
                comando_btn = lambda maquina=pc: self.controlador.iniciar_sesion(maquina)
            elif pc.estado == "Mantenimiento":
                color_estado = COLOR_MANTENIMIENTO
                texto_boton = "En Soporte"
                estado_boton = tk.DISABLED
                bg_btn_color = BG_BOTON
                hover_btn_color = BG_BOTON
                comando_btn = lambda: None
            else:
                color_estado = COLOR_OCUPADA
                texto_boton = "Finalizar Turno"
                estado_boton = tk.NORMAL
                bg_btn_color = "#B71C1C"
                hover_btn_color = COLOR_OCUPADA
                comando_btn = lambda maquina=pc: self.controlador.cerrar_sesion(maquina)
                
            # Frame de la PC individual (Tarjeta) con sticky="nsew" para tamaño homogéneo
            frame_pc = tk.Frame(
                self.frame_interior, 
                bg=BG_PANEL, 
                highlightbackground=color_categoria, #Cambio de color del borde
                highlightthickness=2, 
                padx=15, 
                pady=15
            )
            frame_pc.grid(row=fila, column=columna, padx=12, pady=12, sticky="nsew")
            
            ruta_especifica = f"assets/{pc.codigo_pc}.png"
            ruta_default = f"assets/{pc.categoria.replace(' ', '_').lower()}.png"
            
            ruta_final = ruta_especifica if os.path.exists(ruta_especifica) else ruta_default if os.path.exists(ruta_default) else None
            if ruta_final:
                try:
                    img_original = Image.open(ruta_final)
                    img_redimensionada = img_original.resize((140, 90), Image.Resampling.LANCZOS)
                    foto = ImageTk.PhotoImage(img_redimensionada)
                    
                    lbl_imagen = tk.Label(frame_pc, image=foto, bg=BG_PANEL)
                    lbl_imagen.image = foto  # Mantener referencia
                    lbl_imagen.pack(pady=(0, 10))
                    self.imagenes_referecia.append(foto)  # Evitar recolección
                except Exception as e:
                    print(f"Error cargando imagen para {pc.codigo_pc}: {e}")
                    tk.Frame(frame_pc, bg=BG_BOTON, width=140, height=90).pack(pady=(0, 10))            
            else:
                tk.Frame(frame_pc, bg=BG_BOTON, width=140, height=90).pack(pady=(0, 10))
            
            # Etiquetas informativas
            tk.Label(frame_pc, text=pc.codigo_pc, font=("Segoe UI", 13, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(pady=(0, 2))
            tk.Label(frame_pc, text=pc.categoria.upper(), font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=color_categoria).pack()
            
            # --- MEJORA DE UI: Especificaciones limpias sin recortes ---
            if hasattr(pc, 'especificaciones') and pc.especificaciones:
                cpu = pc.especificaciones.get('procesador', '')
                monitor = pc.especificaciones.get('monitor', '')
                specs_texto = f"💻 {cpu}\n🖥️ {monitor}"
                
                tk.Label(
                    frame_pc, 
                    text=specs_texto, 
                    font=("Segoe UI", 8), 
                    bg=BG_PANEL, 
                    fg=TEXTO_SECUNDARIO,
                    justify="center",
                    wraplength=170 
                ).pack(pady=(2, 5))
            # -----------------------------------------------------------
            
            tk.Label(frame_pc, text=pc.estado, font=("Segoe UI", 11, "bold"), bg=BG_PANEL, fg=color_estado).pack(pady=5)
                        
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
