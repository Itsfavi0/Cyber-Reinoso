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
        self.geometry("950x650")
        self.config(bg=BG_BASE)
        self.resizable(False, False)
        self.grab_set() 
        
        # Centrar la ventana
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        #Aplicar estilo oscuro nativo a la tabla
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=BG_PANEL, foreground=TEXTO_MAIN, fieldbackground=BG_PANEL, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=BG_BOTON, foreground=TEXTO_MAIN, relief="flat", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[('selected', '#1565C0')], foreground=[('selected', 'white')])
        
        db = DBManager()
        self.lista_productos = db.obtener_productos()
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        # --- ZONA IZQUIERDA: CATÁLOGO ---
        frame_izquierdo = tk.Frame(self, bg=BG_BASE)
        frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tk.Label(frame_izquierdo, text="🛒 Catálogo de Productos", font=("Segoe UI", 16, "bold"), bg=BG_BASE, fg=TEXTO_MAIN).pack(anchor="w", pady=(0, 15))
        
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
        frame_derecho = tk.Frame(self, bg=BG_PANEL, bd=1, highlightbackground="#2C2C2C", highlightthickness=1, width=380)
        frame_derecho.pack(side=tk.RIGHT, fill=tk.Y, padx=15, pady=15)
        frame_derecho.pack_propagate(False)
        
        tk.Label(frame_derecho, text="🛍️ Carrito de Compras", font=("Segoe UI", 14, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(pady=15)
        
        columnas = ("Producto", "Cant", "Subtotal")
        self.tree_carrito = ttk.Treeview(frame_derecho, columns=columnas, show="headings", height=15)
        self.tree_carrito.heading("Producto", text="Producto")
        self.tree_carrito.heading("Cant", text="Cant")
        self.tree_carrito.heading("Subtotal", text="Subtotal")
        
        self.tree_carrito.column("Producto", width=180)
        self.tree_carrito.column("Cant", width=50, anchor="center")
        self.tree_carrito.column("Subtotal", width=90, anchor="e")
        self.tree_carrito.pack(fill=tk.BOTH, expand=True, padx=15)
        
        self.btn_quitar = tk.Button(
            frame_derecho, 
            text="❌ Quitar Seleccionado", 
            font=("Segoe UI", 9, "bold"), 
            bg="#5C1010", 
            fg="#FFCDD2", 
            relief="flat", 
            pady=6,
            cursor="hand2"
        )
        self.btn_quitar.pack(fill=tk.X, padx=20, pady=(15, 0))
        self.btn_quitar.config(command=self.quitar_del_carrito)
        
        # Hover para botón Quitar
        self.btn_quitar.bind("<Enter>", lambda e: self.btn_quitar.config(bg="#7C1A1A"))
        self.btn_quitar.bind("<Leave>", lambda e: self.btn_quitar.config(bg="#5C1010"))
        
        self.lbl_total = tk.Label(frame_derecho, text="Total (Inc. IGV): S/ 0.00", font=("Segoe UI", 14, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN)
        self.lbl_total.pack(pady=15)
        
        self.lbl_saldo_disp = tk.Label(frame_derecho, text=f"Saldo Billetera: S/ {self.usuario_actual.saldo_billetera:.2f}", font=("Segoe UI", 10), bg=BG_PANEL, fg=TEXTO_SECUNDARIO)
        self.lbl_saldo_disp.pack(pady=(0, 10))
        
        self.btn_pagar = tk.Button(
            frame_derecho, 
            text="Procesar Pago", 
            font=("Segoe UI", 12, "bold"), 
            bg=BG_BOTON, 
            fg=TEXTO_SECUNDARIO, 
            relief="flat", 
            pady=10,
            state=tk.DISABLED, 
            cursor="hand2"
        )
        self.btn_pagar.pack(fill=tk.X, padx=20, pady=15)
        self.btn_pagar.config(command=self.procesar_pago_lote)
        
        # Hover para botón Pagar (se actualizará en actualizar_vista_carrito cuando esté habilitado)

    def dibujar_tarjetas_productos(self):
        columnas_maximas = 3
        self.imagenes_referencia = []
        
        for index, prod in enumerate(self.lista_productos):
            fila = index // columnas_maximas
            columna = index % columnas_maximas
            
            card = tk.Frame(self.scrollable_frame, bg=BG_PANEL, bd=1, highlightbackground="#2C2C2C", highlightthickness=1, padx=12, pady=12)
            card.grid(row=fila, column=columna, padx=10, pady=10, sticky="nsew")
            
            ruta_imagen = f"assets/{prod['id_producto']}.png"
            
            try:
                if os.path.exists(ruta_imagen):
                    img_original = Image.open(ruta_imagen)
                    img_redimensionada = img_original.resize((100, 80), Image.Resampling.LANCZOS)
                    foto = ImageTk.PhotoImage(img_redimensionada)
                    
                    lbl_imagen = tk.Label(card, image=foto, bg=BG_PANEL)
                    lbl_imagen.image = foto
                    lbl_imagen.pack(pady=(0, 10))
                    self.imagenes_referencia.append(foto)
                else:
                    tk.Frame(card, bg=BG_BOTON, width=100, height=80).pack(pady=(0, 10))
            except Exception as e:
                print(f"Error cargando imagen para {prod['nombre_producto']}: {e}")
                tk.Frame(card, bg=BG_BOTON, width=100, height=80).pack(pady=(0, 10))
            
            tk.Label(card, text=prod["nombre_producto"], font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN, wraplength=120, height=2).pack()
            tk.Label(card, text=f"S/ {prod['precio']:.2f}", font=("Segoe UI", 12, "bold"), bg=BG_PANEL, fg="#81C784").pack(pady=2)
            
            estado_stock = f"Stock: {prod['stock']}"
            color_stock = TEXTO_SECUNDARIO if prod['stock'] > 0 else "#E57373"
            tk.Label(card, text=estado_stock, font=("Segoe UI", 9), bg=BG_PANEL, fg=color_stock).pack(pady=(0, 10))
            
            estado_btn = tk.NORMAL if prod['stock'] > 0 else tk.DISABLED
            bg_btn_actual = COLOR_ACCION if prod['stock'] > 0 else BG_BOTON
            
            btn_add = tk.Button(
                card, 
                text="Agregar", 
                bg=bg_btn_actual, 
                fg="white", 
                relief="flat", 
                state=estado_btn, 
                font=("Segoe UI", 9, "bold"),
                cursor="hand2" if prod['stock'] > 0 else "arrow",
                command=lambda p=prod: self.agregar_al_carrito(p)
            )
            btn_add.pack(fill=tk.X)
            
            # Efecto hover condicional si hay stock
            if prod['stock'] > 0:
                btn_add.bind("<Enter>", lambda e, b=btn_add: b.config(bg="#1E88E5"))
                btn_add.bind("<Leave>", lambda e, b=btn_add: b.config(bg=COLOR_ACCION))

    def agregar_al_carrito(self, producto):
        id_prod = producto["id_producto"]
        
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
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
            
        subtotal_productos = 0.0
        for id_prod, datos in self.carrito.items():
            subtotal_productos += datos["precio"] * datos["cantidad"]
            self.tree_carrito.insert("", "end", iid=id_prod, values=(datos["nombre"], datos["cantidad"], f"S/ {(datos['precio'] * datos['cantidad']):.2f}"))
            
        descuento_rango = subtotal_productos * self.usuario_actual.porcentaje_descuento
        self.total_carrito = subtotal_productos - descuento_rango
        
        if descuento_rango > 0:
            texto_total = f"Total (Inc. IGV): S/ {self.total_carrito:.2f}\n(Desc. {self.usuario_actual.rango_cuenta}: -S/ {descuento_rango:.2f})"
        else:
            texto_total = f"Total (Inc. IGV): S/ {self.total_carrito:.2f}"
            
        self.lbl_total.config(text=texto_total)
        
        if self.total_carrito > 0 and self.total_carrito <= self.usuario_actual.saldo_billetera:
            self.btn_pagar.config(state=tk.NORMAL, bg=COLOR_PAGO, fg="white")
            self.lbl_total.config(fg="#81C784")
            # Hover interactivo si está habilitado
            self.btn_pagar.bind("<Enter>", lambda e: self.btn_pagar.config(bg="#388E3C"))
            self.btn_pagar.bind("<Leave>", lambda e: self.btn_pagar.config(bg=COLOR_PAGO))
        else:
            self.btn_pagar.config(state=tk.DISABLED, bg=BG_BOTON, fg=TEXTO_SECUNDARIO)
            self.lbl_total.config(fg="#E57373" if self.total_carrito > self.usuario_actual.saldo_billetera else TEXTO_MAIN)
            self.btn_pagar.unbind("<Enter>")
            self.btn_pagar.unbind("<Leave>")

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
            
        self.actualizar_vista_carrito()

    def procesar_pago_lote(self):
        #1. Descontamosel saldo del usuario
        self.usuario_actual.descontar_saldo(self.total_carrito)
        db = DBManager()
        db.actualizar_saldo_usuario(self.usuario_actual.id_usuario, self.usuario_actual.saldo_billetera)
        
        #2. Identificamos al empleado que está procesando la venta
        id_cajero = self.master.empleado_actual["id_empleado"] if hasattr(self.master, "empleado_actual") else None
        
        #3. Disparamos la transaccion masica
        exito = db.procesar_compra_kiosco(
            id_usuario=self.usuario_actual.id_usuario,
            id_empleado=id_cajero,
            total_venta=self.total_carrito,
            carrito=self.carrito
        )
        
        # 4. Evaluamos el resultado de la transacción
        if exito:
            messagebox.showinfo(
                "Compra Exitosa", 
                f"Transacción completada.\nTotal cobrado: S/ {self.total_carrito:.2f}\nNuevo saldo: S/ {self.usuario_actual.saldo_billetera:.2f}", 
                parent=self
            )
        else:
            messagebox.showerror(
                "Error de Transacción", 
                "Hubo un problema registrando la venta en la Base de Datos. El saldo pudo verse afectado.", 
                parent=self
            )
        
        if self.callback_actualizar_panel:
            self.callback_actualizar_panel()
            
        self.destroy()
