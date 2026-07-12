"""
CAPA DE PRESENTACIÓN / INTERFAZ GRÁFICA (UI)
MÓDULO DE INFRAESTRUCTURA: PANEL MAPA (DYNAMIC GRID CONTROLLER)
Este componente visual hereda de tk.Frame y encapsula la representación física de las 12 estaciones
del Lan Center. Utiliza una técnica combinada de Canvas + Scrollbar para generar una grilla responsiva,
tolerante a fallos de hardware (Módulos Vacíos) y con renderizado en tiempo real de estados operativos.
"""

import tkinter as tk
import os
from tkinter import ttk
from PIL import Image, ImageTk

# --- PALETA MODO OSCURO ---
BG_BASE = "#121212"
BG_PANEL = "#1E1E1E"
TEXTO_MAIN = "#FFFFFF"
TEXTO_SECUNDARIO = "#A0A0A0"
COLOR_DISPONIBLE = "#00E676"      # Verde Neón para sesiones libres
COLOR_OCUPADA = "#FF1744"         # Rojo Alerta para turnos activos
COLOR_MANTENIMIENTO = "#FF9100"   # Naranja Soporte
BG_BOTON = "#2C2C2C"

class PanelMapa(tk.Frame):
    def __init__(self, parent, controlador, *args, **kwargs):
        """
        CONSTRUCTOR DEL MAPA: Configura el lienzo desplazable y los registros visuales.
        - parent: Contenedor principal de la ventana (AppCyberReinoso).
        - controlador: Instancia del mediador principal para delegar acciones transaccionales (Login/Logout).
        """
        super().__init__(parent, *args, **kwargs)
        self.controlador = controlador # Referencia al main.py
        self.config(bg=BG_BASE)
        
        # DICCIONARIO DE CONCURRENCIA VISUAL:
        # Almacena en RAM los widgets tk.Label del cronómetro (Llave: id_estacion | Valor: Label).
        # Permite que el bucle asíncrono de main.py actualice el tiempo segundo a segundo sin redibujar toda la pantalla.
        self.labels_cronometros = {}

        # ---------------------------------------------------------------------
        # ARQUITECTURA DE SCROLLING RESPONSIVO
        # ---------------------------------------------------------------------
        # tk.Canvas es el único widget de Tkinter capaz de actuar como una "ventana infinita" scrolleable.
        self.canvas = tk.Canvas(self, bg=BG_BASE, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        
        # Sincronización bidireccional entre la barra de scroll y el movimiento del lienzo
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Empaquetamiento perimetral
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Contenedor INTERIOR: Un Frame real que vive *dentro* del Canvas donde se apilarán las tarjetas Grid
        self.frame_interior = tk.Frame(self.canvas, bg=BG_BASE)
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.frame_interior, anchor="nw")

        # EVENTOS DINÁMICOS DE SCROLL (RESIZE BINDINGS):
        # 1. <Configure> en frame_interior: Si añadimos más PCs, recalcula la altura máxima del scroll (scrollregion).
        # 2. <Configure> en canvas: Si el operario agranda la ventana de Windows, estira el frame interior al nuevo ancho.
        self.frame_interior.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_frame_id, width=e.width))

        # UX DE DESPLAZAMIENTO CON MOUSE: Captura la rueda de scroll (MouseWheel) en toda el área visual
        self.canvas.bind("<Enter>", lambda _: self.canvas.focus_set())
        # int(-1 * (e.delta / 120)) normaliza la velocidad de giro de la rueda del ratón en Windows.
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Renderiza la grilla física al inicializar la aplicación
        self.dibujar_mapa_pcs()

    def dibujar_mapa_pcs(self):
        """
        MOTOR DE RENDERIZADO DE LA GRILLA (CARD-BASED UI ENGINE):
        Limpia el contenedor gráfico, calcula la distribución simétrica de columnas y filas, 
        y genera las tarjetas de estado para cada máquina normalizada en SQL Server.
        """
        # Limpiamos los widgets previos para evitar superposiciones al refrescar
        for widget in self.frame_interior.winfo_children():
            widget.destroy()

        # Lista obligatoria para evitar que el Garbage Collector
        # de Python borre las fotos de la memoria RAM al terminar de ejecutarse el método.
        self.imagenes_referecia = [] 

        columnas_maximas = 3
        
        # MATEMÁTICA DE GRILLA RESPONSIVA:
        # columnconfigure con weight=1 obliga a que las 3 columnas tengan exactamente el mismo ancho,
        # expandiéndose de forma simétrica si el monitor es Ultra-Wide o Full HD.
        for col in range(columnas_maximas):
            self.frame_interior.columnconfigure(col, weight=1)
        
        # rowconfigure con weight=1 garantiza que las tarjetas compartan la misma altura por fila
        total_pcs = len(self.controlador.lista_pcs)
        total_filas = (total_pcs + columnas_maximas - 1) // columnas_maximas
        for fila_idx in range(total_filas):
            self.frame_interior.rowconfigure(fila_idx, weight=1)

        # ITERACIÓN Y RENDERIZADO DE LAS ESTACIONES LOGICAS
        for index, pc in enumerate(self.controlador.lista_pcs):
            # Coordenadas matriciales del Grid (Fila, Columna)
            fila = index // columnas_maximas
            columna = index % columnas_maximas
            
            # --- 1. DETECCIÓN DE MÓDULO VACÍO ---
            # Si el administrador eliminó la computadora física en el CRUD, la llave foránea es NULL.
            # El frontend lo detecta y adapta visualmente la mesa sin romper la continuidad del mapa.
            es_modulo_vacio = (pc.codigo_pc is None or pc.codigo_pc == "None")
            
            # --- 2. CODIFICACIÓN VISUAL POR CATEGORÍA (Branding de Bordes) ---
            if pc.categoria == "Streaming VIP":
                color_categoria = "#FFCA28"  # Dorado VIP
            elif pc.categoria == "eSports":
                color_categoria = "#B388FF"  # Morado Neón
            else:
                color_categoria = "#29B6F6"  # Azul Regular
            
            # --- 3. LÓGICA DE COMANDOS Y ESTADOS OPERATIVOS ---
            if es_modulo_vacio:
                color_estado = "#555555" # Gris inactivo
                texto_estado = "Deshabilitado"
                texto_boton = "Sin Equipo"
                estado_boton = tk.DISABLED
                bg_btn_color = BG_BOTON
                hover_btn_color = BG_BOTON
                comando_btn = lambda: None # Función vacía
            elif pc.estado == "Disponible":
                color_estado = COLOR_DISPONIBLE
                texto_boton = "Asignar PC"
                estado_boton = tk.NORMAL
                bg_btn_color = "#1B5E20"
                hover_btn_color = COLOR_DISPONIBLE
                # CLAUSURA: Inyecta el objeto PC actual en la función de apertura de sesión
                comando_btn = lambda maquina=pc: self.controlador.iniciar_sesion(maquina)
            elif pc.estado == "Mantenimiento":
                color_estado = COLOR_MANTENIMIENTO
                texto_boton = "En Soporte"
                estado_boton = tk.DISABLED
                bg_btn_color = BG_BOTON
                hover_btn_color = BG_BOTON
                comando_btn = lambda: None
            else: # Estado Ocupada
                color_estado = COLOR_OCUPADA
                texto_boton = "Finalizar Turno"
                estado_boton = tk.NORMAL
                bg_btn_color = "#B71C1C"
                hover_btn_color = COLOR_OCUPADA
                # CLAUSURA: Delega el cierre transaccional de caja al controlador
                comando_btn = lambda maquina=pc: self.controlador.cerrar_sesion(maquina)
                
            # --- CREACIÓN DEL CONTENEDOR DE TARJETA (CARD FRAME) ---
            # sticky="nsew" (North, South, East, West) obliga al frame a estirar sus 4 bordes para llenar la celda de la grilla
            frame_pc = tk.Frame(
                self.frame_interior, 
                bg=BG_PANEL, 
                highlightbackground=color_categoria, # Borde iluminado según el rango de la máquina
                highlightthickness=2, 
                padx=15, 
                pady=15
            )
            frame_pc.grid(row=fila, column=columna, padx=12, pady=12, sticky="nsew")
            
            # --- 4. GESTIÓN Y CARGA DE IMÁGENES (SISTEMA FALLBACK) ---
            # Busca foto específica de la PC (ej: PC-001.png). Si no existe, usa la foto general (ej: regular.png).
            ruta_final = None
            if not es_modulo_vacio:
                ruta_especifica = f"assets/{pc.codigo_pc}.png"
                ruta_default = f"assets/imagen_pc_defecto.png"
                ruta_final = ruta_especifica if os.path.exists(ruta_especifica) else ruta_default if os.path.exists(ruta_default) else None
            
            if ruta_final:
                try:
                    img_original = Image.open(ruta_final)
                    img_redimensionada = img_original.resize((140, 90), Image.Resampling.LANCZOS)
                    foto = ImageTk.PhotoImage(img_redimensionada)
                    
                    lbl_imagen = tk.Label(frame_pc, image=foto, bg=BG_PANEL)
                    lbl_imagen.image = foto # Anclaje contra la recolección de basura
                    lbl_imagen.pack(pady=(0, 10))
                    self.imagenes_referecia.append(foto)
                except Exception as e:
                    print(f"Error cargando imagen para {pc.codigo_pc}: {e}")
                    tk.Frame(frame_pc, bg=BG_BOTON, width=140, height=90).pack(pady=(0, 10))            
            else:
                # Contenedor gris por defecto si la mesa está vacía o sin fotos en assets
                tk.Frame(frame_pc, bg=BG_BOTON, width=140, height=90).pack(pady=(0, 10))
            
            # --- 5. ETIQUETAS Y ESPECIFICACIONES TÉCNICAS ---
            titulo_pc = "MÓDULO VACÍO" if es_modulo_vacio else pc.codigo_pc
            tk.Label(frame_pc, text=titulo_pc, font=("Segoe UI", 13, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(pady=(0, 2))
            tk.Label(frame_pc, text=pc.categoria.upper(), font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=color_categoria).pack()
            
            # Formateo de las 4 líneas vitales del hardware (CPU, RAM, GPU, Monitor)
            if es_modulo_vacio:
                specs_texto = "⚠️\nSin hardware asignado\nMesa inoperativa"
            elif hasattr(pc, 'especificaciones') and pc.especificaciones:
                cpu = pc.especificaciones.get('procesador', 'No Disp.')
                ram = pc.especificaciones.get("ram", "No Disp.")
                gpu = pc.especificaciones.get("tarjeta_grafica", "No Disp.")
                monitor = pc.especificaciones.get('monitor', 'No Disp.')
                specs_texto = f"💻 {cpu}\n⚡ {ram}\n🎮 {gpu}\n🖥️ {monitor}"
            else:
                specs_texto = "Sin Especificaciones"
                
            # wraplength=175 hace un salto de línea automático si el nombre de una tarjeta de video es muy largo
            tk.Label(
                frame_pc, 
                text=specs_texto, 
                font=("Segoe UI", 8), 
                bg=BG_PANEL, 
                fg=TEXTO_SECUNDARIO,
                justify="center",
                wraplength=175
            ).pack(pady=(2, 5))
            
            # Indicador textual del estado actual
            tk.Label(frame_pc, text=pc.estado, font=("Segoe UI", 11, "bold"), bg=BG_PANEL, fg=color_estado).pack(pady=5)
                        
            # --- 6. CRONÓMETRO MONOESPACIADO ---
            # NOTA BÁSICA: Segoe UI Mono o Courier evitan que el texto del reloj "salte" o tiemble en la pantalla 
            # cuando los segundos cambian entre el '1' (que es delgado) y el '8' (que es ancho).
            lbl_tiempo = tk.Label(frame_pc, text="", font=("Segoe UI Mono", 11, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN)
            lbl_tiempo.pack(pady=(0, 10))
            
            # Registramos el label en el diccionario RAM para que main.py lo actualice de forma asíncrona
            self.labels_cronometros[pc.id_estacion] = lbl_tiempo
             
            # --- 7. BOTÓN DE ACCIÓN CON HOVER Y FEEDBACK VISUAL ---
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
            
            # ENLACE DE EVENTOS HOVER: Si el botón es interactivo, cambiamos su color cuando el cursor pasa por encima
            if estado_boton == tk.NORMAL:
                btn_accion.bind("<Enter>", lambda e, b=btn_accion, h=hover_btn_color: b.config(bg=h, fg="black"))
                btn_accion.bind("<Leave>", lambda e, b=btn_accion, n=bg_btn_color: b.config(bg=n, fg=TEXTO_MAIN))