import tkinter as tk
from tkinter import ttk, messagebox
from conexion import DBManager

# --- PALETA COLORES COHERENTE CON EL DASHBOARD ---
BG_BASE = "#121212"
BG_PANEL = "#1E1E1E"
TEXTO_MAIN = "#FFFFFF"
TEXTO_SECUNDARIO = "#A0A0A0"
BG_BOTON = "#2C2C2C"
COLOR_DISPONIBLE = "#00E676"

class VentanaRegistro(tk.Toplevel):
    def __init__(self, parent, callback_actualizar):
        super().__init__(parent)
        self.callback_actualizar = callback_actualizar
        self.title("Nuevo Gamer")
        self.geometry("380x420")
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
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        card = tk.Frame(self, bg=BG_PANEL, highlightbackground="#2C2C2C", highlightthickness=1, padx=25, pady=25)
        card.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(card, text="Registro de Usuario", font=("Segoe UI", 16, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(pady=(0, 20))
        
        tk.Label(card, text="ALIAS / NICKNAME:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_alias = tk.Entry(card, font=("Segoe UI", 11), bg="#2C2C2C", fg="white", insertbackground="white", relief="flat", bd=5)
        self.entry_alias.pack(fill=tk.X, pady=(5, 15))
        self.entry_alias.focus_set()
        
        tk.Label(card, text="RANGO INICIAL:", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.combo_rango = ttk.Combobox(card, values=["Regular", "VIP"], state="readonly", font=("Segoe UI", 11))
        self.combo_rango.set("Regular")
        self.combo_rango.pack(fill=tk.X, pady=(5, 15))
        
        tk.Label(card, text="SALDO INICIAL (S/):", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_saldo = tk.Entry(card, font=("Segoe UI", 11), bg="#2C2C2C", fg="white", insertbackground="white", relief="flat", bd=5)
        self.entry_saldo.pack(fill=tk.X, pady=(5, 20))
        
        self.btn_guardar = tk.Button(
            card, 
            text="Guardar Gamer", 
            font=("Segoe UI", 11, "bold"), 
            bg="#6A1B9A", 
            fg="white", 
            relief="flat", 
            activebackground="#4A148C", 
            activeforeground="white", 
            pady=8,
            cursor="hand2"
        )
        self.btn_guardar.pack(fill=tk.X, pady=(10, 0))
        self.btn_guardar.config(command=self.guardar)
        
        # Efecto Hover
        self.btn_guardar.bind("<Enter>", lambda e: self.btn_guardar.config(bg="#8E24AA"))
        self.btn_guardar.bind("<Leave>", lambda e: self.btn_guardar.config(bg="#6A1B9A"))
        
    def guardar(self):
        alias = self.entry_alias.get().strip()
        rango = self.combo_rango.get()
        saldo_txt = self.entry_saldo.get().strip()
        
        if not alias or not saldo_txt:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos.", parent=self)
            return
            
        try:
            saldo = float(saldo_txt)
            if saldo < 0:
                raise ValueError()
            db = DBManager()
            exito = db.registrar_usuario(alias, rango, saldo)
            if exito:
                messagebox.showinfo("Éxito", f"Usuario {alias} registrado correctamente.", parent=self)
                if self.callback_actualizar:
                    self.callback_actualizar()
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo registrar el usuario en la Base de Datos.", parent=self)
        except ValueError:
            messagebox.showerror("Error de formato", "El saldo debe ser un número positivo válido.", parent=self)


class VentanaRecarga(tk.Toplevel):
    def __init__(self, parent, usuario, callback_actualizar):
        super().__init__(parent)
        self.usuario = usuario
        self.callback_actualizar = callback_actualizar
        self.title("Recarga de Billetera")
        self.geometry("350x300")
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
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        card = tk.Frame(self, bg=BG_PANEL, highlightbackground="#2C2C2C", highlightthickness=1, padx=25, pady=25)
        card.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(card, text="Recargar Billetera", font=("Segoe UI", 16, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(pady=(0, 5))
        tk.Label(card, text=f"Gamer: {self.usuario.alias_gamer}", font=("Segoe UI", 11, "bold"), bg=BG_PANEL, fg=COLOR_DISPONIBLE).pack(pady=(0, 20))
        
        tk.Label(card, text="MONTO A RECARGAR (S/):", font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_monto = tk.Entry(card, font=("Segoe UI", 12), bg="#2C2C2C", fg="white", insertbackground="white", relief="flat", bd=5)
        self.entry_monto.pack(fill=tk.X, pady=(5, 20))
        self.entry_monto.focus_set()
        
        self.btn_recargar = tk.Button(
            card, 
            text="Confirmar Recarga", 
            font=("Segoe UI", 11, "bold"), 
            bg="#2E7D32", 
            fg="white", 
            relief="flat", 
            activebackground="#1B5E20", 
            activeforeground="white", 
            pady=8,
            cursor="hand2"
        )
        self.btn_recargar.pack(fill=tk.X)
        self.btn_recargar.config(command=self.procesar_recarga)
        
        # Efecto Hover
        self.btn_recargar.bind("<Enter>", lambda e: self.btn_recargar.config(bg="#388E3C"))
        self.btn_recargar.bind("<Leave>", lambda e: self.btn_recargar.config(bg="#2E7D32"))
        
    def procesar_recarga(self):
        try:
            monto_texto = self.entry_monto.get().strip()
            if not monto_texto:
                raise ValueError("El campo está vacío.")
            
            monto = float(monto_texto)
            if monto <= 0:
                raise ValueError("El monto debe ser positivo.")
            
            self.usuario.recargar_saldo(monto)
                
            nuevo_saldo = self.usuario.saldo_billetera + monto
            db = DBManager()
            db.actualizar_saldo_usuario(self.usuario.id_usuario, nuevo_saldo)
            
            messagebox.showinfo("Recarga Exitosa", f"Se recargaron S/ {monto:.2f} a {self.usuario.alias_gamer}.\nNuevo saldo: S/ {nuevo_saldo:.2f}", parent=self)
            
            if self.callback_actualizar:
                self.callback_actualizar()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error de entrada", f"Por favor ingrese un número válido. ({e})", parent=self)

class VentanaReporteCaja(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reporte de Caja")
        self.geometry("380x450")
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
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        tk.Label(self, text="Cierre de Turno", font=("Segoe UI", 16, "bold"), bg=BG_BASE, fg=TEXTO_MAIN).pack(pady=15)
        
        db = DBManager()
        ingresos_pcs = db.obtener_reporte_caja_hoy()
        ingresos_kiosco = db.obtener_reporte_tienda_hoy()
        total_absoluto = ingresos_pcs + ingresos_kiosco
        
        frame_datos = tk.Frame(self, bg=BG_PANEL, bd=1, highlightbackground="#2C2C2C", highlightthickness=1, padx=20, pady=20)
        frame_datos.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        tk.Label(frame_datos, text="Alquiler de PCs:", font=("Segoe UI", 11), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        tk.Label(frame_datos, text=f"S/ {ingresos_pcs:.2f}", font=("Segoe UI", 14, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="e", pady=(0, 15))
        
        tk.Label(frame_datos, text="Ventas de Kiosco:", font=("Segoe UI", 11), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        tk.Label(frame_datos, text=f"S/ {ingresos_kiosco:.2f}", font=("Segoe UI", 14, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="e", pady=(0, 15))
        
        # Separador
        separator = tk.Frame(frame_datos, bg="#333333", height=1)
        separator.pack(fill=tk.X, pady=15)
        
        tk.Label(frame_datos, text="TOTAL EN CAJA:", font=("Segoe UI", 12, "bold"), bg=BG_PANEL, fg=COLOR_DISPONIBLE).pack(anchor="w")
        tk.Label(frame_datos, text=f"S/ {total_absoluto:.2f}", font=("Segoe UI", 22, "bold"), bg=BG_PANEL, fg=COLOR_DISPONIBLE).pack(anchor="e")
        
        self.btn_cerrar = tk.Button(
            self, 
            text="Cerrar Reporte", 
            font=("Segoe UI", 11, "bold"), 
            bg=BG_BOTON, 
            fg=TEXTO_MAIN, 
            relief="flat", 
            activebackground="#424242", 
            activeforeground="white", 
            pady=8,
            cursor="hand2"
        )
        self.btn_cerrar.pack(fill=tk.X, padx=20, pady=(0, 20))
        self.btn_cerrar.config(command=self.destroy)
        
        # Efecto Hover
        self.btn_cerrar.bind("<Enter>", lambda e: self.btn_cerrar.config(bg="#424242"))
        self.btn_cerrar.bind("<Leave>", lambda e: self.btn_cerrar.config(bg=BG_BOTON))
