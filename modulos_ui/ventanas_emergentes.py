import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from conexion import DBManager

class VentanaRegistro(tk.Toplevel):
    def __init__(self, parent, callback_actualizar=None):
        super().__init__(parent)
        self.parent = parent
        self.callback_actualizar = callback_actualizar # Para avisarle al main que refresque algo si es necesario
        
        self.title("Registrar Nuevo Usuario")
        self.config(bg="#f4f4f9")
        self.resizable(False, False)
        
        # Bloquea la ventana principal
        self.grab_set()
        
        # Inicia la construcción visual
        self.construir_interfaz()
        
    def construir_interfaz(self):
        lbl_v_titulo = tk.Label(self, text="Ficha de Nuevo Gamer", font=("Arial", 14, "bold"), bg="#f4f4f9", fg="#333333")
        lbl_v_titulo.pack(pady=15)
        
        # Alias
        tk.Label(self, text="Alias Gamer:", font=("Arial", 10), bg="#f4f4f9").pack(anchor="w", padx=30)
        self.entry_alias = tk.Entry(self, font=("Arial", 11), width=30)
        self.entry_alias.pack(pady=(2,10), padx=30)
        
        # Rango
        tk.Label(self, text="Rango Cuenta:", font=("Arial", 10), bg="#f4f4f9").pack(anchor="w", padx=30)
        self.rango_var = tk.StringVar(value="Regular")
        menu_rango = tk.OptionMenu(self, self.rango_var, "Regular", "VIP")
        menu_rango.config(font=("Arial", 10), width=26, bg="#ffffff")
        menu_rango.pack(pady=(2,10), padx=30)
        
        # Saldo inicial con placeholders
        tk.Label(self, text="Saldo Inicial (S/):", font=("Arial", 10), bg="#f4f4f9").pack(anchor="w", padx=30)
        self.entry_saldo = tk.Entry(self, font=("Arial", 11), width=30)
        self.entry_saldo.insert(0, "0.00")
        self.entry_saldo.pack(pady=(2,15), padx=30)
        
        self.entry_saldo.bind("<FocusIn>", lambda e: (self.entry_saldo.delete(0, tk.END), self.entry_saldo.config(fg="#000000")) if self.entry_saldo.get() == "0.00" else None)
        self.entry_saldo.bind("<FocusOut>", lambda e: (self.entry_saldo.insert(0, "0.00"), self.entry_saldo.config(fg="#555555")) if self.entry_saldo.get().strip() == "" else None)
        
        btn_guardar = tk.Button(
            self, 
            text="Guardar Usuario",
            font=("Arial", 11, "bold"),
            bg="#c8e6c9", 
            fg="#1b5e20",
            command=self.procesar_registro
        )
        btn_guardar.pack(pady=10)
        
    def procesar_registro(self):
        alias = self.entry_alias.get()
        rango = self.rango_var.get()
        saldo_texto = self.entry_saldo.get()
        
        if not alias.strip():
            messagebox.showwarning("Formulario Incompleto", "El campo 'Alias Gamer' no puede estar vacío", parent=self)
            return
        
        try:
            saldo_inicial = float(saldo_texto)
            if saldo_inicial < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Error de Formato", "El saldo debe ser un número positivo válido", parent=self)
            return
        
        db = DBManager()
        exito = db.registrar_usuario(alias.strip(), rango, saldo_inicial)
        
        if exito:
            messagebox.showinfo("Registro Exitoso", f"El Usuario '{alias}' ha sido incorporado al sistema correctamente", parent=self)
            
            # Si pasamos una función de actualización, la ejecutamos (ej: actualizar el combobox)
            if self.callback_actualizar:
                self.callback_actualizar()
                
            self.destroy() # Cierra la ventana emergente
        else:
            messagebox.showerror("Error del Sistema", "No se pudo completar el registro en la Base de Datos.", parent=self)

class VentanaRecarga(tk.Toplevel):
    def __init__(self, parent, usuario, callback_actualizar=None):
        super().__init__(parent)
        self.parent = parent
        self.usuario = usuario
        self.callback_actualizar = callback_actualizar
        
        self.title("Recarga de billetera")
        self.geometry("300x250")
        self.config(bg="#f4f4f9")
        self.resizable(False, False)
        self.grab_set() 
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        tk.Label(self, text="Caja - Recarga Saldo", font=("Arial", 12, "bold"), bg="#f4f4f9").pack(pady=15)
        tk.Label(self, text=f"Gamer: {self.usuario.alias_gamer}", font=("Arial", 11), bg="#f4f4f9").pack()
        tk.Label(self, text=f"Saldo Actual: S/ {self.usuario.saldo_billetera:.2f}", font=("Arial", 10), fg="gray", bg="#f4f4f9").pack(pady=(0, 15))
        
        tk.Label(self, text="Monto a recargar (S/):", font=("Arial", 10, "bold"), bg="#f4f4f9").pack()
        
        self.entry_monto = tk.Entry(self, font=("Arial", 14), width=15, justify="center")
        self.entry_monto.pack(pady=10)
        self.entry_monto.focus()
        
        btn_confirmar = tk.Button(
            self,
            text="Confirmar Recarga",
            bg="#c8e6c9",
            font=("Arial", 10, "bold"),
            command=self.procesar_recarga
        )
        btn_confirmar.pack(pady=15)
        
    def procesar_recarga(self):
        monto_texto = self.entry_monto.get()
        try:
            monto = float(monto_texto)
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "Ingresa un monto numérico mayor a cero", parent=self)
            return
        
        self.usuario.recargar_saldo(monto)
        
        db = DBManager()
        db.actualizar_saldo_usuario(self.usuario.id_usuario, self.usuario.saldo_billetera)
        
        if self.callback_actualizar:
            self.callback_actualizar()
            
        messagebox.showinfo("Recarga Exitosa", f"Se ha recargado S/ {monto:.2f} a la billetera de {self.usuario.alias_gamer}.\nNuevo saldo: S/ {self.usuario.saldo_billetera:.2f}", parent=self)
        self.destroy()

class VentanaReporteCaja(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.title("Cuadre de Caja - Cyber Reinoso")
        self.geometry("320x280")
        self.config(bg="#f4f4f9")
        self.resizable(False, False)
        self.grab_set()
        
        self.construir_interfaz()
        
    def construir_interfaz(self):
        db = DBManager()
        total_hoy = db.obtener_reporte_caja_hoy()
        
        tk.Label(self, text="📊 Cierre de Turno", font=("Arial", 14, "bold"), bg="#f4f4f9", fg="#333333").pack(pady=15)
        tk.Label(self, text=f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", font=("Arial", 10), bg="#f4f4f9", fg="#555555").pack()
        
        frame_total = tk.Frame(self, bg="#ffffff", bd=2, relief="groove")
        frame_total.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)
        
        tk.Label(frame_total, text="Total Ingresos (Alquiler PCs)", font=("Arial", 10), bg="#ffffff").pack(pady=(15, 5))
        tk.Label(frame_total, text=f"S/ {total_hoy:.2f}", font=("Arial", 20, "bold"), bg="#ffffff", fg="green").pack(pady=5)
        
        tk.Button(
            self, 
            text="Validar y Cerrar", 
            font=("Arial", 10, "bold"), 
            bg="#e0e0e0", 
            command=self.destroy
        ).pack(pady=10)