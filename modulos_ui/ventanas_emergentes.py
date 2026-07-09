import tkinter as tk
from tkinter import ttk, messagebox
from conexion import DBManager

# --- PALETA COLORES ---
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
        self.geometry("350x380")
        self.config(bg=BG_BASE)
        self.grab_set()
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        tk.Label(self, text="Registro de Usuario", font=("Arial", 14, "bold"), bg=BG_BASE, fg=TEXTO_MAIN).pack(pady=20)
        
        tk.Label(self, text="Alias / Nickname:", font=("Arial", 10), bg=BG_BASE, fg=TEXTO_SECUNDARIO).pack(anchor="w", padx=40)
        self.entry_alias = ttk.Entry(self, font=("Arial", 11))
        self.entry_alias.pack(fill=tk.X, padx=40, pady=(5, 15))
        
        tk.Label(self, text="Rango Inicial:", font=("Arial", 10), bg=BG_BASE, fg=TEXTO_SECUNDARIO).pack(anchor="w", padx=40)
        self.combo_rango = ttk.Combobox(self, values=["Regular", "VIP"], state="readonly", font=("Arial", 11))
        self.combo_rango.set("Regular")
        self.combo_rango.pack(fill=tk.X, padx=40, pady=(5, 15))
        
        tk.Label(self, text="Saldo Inicial (S/):", font=("Arial", 10), bg=BG_BASE, fg=TEXTO_SECUNDARIO).pack(anchor="w", padx=40)
        self.entry_saldo = ttk.Entry(self, font=("Arial", 11))
        self.entry_saldo.pack(fill=tk.X, padx=40, pady=(5, 25))
        
        tk.Button(self, text="Guardar Gamer", font=("Arial", 11, "bold"), bg="#6A1B9A", fg="white", relief="flat", activebackground="#4A148C", activeforeground="white", command=self.guardar).pack(fill=tk.X, padx=40)
        
    def guardar(self):
        alias = self.entry_alias.get().strip()
        rango = self.combo_rango.get()
        saldo_txt = self.entry_saldo.get()
        
        if not alias or not saldo_txt:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos.", parent=self)
            return
            
        try:
            saldo = float(saldo_txt)
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
            messagebox.showerror("Error de formato", "El saldo debe ser un número válido.", parent=self)


class VentanaRecarga(tk.Toplevel):
    def __init__(self, parent, usuario, callback_actualizar):
        super().__init__(parent)
        self.usuario = usuario
        self.callback_actualizar = callback_actualizar
        self.title("Recarga de Billetera")
        self.geometry("300x250")
        self.config(bg=BG_BASE)
        self.grab_set()
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        tk.Label(self, text="Recargar Billetera", font=("Arial", 14, "bold"), bg=BG_BASE, fg=TEXTO_MAIN).pack(pady=(20, 5))
        tk.Label(self, text=f"Gamer: {self.usuario.alias_gamer}", font=("Arial", 11), bg=BG_BASE, fg=COLOR_DISPONIBLE).pack(pady=(0, 20))
        
        tk.Label(self, text="Monto a recargar (S/):", font=("Arial", 10), bg=BG_BASE, fg=TEXTO_SECUNDARIO).pack(anchor="w", padx=40)
        self.entry_monto = ttk.Entry(self, font=("Arial", 12))
        self.entry_monto.pack(fill=tk.X, padx=40, pady=(5, 20))
        
        tk.Button(self, text="Confirmar Recarga", font=("Arial", 11, "bold"), bg="#2E7D32", fg="white", relief="flat", activebackground="#1B5E20", activeforeground="white", command=self.procesar_recarga).pack(fill=tk.X, padx=40)
        
    def procesar_recarga(self):
        try:
            monto = float(self.entry_monto.get())
            if monto <= 0:
                raise ValueError("El monto debe ser positivo.")
                
            nuevo_saldo = self.usuario.saldo_billetera + monto
            db = DBManager()
            db.actualizar_saldo_usuario(self.usuario.id_usuario, nuevo_saldo)
            
            messagebox.showinfo("Recarga Exitosa", f"Se recargaron S/ {monto:.2f} a {self.usuario.alias_gamer}.\nNuevo saldo: S/ {nuevo_saldo:.2f}", parent=self)
            
            if self.callback_actualizar:
                self.callback_actualizar()
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Ingrese un monto válido y mayor a cero.", parent=self)


class VentanaReporteCaja(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reporte de Caja")
        self.geometry("350x400")
        self.config(bg=BG_BASE)
        self.grab_set()
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        tk.Label(self, text="Cierre de Turno", font=("Arial", 16, "bold"), bg=BG_BASE, fg=TEXTO_MAIN).pack(pady=20)
        
        db = DBManager()
        ingresos_pcs = db.obtener_reporte_caja_hoy()
        ingresos_kiosco = db.obtener_reporte_tienda_hoy()
        total_absoluto = ingresos_pcs + ingresos_kiosco
        
        frame_datos = tk.Frame(self, bg=BG_PANEL, bd=1, relief="ridge", padx=20, pady=20)
        frame_datos.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        tk.Label(frame_datos, text="Alquiler de PCs:", font=("Arial", 11), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        tk.Label(frame_datos, text=f"S/ {ingresos_pcs:.2f}", font=("Arial", 14, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="e", pady=(0, 15))
        
        tk.Label(frame_datos, text="Ventas de Kiosco:", font=("Arial", 11), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        tk.Label(frame_datos, text=f"S/ {ingresos_kiosco:.2f}", font=("Arial", 14, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="e", pady=(0, 15))
        
        # Separador
        tk.Frame(frame_datos, bg=TEXTO_SECUNDARIO, height=1).pack(fill=tk.X, pady=10)
        
        tk.Label(frame_datos, text="TOTAL EN CAJA:", font=("Arial", 12, "bold"), bg=BG_PANEL, fg=COLOR_DISPONIBLE).pack(anchor="w")
        tk.Label(frame_datos, text=f"S/ {total_absoluto:.2f}", font=("Arial", 20, "bold"), bg=BG_PANEL, fg=COLOR_DISPONIBLE).pack(anchor="e")
        
        tk.Button(self, text="Cerrar Reporte", font=("Arial", 11, "bold"), bg=BG_BOTON, fg=TEXTO_MAIN, relief="flat", activebackground="#424242", activeforeground="white", command=self.destroy).pack(fill=tk.X, padx=20, pady=(0, 20))