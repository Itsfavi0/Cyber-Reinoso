import tkinter as tk
from tkinter import messagebox
from conexion import DBManager

class PanelKiosco(tk.LabelFrame):
    def __init__(self, parent, usuario_actual, callback_actualizar_panel):
        # Inicializamos el LabelFrame padre
        super().__init__(parent, text="🛒 Kiosco Cyber", font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
        
        self.usuario_actual = usuario_actual
        self.callback_actualizar_panel = callback_actualizar_panel
        
        # El Kiosco es independiente, él mismo pide sus productos a la BD
        db = DBManager()
        self.lista_productos = db.obtener_productos()
        
        self.dibujar_productos()
        
    def dibujar_productos(self):
        """Renderiza los botones de la tienda leyendo la lista en memoria"""
        # Limpiamos el frame por si se está redibujando tras una compra
        for widget in self.winfo_children():
            widget.destroy()
            
        lbl_igv = tk.Label(self, text="* Todos los precios incluyen IGV", font=("Arial", 8, "italic"), bg="#f0f0f0", fg="#555555")
        lbl_igv.pack(pady=(5,15), anchor=tk.CENTER)
        
        for prod in self.lista_productos:
            nombre = prod["nombre_producto"]
            precio = prod["precio"]
            stock  = prod["stock"]
            
            color_boton = "#bbdefb"
            if "Cuate" in nombre or "Snack" in nombre:
                color_boton = "#ffe0b2"
            elif "Recarga" in nombre:
                color_boton = "#c8e6c9"
                
            if stock > 0:
                texto_boton = f"{nombre} ({stock} und) - S/{precio:.2f}"
                estado_boton = tk.NORMAL
            else:
                texto_boton = f"{nombre} (AGOTADO) - S/{precio:.2f}"
                estado_boton = tk.DISABLED
                color_boton = "#e0e0e0"
            
            btn_prod = tk.Button(
                self, 
                text=texto_boton, 
                bg=color_boton, 
                width=25,
                state=estado_boton,
                command=lambda n=nombre, p=precio: self.comprar_producto(n, p)
            )
            btn_prod.pack(pady=5, anchor=tk.CENTER)
            
    def comprar_producto(self, nombre_producto, precio):
        """Procesa la venta y se comunica con el DAO"""
        if self.usuario_actual.saldo_billetera < precio:
            messagebox.showwarning("Saldo Insuficiente", f"No hay saldo suficiente para comprar {nombre_producto}.", parent=self)
            return
        
        # 1. Descuento en modelo
        self.usuario_actual.descontar_saldo(precio)
        
        # 2. Impacto en Base de Datos
        db = DBManager()
        db.actualizar_saldo_usuario(self.usuario_actual.id_usuario, self.usuario_actual.saldo_billetera)
        db.restar_stock_producto(nombre_producto)
        
        # 3. Refrescar datos internos del Kiosco y redibujar botones
        self.lista_productos = db.obtener_productos()
        self.dibujar_productos()
        
        # 4. Mostramos el mensaje de éxito PRIMERO (mientras este panel aún existe)
        messagebox.showinfo(
            "Venta exitosa", 
            f"Se vendió: {nombre_producto}\nTotal cobrado: S/{precio:.2f}\nNuevo Saldo: S/{self.usuario_actual.saldo_billetera:.2f}", 
            parent=self
        )
        
        # 5. Avisar al main.py que actualice todo el panel derecho AL FINAL 
        # (Esto destruirá este objeto PanelKiosco y creará uno nuevo)
        if self.callback_actualizar_panel:
            self.callback_actualizar_panel()
            
        messagebox.showinfo("Venta exitosa", f"Se vendió: {nombre_producto}\nTotal cobrado: S/{precio:.2f}\nNuevo Saldo: S/{self.usuario_actual.saldo_billetera:.2f}", parent=self)