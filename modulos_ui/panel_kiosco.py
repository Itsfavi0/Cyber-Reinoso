import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
from conexion import DBManager

# ---PALETA DE COLORES ---
BG_BASE = "#121212"
BG_PANEL = "#1E1E1E"
TEXTO_MAIN = "#FFFFFF"
TEXTO_SECUNDARIO = "#A0A0A0"
BG_BOTON = "#2C2C2C"
COLOR_ACCION = "#1565C0"
COLOR_QUITAR = "#C62828"
COLOR_PAGO = "#2E7D32"

class VentanaTienda(tk.Toplevel):
    def __init__(self, parent, usuario_actual, callback_actualizar_panel):
        super().__init__(parent)
        self.usuario_actual = usuario_actual
        self.callback_actualizar_panel = callback_actualizar_panel
        
        self.carrito = {} 
        self.total_carrito = 0.0
        
        self.title(f"Tienda y Snacks - Atendiendo a {self.usuario_actual.alias_gamer}")
        self.geometry("900x600")
        self.config(bg=BG_BASE)
        self.grab_set() 
        
        # Magia de UI: Aplicar estilo oscuro nativo a la tabla (Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=BG_PANEL, foreground=TEXTO_MAIN, fieldbackground=BG_PANEL, borderwidth=0)
        style.configure("Treeview.Heading", background=BG_BOTON, foreground=TEXTO_MAIN, relief="flat")
        style.map("Treeview", background=[('selected', '#34495E')])
        
        db = DBManager()
        self.lista_productos = db.obtener_productos()
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        # --- ZONA IZQUIERDA: CATÁLOGO ---
        frame_izquierdo = tk.Frame(self, bg=BG_BASE)
        frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame_izquierdo, text="🛒 Catálogo de Productos", font=("Arial", 14, "bold"), bg=BG_BASE, fg=TEXTO_MAIN).pack(anchor="w", pady=(0, 10))
        
        canvas = tk.Canvas(frame_izquierdo, bg=BG_BASE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_izquierdo, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=BG_BASE)
        
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.dibujar_tarjetas_productos()
        
        # --- ZONA DERECHA: CARRITO ---
        frame_derecho = tk.Frame(self, bg=BG_PANEL, bd=1, relief="ridge", width=350)
        frame_derecho.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        frame_derecho.pack_propagate(False)
        
        tk.Label(frame_derecho, text="🛍️ Carrito de Compras", font=("Arial", 12, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(pady=10)
        
        columnas = ("Producto", "Cant", "Subtotal")
        self.tree_carrito = ttk.Treeview(frame_derecho, columns=columnas, show="headings", height=15)
        self.tree_carrito.heading("Producto", text="Producto")
        self.tree_carrito.heading("Cant", text="Cant")
        self.tree_carrito.heading("Subtotal", text="Subtotal")
        
        self.tree_carrito.column("Producto", width=160)
        self.tree_carrito.column("Cant", width=40, anchor="center")
        self.tree_carrito.column("Subtotal", width=80, anchor="e")
        self.tree_carrito.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.btn_quitar = tk.Button(frame_derecho, text="❌ Quitar Seleccionado", font=("Arial", 9, "bold"), bg="#5C1010", fg="#FFCDD2", relief="flat", command=self.quitar_del_carrito)
        self.btn_quitar.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        self.lbl_total = tk.Label(frame_derecho, text="Total (Inc. IGV): S/ 0.00", font=("Arial", 14, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN)
        self.lbl_total.pack(pady=15)
        
        self.lbl_saldo_disp = tk.Label(frame_derecho, text=f"Saldo Billetera: S/ {self.usuario_actual.saldo_billetera:.2f}", font=("Arial", 10), bg=BG_PANEL, fg=TEXTO_SECUNDARIO)
        self.lbl_saldo_disp.pack(pady=(0, 10))
        
        self.btn_pagar = tk.Button(frame_derecho, text="Procesar Pago", font=("Arial", 12, "bold"), bg=BG_BOTON, fg=TEXTO_SECUNDARIO, relief="flat", state=tk.DISABLED, command=self.procesar_pago_lote)
        self.btn_pagar.pack(fill=tk.X, padx=20, pady=10)

    def dibujar_tarjetas_productos(self):
        columnas_maximas = 3
        self.imagenes_referencia = []
        
        for index, prod in enumerate(self.lista_productos):
            fila = index // columnas_maximas
            columna = index % columnas_maximas
            
            card = tk.Frame(self.scrollable_frame, bg=BG_PANEL, bd=1, relief="ridge", padx=10, pady=10)
            card.grid(row=fila, column=columna, padx=10, pady=10, sticky="nsew")
            
            ruta_imagen = f"assets/{prod['id_producto']}.png"
            
            try:
                if os.path.exists(ruta_imagen):
                    img_original = Image.open(ruta_imagen)
                    img_redimensionada = img_original.resize((100,80), Image.Resampling.LANCZOS)
                    foto = ImageTk.PhotoImage(img_redimensionada)
                    
                    lbl_imagen = tk.Label(card, image=foto, bg=BG_PANEL)
                    lbl_imagen.image = foto
                    lbl_imagen.pack(pady=(0,10))
                    self.imagenes_referencia.append(foto)
                else:
                    #Cuadro gris si no hay imagen
                    tk.Frame(card, bg=BG_BOTON, width=100, height=80).pack(pady=(0, 10))
            except Exception as e:
                print(f"Error cargando imagen para {prod['nombre_producto']}: {e}")
                tk.Frame(card, bg=BG_BOTON, width=100, height=80).pack(pady=(0, 10))
            
            #tk.Frame(card, bg=BG_BOTON, width=100, height=80).pack(pady=(0, 10))
            
            tk.Label(card, text=prod["nombre_producto"], font=("Arial", 10, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN, wraplength=120).pack()
            tk.Label(card, text=f"S/ {prod['precio']:.2f}", font=("Arial", 12, "bold"), bg=BG_PANEL, fg="#81C784").pack(pady=2)
            
            estado_stock = f"Stock: {prod['stock']}"
            color_stock = TEXTO_SECUNDARIO if prod['stock'] > 0 else "#E57373"
            tk.Label(card, text=estado_stock, font=("Arial", 9), bg=BG_PANEL, fg=color_stock).pack(pady=(0, 10))
            
            estado_btn = tk.NORMAL if prod['stock'] > 0 else tk.DISABLED
            bg_btn_actual = COLOR_ACCION if prod['stock'] > 0 else BG_BOTON
            tk.Button(card, text="Agregar", bg=bg_btn_actual, fg="white", relief="flat", state=estado_btn, command=lambda p=prod: self.agregar_al_carrito(p)).pack(fill=tk.X)

    def agregar_al_carrito(self, producto):
        id_prod = producto["id_producto"]
        
        # Validar que no exceda el stock real
        cant_actual = self.carrito.get(id_prod, {}).get("cantidad", 0)
        if cant_actual >= producto["stock"]:
            messagebox.showwarning("Stock Insuficiente", "No hay más unidades disponibles de este producto.", parent=self)
            return

        if id_prod in self.carrito:
            self.carrito[id_prod]["cantidad"] += 1
        else:
            self.carrito[id_prod] = {
                "nombre": producto["nombre_producto"],
                "precio": producto["precio"],
                "cantidad": 1
            }
            
        self.actualizar_vista_carrito()

    def actualizar_vista_carrito(self):
        # Limpiar tabla
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
            
        self.total_carrito = 0.0
        
        for id_prod, datos in self.carrito.items():
            subtotal = datos["precio"] * datos["cantidad"]
            self.total_carrito += subtotal
            # NUEVO: Le inyectamos el id_prod al parámetro 'iid' (Internal ID)
            self.tree_carrito.insert("", "end", iid=id_prod, values=(datos["nombre"], datos["cantidad"], f"S/ {subtotal:.2f}"))
            
        self.lbl_total.config(text=f"Total (Inc. IGV): S/ {self.total_carrito:.2f}")
        
        # Dinamismo de color en el botón de pago
        if self.total_carrito > 0 and self.total_carrito <= self.usuario_actual.saldo_billetera:
            self.btn_pagar.config(state=tk.NORMAL, bg=COLOR_PAGO, fg="white")
            self.lbl_total.config(fg="#81C784")
        else:
            self.btn_pagar.config(state=tk.DISABLED, bg=BG_BOTON, fg=TEXTO_SECUNDARIO)
            self.lbl_total.config(fg="#E57373" if self.total_carrito > self.usuario_actual.saldo_billetera else TEXTO_MAIN)

    def quitar_del_carrito(self):
        seleccion = self.tree_carrito.selection()
        
        if not seleccion:
            messagebox.showwarning("Selección vacía", "Primero haz clic en un producto del carrito para poder quitarlo.", parent=self)
            return
            
        id_prod = int(seleccion[0]) 
        
        if self.carrito[id_prod]["cantidad"] > 1:
            self.carrito[id_prod]["cantidad"] -= 1
        else:
            del self.carrito[id_prod]
            
        # Recalculamos toda la tabla y los botones mágicamente
        self.actualizar_vista_carrito()

    def procesar_pago_lote(self):
        # 1. Descuento en el objeto de memoria
        self.usuario_actual.descontar_saldo(self.total_carrito)
        db = DBManager()
        # 2. Actualizar saldo en BD
        db.actualizar_saldo_usuario(self.usuario_actual.id_usuario, self.usuario_actual.saldo_billetera)
        
        for id_prod, datos in self.carrito.items():
            for _ in range(datos["cantidad"]):
                db.restar_stock_producto(datos["nombre"])
                db.registrar_venta_tienda(self.usuario_actual.id_usuario, id_prod, datos["precio"])
        
        messagebox.showinfo("Compra Exitosa", f"Transacción completada.\nTotal cobrado: S/ {self.total_carrito:.2f}\nNuevo saldo: S/ {self.usuario_actual.saldo_billetera:.2f}", parent=self)
        
        if self.callback_actualizar_panel:
            self.callback_actualizar_panel()
            
        self.destroy()