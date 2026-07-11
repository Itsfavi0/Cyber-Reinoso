import tkinter as tk
from tkinter import messagebox
from conexion import DBManager
from modelos import Usuario, PC_Regular, PC_eSports, PC_StreamingVIP, Sesion, SaldoInsuficienteError
from datetime import datetime
from modulos_ui.ventana_login import VentanaLogin
from modulos_ui.panel_mapa import PanelMapa
from modulos_ui.panel_usuario import PanelUsuario
from modulos_ui.panel_administrador import PanelAdministrador

BG_BASE = "#121212"

# Clase app que hereda de la ventana de tk
class AppCyberReinoso(tk.Tk):
    def __init__(self):
        super().__init__()
        self.sesiones_activas = {}
        self.empleado_actual = None 

        # Ocultamos la ventana principal inmediatamente al arrancar
        self.withdraw()
        self.title("Cyber Reinoso - Smart Center Dashboard")
        
        try:
            self.iconbitmap("assets/logo.ico")
        except Exception as e:
            print(f"Aviso: No se pudo cargar el archivo .ico de la ventana principal: {e}")
        
        # Centrar la ventana principal
        ancho = 1250
        alto = 900
        self.geometry(f"{ancho}x{alto}")
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        self.config(bg=BG_BASE)
        
        # Levantamos el escudo de seguridad bloqueando el flujo
        VentanaLogin(self)
        self.cargar_datos_iniciales()
        
        # Construccion de la interfaz
        self.crear_interfaz()
        self.actualizar_cronometros()
        
    def cargar_datos_iniciales(self):
        """Extrae los datos de SQL y los convierte en objetos"""
        self.lista_pcs = []
        self.sesiones_activas = {}
        db = DBManager()
        
        # Convertimos diccionarios a objetos EstacionTrabajo
        datos_db = db.obtener_estaciones()
        for fila in datos_db:
            categoria = fila["categoria"]
            specs = fila.get("specs", {})
            
            # Instanciamos la clase correcta según la BD, pasándole las especificaciones
            if categoria == "Streaming VIP":
                pc = PC_StreamingVIP(fila["id_estacion"], fila["codigo_pc"], specs)
            elif categoria == "eSports":
                pc = PC_eSports(fila["id_estacion"], fila["codigo_pc"], specs)
            else:
                pc = PC_Regular(fila["id_estacion"], fila["codigo_pc"], specs)
                
            pc.estado = fila["estado_actual"]
            self.lista_pcs.append(pc)
        
        # Cargamos el usuario por defecto (ID 1)
        datos_usr = db.obtener_usuario(1)
        self.usuario_activo = Usuario(
                            id_usuario=datos_usr["id_usuario"], 
                            alias_gamer=datos_usr["alias_gamer"],
                            rango_cuenta=datos_usr["rango_cuenta"],
                            saldo_billetera=datos_usr["saldo_billetera"],
                            minutos_acumulados=datos_usr.get("minutos_acumulados", 0))
        
        sesiones_db = db.obtener_sesiones_activas()
        for s in sesiones_db:
            # Buscamos la instancia del objeto PC correspondiente
            pc_obj = next((pc for pc in self.lista_pcs if pc.id_estacion == s["id_estacion"]), None)
            # Cargamos el usuario de esa sesión activa
            datos_gamer = db.obtener_usuario(s["id_usuario"])
            if pc_obj and datos_gamer:
                gamer_obj = Usuario(
                    id_usuario=datos_gamer["id_usuario"],
                    alias_gamer=datos_gamer["alias_gamer"],
                    rango_cuenta=datos_gamer["rango_cuenta"],
                    saldo_billetera=datos_gamer["saldo_billetera"],
                    minutos_acumulados=datos_gamer.get("minutos_acumulados", 0)
                )
                self.sesiones_activas[pc_obj.id_estacion] = Sesion(id_sesion=s["id_sesion"], usuario=gamer_obj, estacion=pc_obj, hora_inicio=s["hora_inicio"])
        
    def crear_interfaz(self):
        lbl_titulo = tk.Label(self, text="Cyber Reinoso • Smart Center Dashboard", font=("Segoe UI", 20, "bold"), bg=BG_BASE, fg="#FFFFFF")
        lbl_titulo.pack(pady=15)
        
        self.contenedor_principal = tk.Frame(self, bg=BG_BASE)
        self.contenedor_principal.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Inyectamos el Panel Administrador
        self.admin_ui = PanelAdministrador(self.contenedor_principal, controlador=self, width=240)
        self.admin_ui.pack(side="left", fill="y", padx=10, pady=10)
        # self.admin_ui.pack_propagate(False) Mantiene el ancho fijo estético
        
        # Inyectamos el Panel Mapa
        self.mapa_ui = PanelMapa(self.contenedor_principal, controlador=self)
        self.mapa_ui.pack(side="left", expand=True, fill="both", padx=20, pady=10)
        
        # Inyectamos el Panel Usuario
        self.usuario_ui = PanelUsuario(self.contenedor_principal, controlador=self)
        self.usuario_ui.pack(side="right", fill="y", padx=10, pady=10)

    def cambiar_usuario_activo(self, event):
        seleccion = self.usuario_ui.combo_usuarios.get()
        id_seleccionado = int(seleccion.split(" - ")[0])
        datos_usr = DBManager().obtener_usuario(id_seleccionado)
        if datos_usr:
            self.usuario_activo = Usuario(
            id_usuario=datos_usr["id_usuario"], 
            alias_gamer=datos_usr["alias_gamer"], 
            rango_cuenta=datos_usr["rango_cuenta"], 
            saldo_billetera=datos_usr["saldo_billetera"],
            minutos_acumulados=datos_usr.get("minutos_acumulados", 0)
        )
        self.refrescar_interfaz()
        
    def refrescar_interfaz(self):
        self.mapa_ui.dibujar_mapa_pcs()
        self.usuario_ui.dibujar_panel()
        self.admin_ui.dibujar_panel()

    def iniciar_sesion(self, maquina_seleccionada):
        # Verificar si el usuario ya tiene otra sesión activa
        for id_est, sesion in self.sesiones_activas.items():
            if sesion.usuario.id_usuario == self.usuario_activo.id_usuario:
                messagebox.showwarning(
                    "Usuario con sesión activa",
                    f"El gamer {self.usuario_activo.alias_gamer} ya tiene una sesión activa en la PC {sesion.estacion.codigo_pc}.",
                    parent=self
                )
                return

        costo_minimo = maquina_seleccionada.calcular_tarifa(1)
        if self.usuario_activo.saldo_billetera < costo_minimo:
            messagebox.showwarning("Saldo insuficiente", f"Saldo insuficiente. Mínimo requerido: S/{costo_minimo:.2f}")
            return
        
        db = DBManager()
        hora_inicio = datetime.now()
        
        id_cajero = self.empleado_actual["id_empleado"] if self.empleado_actual else 1
        id_sesion = db.registrar_inicio_sesion(self.usuario_activo.id_usuario, id_cajero, maquina_seleccionada.id_estacion, hora_inicio)
        
        if id_sesion:
            self.sesiones_activas[maquina_seleccionada.id_estacion] = Sesion(id_sesion, self.usuario_activo, maquina_seleccionada, hora_inicio)
            db.actualizar_estado_pc(maquina_seleccionada.id_estacion, "Ocupada")
            self.refrescar_interfaz()
        
    def cerrar_sesion(self, maquina_seleccionada, es_corte_automatico=False):
        sesion_actual = self.sesiones_activas.get(maquina_seleccionada.id_estacion)
        if sesion_actual:
            usuario = sesion_actual.usuario
            db = DBManager()
            try:
                sesion_actual.finalizar_sesion(es_corte_automatico=es_corte_automatico)
                
                #calculamos los minutos jugados
                minutos_jugados = int((sesion_actual.hora_fin - sesion_actual.hora_inicio).total_seconds() // 60)
                
                #pasamos los minutos al modelo. Retorna True si cambio de rango
                subio_rango = usuario.agregar_minutos_jugados(minutos_jugados)
                
                db.actualizar_progreso_usuario(usuario.id_usuario, usuario.saldo_billetera, usuario.rango_cuenta, usuario.minutos_acumulados)
                db.actualizar_fin_sesion(sesion_actual.id_sesion, sesion_actual.hora_fin, sesion_actual.monto_cobrado)
                
                if not es_corte_automatico:
                    # Forzamos mínimo 1 minuto para el cálculo de boleta
                    tiempo_cobro = max(1, minutos_jugados) 
                    costo_original = round(maquina_seleccionada.calcular_tarifa(tiempo_cobro), 2)
                    monto_final = round(sesion_actual.monto_cobrado, 2)
                    ahorro = round(costo_original - monto_final, 2)
                    
                    texto_boleta = (
                        f"PC: {maquina_seleccionada.codigo_pc}\n"
                        f"Gamer: {usuario.alias_gamer} [{usuario.rango_cuenta}]\n"
                        f"⏱ Tiempo jugado: {minutos_jugados} min\n"
                    )
                    
                    #Solo mostramos ahorro si hay descuento Y si el ahorro es real (>0)
                    if usuario.porcentaje_descuento > 0 and ahorro > 0:
                        porcentaje = int(usuario.porcentaje_descuento * 100)
                        texto_boleta += f"Costo base: S/ {costo_original:.2f}\n"
                        texto_boleta += f"Ahorro VIP ({porcentaje}%): -S/ {ahorro:.2f}\n"
                    
                    texto_boleta += (
                        f"Total cobrado: S/ {monto_final:.2f}\n"
                        f"Saldo restante: S/ {usuario.saldo_billetera:.2f}"
                    )
                    
                    messagebox.showinfo("Sesión Finalizada - Boleta", texto_boleta, parent=self)
                else:
                    messagebox.showwarning(
                        "Corte Automático",
                        f"Se agotó el saldo de {usuario.alias_gamer} en {maquina_seleccionada.codigo_pc}.\nLa sesión ha sido finalizada por el sistema.",
                        parent=self
                    )
                
                if subio_rango:
                    messagebox.showinfo(
                        "¡LEVEL UP!",
                        f"¡Felicitaciones!\nEl gamer {usuario.alias_gamer} ha acumulado {usuario.minutos_acumulados // 60} horas en el Cyber Reinoso.\n\nNuevo Rango: {usuario.rango_cuenta.upper()}",
                        parent=self
                    )
            except SaldoInsuficienteError:
                if es_corte_automatico:
                    db.actualizar_saldo_usuario(usuario.id_usuario, 0.00)
                    db.actualizar_fin_sesion(sesion_actual.id_sesion, datetime.now(), usuario.saldo_billetera)
            
            if maquina_seleccionada.id_estacion in self.sesiones_activas:
                del self.sesiones_activas[maquina_seleccionada.id_estacion]
            db.actualizar_estado_pc(maquina_seleccionada.id_estacion, "Disponible")
        self.refrescar_interfaz()
        
    def actualizar_cronometros(self):
        tiempo_actual = datetime.now()
        for id_estacion, sesion in list(self.sesiones_activas.items()):
            if id_estacion in self.mapa_ui.labels_cronometros:
                segundos = int((tiempo_actual - sesion.hora_inicio).total_seconds())
                self.mapa_ui.labels_cronometros[id_estacion].config(text=f"⏱️ {segundos // 3600:02d}:{(segundos % 3600) // 60:02d}:{segundos % 60:02d}")
                if sesion.estacion.calcular_tarifa((segundos // 60) + 1) > sesion.usuario.saldo_billetera:
                    self.cerrar_sesion(sesion.estacion, es_corte_automatico=True)
        self.after(1000, self.actualizar_cronometros)
    
if __name__ == "__main__":
    AppCyberReinoso().mainloop()