import tkinter as tk
from tkinter import ttk, messagebox
from conexion import DBManager

# --- PALETA DE COLORES ---
BG_PANEL = "#1E1E1E"
TEXTO_MAIN = "#FFFFFF"
TEXTO_SECUNDARIO = "#A0A0A0"
COLOR_ELIMINAR = "#D32F2F"

class PanelAdministrador(tk.LabelFrame):
    def __init__(self, parent, controlador, *args, **kwargs):
        super().__init__(parent, text="Módulo Administrador", font=("Segoe UI", 12, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN, padx=15, pady=15, *args, **kwargs)
        self.controlador = controlador
        self.dibujar_panel()

    def dibujar_panel(self):
        for widget in self.winfo_children():
            widget.destroy()

        db = DBManager()

        # ==========================================
        # SECCIÓN U: ACTUALIZAR COMPONENTES PC
        # ==========================================
        tk.Label(self, text="⚙️ Actualizar Hardware:", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="w", pady=(0, 5))
        
        # Selector de PC a modificar
        pcs_validas = [pc.codigo_pc for pc in self.controlador.lista_pcs if pc.codigo_pc and pc.codigo_pc != "None"]
        self.combo_pcs = ttk.Combobox(self, values=pcs_validas, state="readonly", font=("Segoe UI", 10))
        self.combo_pcs.pack(fill=tk.X, pady=(0, 10))
        
        if pcs_validas:
            self.combo_pcs.current(0)

        # Campos de texto de componentes
        tk.Label(self, text="Procesador:", font=("Segoe UI", 9), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_cpu = tk.Entry(self, font=("Segoe UI", 10), bg="#2C2C2C", fg="white", relief="flat", bd=4)
        self.entry_cpu.pack(fill=tk.X, pady=(0, 8))

        tk.Label(self, text="Monitor:", font=("Segoe UI", 9), bg=BG_PANEL, fg=TEXTO_SECUNDARIO).pack(anchor="w")
        self.entry_monitor = tk.Entry(self, font=("Segoe UI", 10), bg="#2C2C2C", fg="white", relief="flat", bd=4)
        self.entry_monitor.pack(fill=tk.X, pady=(0, 15))

        self.btn_update = tk.Button(self, text="Actualizar Hardware", font=("Segoe UI", 10, "bold"), bg="#1976D2", fg="white", relief="flat", pady=5, cursor="hand2", command=self.ejecutar_actualizacion_pc)
        self.btn_update.pack(fill=tk.X, pady=(0, 20))

        # ==========================================
        # SECCIÓN D: ELIMINAR REGISTROS
        # ==========================================
        tk.Label(self, text="🗑️ Zona de Eliminación:", font=("Segoe UI", 10, "bold"), bg=BG_PANEL, fg=TEXTO_MAIN).pack(anchor="w", pady=(0, 5))

        self.btn_del_pc = tk.Button(self, text="❌ Eliminar PC Seleccionada", font=("Segoe UI", 9, "bold"), bg=COLOR_ELIMINAR, fg="white", relief="flat", pady=6, cursor="hand2", command=self.ejecutar_eliminar_pc)
        self.btn_del_pc.pack(fill=tk.X, pady=(0, 10))

        self.btn_del_user = tk.Button(self, text="👤 Eliminar Gamer Activo", font=("Segoe UI", 9, "bold"), bg="#C62828", fg="white", relief="flat", pady=6, cursor="hand2", command=self.ejecutar_eliminar_usuario)
        self.btn_del_user.pack(fill=tk.X)

    def ejecutar_actualizacion_pc(self):
        pc_codigo = self.combo_pcs.get()
        cpu = self.entry_cpu.get().strip()
        mon = self.entry_monitor.get().strip()

        if not cpu and not mon:
            messagebox.showwarning("Campos Vacíos", "Por favor rellene los nuevos componentes.", parent=self)
            return

        db = DBManager()
        # Creamos el método en conexion.py
        if db.actualizar_hardware_pc(pc_codigo, cpu, mon):
            messagebox.showinfo("CRUD: Update", f"Componentes de {pc_codigo} actualizados con éxito.", parent=self)
            self.entry_cpu.delete(0, tk.END)
            self.entry_monitor.delete(0, tk.END)
            self.controlador.cargar_datos_iniciales()
            self.controlador.refrescar_interfaz()

    def ejecutar_eliminar_pc(self):
        pc_codigo = self.combo_pcs.get()
        if not pc_codigo: return

        confirmar = messagebox.askyesno("CRUD: Delete", f"¿Está seguro de eliminar por completo la {pc_codigo}?\nEsto borrará su estación lógica.", parent=self)
        if confirmar:
            db = DBManager()
            if db.eliminar_pc_fisica(pc_codigo):
                messagebox.showinfo("Éxito", f"Máquina {pc_codigo} eliminada del sistema.", parent=self)
                self.controlador.cargar_datos_iniciales()
                self.controlador.refrescar_interfaz()

    def ejecutar_eliminar_usuario(self):
        usuario = self.controlador.usuario_activo
        if usuario.id_usuario == 1:
            messagebox.showwarning("Acción denegada", "No puedes eliminar al usuario base por defecto del sistema.", parent=self)
            return

        confirmar = messagebox.askyesno("CRUD: Delete", f"¿Está seguro de eliminar permanentemente al gamer {usuario.alias_gamer}?", parent=self)
        if confirmar:
            db = DBManager()
            if db.eliminar_usuario_gamer(usuario.id_usuario):
                messagebox.showinfo("Éxito", f"Usuario {usuario.alias_gamer} eliminado correctamente.", parent=self)
                self.controlador.cargar_datos_iniciales()
                self.controlador.refrescar_interfaz()




