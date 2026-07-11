"""
APP PRINCIPAL
Este archivo define la ventana principal y actúa como el controlador central de la app.
Aplica el Patrón Mediador (Mediator Pattern): los sub-componentes (panel_mapa, panel_usuario, panel_administrador)
nunca se comunican entre sí directamente; todo pasa por este orquestador para mantener un bajo acoplamiento.
"""
import tkinter as tk
from tkinter import messagebox
from conexion import DBManager
from modelos import Usuario, PC_Regular, PC_eSports, PC_StreamingVIP, Sesion, SaldoInsuficienteError
from datetime import datetime
from modulos_ui.ventana_login import VentanaLogin
from modulos_ui.panel_mapa import PanelMapa
from modulos_ui.panel_usuario import PanelUsuario
from modulos_ui.panel_administrador import PanelAdministrador

BG_BASE = "#121212" # Color base del tema oscur

# HERENCIA: AppCyberReinoso hereda de tk.Tk, convirtiéndose ella misma en la ventana principal.
class AppCyberReinoso(tk.Tk):
    def __init__(self):
        # super().__init__() ejecuta el constructor de tk.Tk para inicializar las capacidades de la ventana gráfica.
        super().__init__()
        # ESTRUCTURA DE CONCURRENCIA: Diccionario en RAM donde la clave es el ID de la mesa 
        # y el valor es el objeto Sesion corriendo en vivo. Permite gestionar múltiples PCs simultáneamente.
        self.sesiones_activas = {}
        self.empleado_actual = None # Almacenará la sesión del cajero/admin autenticado

        # SEGURIDAD (WITHDRAW): Oculta la ventana de fondo en milisegundos hasta que el Login sea exitoso.
        self.withdraw()
        self.title("Cyber Reinoso - Smart Center Dashboard")
        
        try:
            # Carga el ícono nativo del sistema en la esquina superior izquierda y en la barra de tareas.
            self.iconbitmap("assets/logo.ico")
        except Exception as e:
            print(f"Aviso: No se pudo cargar el archivo .ico de la ventana principal: {e}")
        
        # MATEMÁTICA DE INTERFAZ: Algoritmo para centrar la ventana principal exactamente en el medio del monitor.
        ancho = 1250
        alto = 900
        self.geometry(f"{ancho}x{alto}")
        self.update_idletasks() # Fuerza a Tkinter a calcular las dimensiones reales del monitor antes de ubicarla.
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        self.config(bg=BG_BASE)
        
        # CONTROL DE ACCESO: Dispara el modal flotante de seguridad. El código se detiene aquí hasta que el usuario se autentique.
        VentanaLogin(self)
        
        # INICIALIZACIÓN DEL SISTEMA: Si el Login pasó, extraemos la infraestructura relacional de SQL.
        self.cargar_datos_iniciales()
        
        # DIBUJADO UI: Construimos la jerarquía de los paneles modulares.
        self.crear_interfaz()
        # HILO DE CONCURRENCIA: Arranca el motor del cronómetro y vigilancia del Kill Switch.
        self.actualizar_cronometros()
        
    def cargar_datos_iniciales(self):
        """
        TRANSFORMACIÓN ORM (Object-Relational Mapping):
        Lee la base de datos relacional y convierte las filas de SQL en objetos orientados a objetos puros en RAM.
        """
        self.lista_pcs = []
        self.sesiones_activas = {}
        db = DBManager()
        
        # 1. Cargamos el Hardware Físico aplicando Polimorfismo según la columna 'categoria' de SQL.
        datos_db = db.obtener_estaciones()
        for fila in datos_db:
            categoria = fila["categoria"]
            specs = fila.get("specs", {})
            
            # Según el texto de la BD, instanciamos la clase hija correcta.
            if categoria == "Streaming VIP":
                pc = PC_StreamingVIP(fila["id_estacion"], fila["codigo_pc"], specs)
            elif categoria == "eSports":
                pc = PC_eSports(fila["id_estacion"], fila["codigo_pc"], specs)
            else:
                pc = PC_Regular(fila["id_estacion"], fila["codigo_pc"], specs)
                
            pc.estado = fila["estado_actual"]
            self.lista_pcs.append(pc)
        
        # 2. Cargamos un gamer por defecto en memoria (El Invitado ID 1) para evitar que la UI inicie vacía o crashee.
        datos_usr = db.obtener_usuario(1)
        self.usuario_activo = Usuario(
                            id_usuario=datos_usr["id_usuario"], 
                            alias_gamer=datos_usr["alias_gamer"],
                            rango_cuenta=datos_usr["rango_cuenta"],
                            saldo_billetera=datos_usr["saldo_billetera"],
                            minutos_acumulados=datos_usr.get("minutos_acumulados", 0),
                            estado=datos_usr.get("activo", 1)
        )
        
        # 3. RECUPERACIÓN ANTI-APAGONES (Fault Tolerance):
        # Reconstruye en RAM las sesiones que quedaron abiertas (hora_fin = NULL) antes de una caída del sistema.
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
        """
        DESACOPLAMIENTO DE UI: Inyecta los componentes visuales pasándole 'self' (la clase app) como controlador.
        Esto permite que los paneles deleguen la lógica compleja al mediador central.
        """
        lbl_titulo = tk.Label(self, text="Cyber Reinoso • Smart Center Dashboard", font=("Segoe UI", 20, "bold"), bg=BG_BASE, fg="#FFFFFF")
        lbl_titulo.pack(pady=15)
        
        self.contenedor_principal = tk.Frame(self, bg=BG_BASE)
        self.contenedor_principal.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Panel Izquierdo: Gestión de Infraestructura ITSM y CRUD
        self.admin_ui = PanelAdministrador(self.contenedor_principal, controlador=self, width=240)
        self.admin_ui.pack(side="left", fill="y", padx=10, pady=10)
        
        # Panel Central: Grilla Dinámica de PCs (Canvas con Scrollbar)
        self.mapa_ui = PanelMapa(self.contenedor_principal, controlador=self)
        self.mapa_ui.pack(side="left", expand=True, fill="both", padx=20, pady=10)
        
        # Panel Derecho: Tarjeta del Gamer, Fidelización VIP y Kiosco POS
        self.usuario_ui = PanelUsuario(self.contenedor_principal, controlador=self)
        self.usuario_ui.pack(side="right", fill="y", padx=10, pady=10)

    def cambiar_usuario_activo(self, event):
        """EVENT HANDLER: Captura la selección en el Combobox lateral, extrae el ID y reconstruye el objeto en RAM"""
        seleccion = self.usuario_ui.combo_usuarios.get()
        id_seleccionado = int(seleccion.split(" - ")[0]) # Separa el texto "1 - Maximus_27" y toma solo el número "1"
        datos_usr = DBManager().obtener_usuario(id_seleccionado)
        if datos_usr:
            self.usuario_activo = Usuario(
            id_usuario=datos_usr["id_usuario"], 
            alias_gamer=datos_usr["alias_gamer"], 
            rango_cuenta=datos_usr["rango_cuenta"], 
            saldo_billetera=datos_usr["saldo_billetera"],
            minutos_acumulados=datos_usr.get("minutos_acumulados", 0),
            estado=datos_usr["estado"]
        )
        self.refrescar_interfaz()
        
    def refrescar_interfaz(self):
        """PATRÓN OBSERVER BÁSICO: Manda una señal a todos los paneles sub-modulares para que repinten su UI con los nuevos estados"""
        self.mapa_ui.dibujar_mapa_pcs()
        self.usuario_ui.dibujar_panel()
        self.admin_ui.dibujar_panel()

    def iniciar_sesion(self, maquina_seleccionada):
        """
        LÓGICA TRANSACCIONAL DE APERTURA:
        Abre el alquiler de un módulo validando reglas de negocio, saldos y multisesión.
        """
        # REGLA ANTI-ABUSO (Multisesión): Evita que un mismo gamer alquile 3 PCs a la vez con un mismo saldo.
        for id_est, sesion in self.sesiones_activas.items():
            if sesion.usuario.id_usuario == self.usuario_activo.id_usuario:
                messagebox.showwarning(
                    "Usuario con sesión activa",
                    f"El gamer {self.usuario_activo.alias_gamer} ya tiene una sesión activa en la PC {sesion.estacion.codigo_pc}.",
                    parent=self
                )
                return
        # VALIDACIÓN ECONÓMICA: Si el cliente no tiene ni para pagar el primer minuto de esa gama, bloquea el alquiler.
        costo_minimo = maquina_seleccionada.calcular_tarifa(1)
        if self.usuario_activo.saldo_billetera < costo_minimo:
            messagebox.showwarning("Saldo insuficiente", f"Saldo insuficiente. Mínimo requerido: S/{costo_minimo:.2f}")
            return
        
        db = DBManager()
        hora_inicio = datetime.now()
        
        # AUDITORÍA ITSM: Identifica qué empleado/cajero es responsable de autorizar la apertura.
        id_cajero = self.empleado_actual["id_empleado"] if self.empleado_actual else 1
        id_sesion = db.registrar_inicio_sesion(self.usuario_activo.id_usuario, id_cajero, maquina_seleccionada.id_estacion, hora_inicio)
        
        if id_sesion:
            # REGISTRO CONCURRENTE: Almacenamos el objeto Sesion en el diccionario en RAM para que el reloj lo empiece a auditar.
            self.sesiones_activas[maquina_seleccionada.id_estacion] = Sesion(id_sesion, self.usuario_activo, maquina_seleccionada, hora_inicio)
            db.actualizar_estado_pc(maquina_seleccionada.id_estacion, "Ocupada")
            self.refrescar_interfaz()
        
    def cerrar_sesion(self, maquina_seleccionada, es_corte_automatico=False):
        """
        ALGORITMO DE CIERRE Y BILLING:
        Detiene el reloj, calcula el costo total en RAM, actualiza la base de datos, 
        evalúa si el jugador subió de rango (Level Up) y emite la boleta digital.
        """
        sesion_actual = self.sesiones_activas.get(maquina_seleccionada.id_estacion)
        if sesion_actual:
            usuario = sesion_actual.usuario
            db = DBManager()
            try:
                # 1. Ejecutamos el método del modelo en RAM (Descuenta el dinero del objeto y cambia estado a Disponible)
                sesion_actual.finalizar_sesion(es_corte_automatico=es_corte_automatico)
                
                # 2. Cálculo de tiempo para fidelización VIP
                minutos_jugados = int((sesion_actual.hora_fin - sesion_actual.hora_inicio).total_seconds() // 60)
                
                # 3. Suma de tiempo en RAM. Retorna True únicamente si cruzó una barrera de horas y cambió de rango.
                subio_rango = usuario.agregar_minutos_jugados(minutos_jugados)
                
                # 4. PERSISTENCIA ACID: Sincroniza el monedero y el cierre de sesión en SQL Server.
                db.actualizar_progreso_usuario(usuario.id_usuario, usuario.saldo_billetera, usuario.rango_cuenta, usuario.minutos_acumulados)
                db.actualizar_fin_sesion(sesion_actual.id_sesion, sesion_actual.hora_fin, sesion_actual.monto_cobrado)
                
                # 5. GENERACIÓN DE BOLETA COMERCIAL
                if not es_corte_automatico:
                    # Forzamos mínimo 1 minuto para el cálculo de boleta
                    tiempo_cobro = max(1, minutos_jugados) # SALVAVIDAS COMERCIAL: Cobro mínimo de 1 minuto
                    costo_original = round(maquina_seleccionada.calcular_tarifa(tiempo_cobro), 2)
                    monto_final = round(sesion_actual.monto_cobrado, 2)
                    ahorro = round(costo_original - monto_final, 2)
                    
                    texto_boleta = (
                        f"PC: {maquina_seleccionada.codigo_pc}\n"
                        f"Gamer: {usuario.alias_gamer} [{usuario.rango_cuenta}]\n"
                        f"⏱ Tiempo jugado: {minutos_jugados} min\n"
                    )
                    
                    # TRANSPARENCIA EN FACTURACIÓN: Muestra el beneficio VIP en la boleta si hubo ahorro real (> 0).
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
                    # NOTIFICACIÓN DE KILL SWITCH
                    messagebox.showwarning(
                        "Corte Automático",
                        f"Se agotó el saldo de {usuario.alias_gamer} en {maquina_seleccionada.codigo_pc}.\nLa sesión ha sido finalizada por el sistema.",
                        parent=self
                    )
                
                # RECOMPENSA UX: Alerta festiva si el cliente subió de categoría en este turno.
                if subio_rango:
                    messagebox.showinfo(
                        "¡LEVEL UP!",
                        f"¡Felicitaciones!\nEl gamer {usuario.alias_gamer} ha acumulado {usuario.minutos_acumulados // 60} horas en el Cyber Reinoso.\n\nNuevo Rango: {usuario.rango_cuenta.upper()}",
                        parent=self
                    )
            except SaldoInsuficienteError:
                # Si por alguna razón asíncrona falló el cobro, fuerza el saldo a S/ 0.00 por seguridad.
                if es_corte_automatico:
                    db.actualizar_saldo_usuario(usuario.id_usuario, 0.00)
                    db.actualizar_fin_sesion(sesion_actual.id_sesion, datetime.now(), usuario.saldo_billetera)
            
            # LIMPIEZA DE CONCURRENCIA: Borra la sesión del diccionario en RAM para liberar el cronómetro en pantalla.
            if maquina_seleccionada.id_estacion in self.sesiones_activas:
                del self.sesiones_activas[maquina_seleccionada.id_estacion]
            db.actualizar_estado_pc(maquina_seleccionada.id_estacion, "Disponible")
        self.refrescar_interfaz()
        
    def actualizar_cronometros(self):
        """
        MOTOR ASÍNCRONO DE CONCURRENCIA (THE KILL SWITCH):
        Bucle de segundo plano impulsado por self.after(1000). Recorre las sesiones activas segundo a segundo,
        pinta el tiempo transcurrido en el mapa y evalúa el saldo para disparar cortes automáticos si el monedero llega a 0.
        """
        tiempo_actual = datetime.now()
        # list(self.sesiones_activas.items()) crea una copia temporal del diccionario para poder
        # modificar y borrar sesiones en vivo dentro del ciclo 'for' sin que Python lance el error 'RuntimeError: dictionary changed size'.
        for id_estacion, sesion in list(self.sesiones_activas.items()):
            if id_estacion in self.mapa_ui.labels_cronometros:
                segundos = int((tiempo_actual - sesion.hora_inicio).total_seconds())
                
                # MATEMÁTICA DE FORMATO: Convierte los segundos en formato estándar HH:MM:SS de dos dígitos (00:00:00).
                self.mapa_ui.labels_cronometros[id_estacion].config(text=f"⏱️ {segundos // 3600:02d}:{(segundos % 3600) // 60:02d}:{segundos % 60:02d}")
                
                # EVALUACIÓN DE CORTE (Kill Switch): Si el costo del próximo minuto es mayor al saldo, corta de golpe.
                if sesion.estacion.calcular_tarifa((segundos // 60) + 1) > sesion.usuario.saldo_billetera:
                    self.cerrar_sesion(sesion.estacion, es_corte_automatico=True)
        
        # RECURSIÓN CONTROLADA: Le ordena a Tkinter que vuelva a invocar a esta misma función exactamente dentro de 1000 milisegundos (1 segundo).
        self.after(1000, self.actualizar_cronometros)
    
if __name__ == "__main__":
    # Instancia el orquestador principal y enciende el ciclo infinito visual (mainloop) para escuchar eventos del mouse y teclado.
    AppCyberReinoso().mainloop()