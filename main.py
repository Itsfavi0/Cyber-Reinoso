import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from conexion import DBManager
from modulos_ui.ventanas_emergentes import VentanaRegistro, VentanaRecarga, VentanaReporteCaja
from modulos_ui.panel_kiosco import PanelKiosco
from modelos import Usuario, PC_Regular, PC_VIP, EstacionTrabajo, Sesion, SaldoInsuficienteError
from datetime import datetime

# Clase app que hereda de la ventana de tk
class AppCyberReinoso(tk.Tk):
    def __init__(self):
        super().__init__()
        self.sesiones_activas = {}

        # Ventana básica
        self.title("Cyber Reinoso - Smart Center Dashboard")
        self.geometry("900x800")
        self.config(bg="#f4f4f9")
        
        # inicializar base de datos simulada en memoria por ahora
        self.cargar_datos_iniciales()
        
        # Construccion de la interfaz
        self.crear_interfaz()
        self.actualizar_cronometros()
        
    def cargar_datos_iniciales(self):
        """Extrae los datos de SQL y los convierte en objetos"""
        self.lista_pcs = []
        
        #instanciamos la conexion con la base de datos
        db = DBManager()
        datos_db = db.obtener_estaciones()
        
        #Diccionarios a objetos
        for fila in datos_db:
            if fila["categoria"] == "VIP":
                pc = PC_VIP(fila["id_estacion"], fila["codigo_pc"])
            else:
                pc = PC_Regular(fila["id_estacion"], fila["codigo_pc"])
                
            pc.estado = fila["estado_actual"]
            self.lista_pcs.append(pc)
        
        datos_usr = db.obtener_usuario(1)
        
        if datos_usr:
            self.usuario_prueba = Usuario(
                datos_usr["id_usuario"],
                datos_usr["alias_gamer"],
                datos_usr["rango_cuenta"],
                datos_usr["saldo_billetera"]
            )
        else:
            print("No se encontró el usuario en la BD. Creando temporal...")
            self.usuario_prueba = Usuario(999, "Invitado", "Regular", 0.0)
            
        self.sesiones_activas = {}
        
    def crear_interfaz(self):
        """Aquí maquetaremos los frames usando el gestor Grid o Pack"""
        # Titulo Principal
        lbl_titulo = tk.Label(self, text="Panel de Control - Cyber Reinoso",
                              font=("Arial", 18, "bold"), bg="#f4f4f9", fg="#333333")
        lbl_titulo.pack(pady=10)
        
        # Caja para partir la ventana en dos partes
        self.contenedor_principal = tk.Frame(self, bg="#f4f4f9")
        self.contenedor_principal.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Contenedor del mapa de computadoras puesto a la izquierda
        self.frame_mapa = tk.Frame(self.contenedor_principal, bg="#e0e0eb", bd=3, relief="groove")
        self.frame_mapa.pack(side="left", expand=True, fill="both", padx=20, pady=10)
        
        # Panel del cliente puesto a la derecha
        self.frame_panel = tk.LabelFrame(self.contenedor_principal, text="Módulo del Cliente",
                                         font=("Arial", 12, "bold"), bg="#f4f4f9", padx=20, pady=20)
        self.frame_panel.pack(side="right", fill="y", padx=10, pady=10)
        
        self.dibujar_mapa_pcs()
        self.dibujar_panel_usuario()
        
    # Dibujamos el mapa usando grid    
    def dibujar_mapa_pcs(self):
        # Configuramos nuestras pcs maximas por fila
        columnas_maximas = 3
        self.labels_cronometros = {}
        
        # Recorrido de nuestra lista objetos pc
        for index, pc in enumerate(self.lista_pcs):
            # Si index es 0, 1, 2 -> Fila 0
            # Si index es 3, 4, 5 -> Fila 1
            fila = index // columnas_maximas
            columna = index % columnas_maximas
            
            if pc.estado == "Disponible":
                color_fondo = "#d1c4e9" if pc.categoria == "VIP" else "#c8e6c9"
                texto_boton = "Asignar"
                estado_boton = tk.NORMAL
                comando_btn = lambda maquina=pc : self.iniciar_sesion(maquina)
            elif pc.estado == "Mantenimiento":
                color_fondo = "#ffe0b2"
                texto_boton = "En Mantenimiento"
                estado_boton = tk.DISABLED #Al estar en mantenimiento bloqueamos el boton
                comando_btn = lambda: None
            else:
                color_fondo = "#ffcdd2"
                texto_boton = "Cerrar Sesión"
                estado_boton = tk.NORMAL
                comando_btn = lambda maquina=pc : self.cerrar_sesion(maquina) 
                
            
            # Frame para cada pc
            frame_pc = tk.Frame(self.frame_mapa, bg=color_fondo, bd=2, relief="raised", padx=10, pady=10)
            frame_pc.grid(row=fila, column=columna, padx=15, pady=15)
            
            # Informacion de cada pc en el frame
            lbl_nombre = tk.Label(frame_pc, text=pc.codigo_pc, font=("Arial", 12, "bold"), bg=color_fondo)
            lbl_nombre.pack()
            
            lbl_cat = tk.Label(frame_pc, text=pc.categoria, font=("Arial", 9), bg=color_fondo, fg="#555555")
            lbl_cat.pack()
            
            color_texto_estado = "green" if pc.estado == "Disponible" else "red" 
            lbl_estado = tk.Label(frame_pc, text=pc.estado, font=("Arial", 10, "bold"), bg=color_fondo, fg=color_texto_estado)
            lbl_estado.pack(pady=5)
            
            lbl_tiempo = tk.Label(frame_pc, text="", font=("Courier", 11, "bold"), bg=color_fondo, fg="#333333")
            lbl_tiempo.pack(pady=(0, 5))
            
            # Guardamos la etiqueta en el diccionario usando el ID de la PC como llave
            self.labels_cronometros[pc.id_estacion] = lbl_tiempo
             
            btn_accion = tk.Button(frame_pc, text=texto_boton, bg="#ffffff", state=estado_boton, command=comando_btn)
            btn_accion.pack()
    
    # dibuja la informacion del cliente en un panel derecho
    def dibujar_panel_usuario(self):
        """"Dibuja el panel derecho con el selector de usuarios, datos y el kiosco"""
        for widget in self.frame_panel.winfo_children():
            widget.destroy()
        
        usuario = self.usuario_prueba
        
        frame_seleccion = tk.Frame(self.frame_panel, bg="#f4f4f9")
        frame_seleccion.pack(fill=tk.X, pady=(0,15))
        
        tk.Label(frame_seleccion, text="Seleccionar Cliente:", font=("Arial", 10, "bold"), bg="#f4f4f9").pack(anchor="w")
        
        db = DBManager()
        todos_los_usuarios = db.obtener_todos_los_usuarios()
        
        lista_nombres = [f"{u['id_usuario']} - {u['alias_gamer']}" for u in todos_los_usuarios]
        self.combo_usuarios = ttk.Combobox(frame_seleccion, values=lista_nombres, state="readonly", font=("Arial", 11))
        self.combo_usuarios.pack(fill=tk.X, pady=5)
        self.combo_usuarios.set(f"{usuario.id_usuario} - {usuario.alias_gamer}") #Usuario prueba actual
        
        #cambio de seleccion
        self.combo_usuarios.bind("<<ComboboxSelected>>", self.cambiar_usuario_activo)
        
        #creamos etiquetas del usuario
        lbl_alias_titulo = tk.Label(self.frame_panel, text="Gamer:", font=("Arial", 10), bg="#f4f4f9", fg="#555555")
        lbl_alias_titulo.pack(anchor="w")
        
        lbl_alias = tk.Label(self.frame_panel, text=usuario.alias_gamer, font=("Arial", 14, "bold"), bg="#f4f4f9", fg="#333333")
        lbl_alias.pack(anchor="w", pady=(0, 15))
        
        lbl_rango_titulo = tk.Label(self.frame_panel, text="Rango:", font=("Arial", 10), bg="#f4f4f9", fg="#555555")
        lbl_rango_titulo.pack(anchor="w")
        
        color_rango = "purple" if usuario.rango_cuenta == "VIP" else "blue"
        lbl_rango = tk.Label(self.frame_panel, text=usuario.rango_cuenta, font=("Arial", 14, "bold"), bg="#f4f4f9", fg=color_rango)
        lbl_rango.pack(anchor="w", pady=(0, 15))
        
        lbl_saldo_titulo = tk.Label(self.frame_panel, text="Saldo Disponible:", font=("Arial", 10), bg="#f4f4f9", fg="#555555")
        lbl_saldo_titulo.pack(anchor="w")
        
        self.lbl_saldo_valor = tk.Label(self.frame_panel, text=f"S/ {usuario.saldo_billetera:.2f}",
                                        font=("Arial", 16, "bold"), bg="#f4f4f9", fg="green")
        self.lbl_saldo_valor.pack(anchor="w", pady=(0, 20))
        
        btn_recargar = tk.Button(
            self.frame_panel,
            text="Recargar Billetera",
            font=("Arial", 10, "bold"),
            bg="#a5d6a7",
            fg="#1b5e20",
            command=lambda: VentanaRecarga(self, self.usuario_prueba, callback_actualizar=self.dibujar_panel_usuario)
        )
        btn_recargar.pack(anchor="w", pady=(0, 15))
        
        # --- INSTANCIACIÓN DEL KIOSCO MODULAR ---
        self.panel_kiosco = PanelKiosco(self.frame_panel, usuario, callback_actualizar_panel=self.dibujar_panel_usuario)
        self.panel_kiosco.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # ----------------------------------------
        
        #Boton para registrar usuarios
        btn_registrar = tk.Button(
            self.frame_panel,
            text="Registrar nuevo Usuario",
            font=("Arial", 10, "bold"),
            bg="#e1bee7",
            fg="#4a148c",
            #Llamamos a la clase y le pasamose el metodo para refrescar
            command=lambda: VentanaRegistro(self,callback_actualizar=self.dibujar_panel_usuario)
        )
        btn_registrar.pack(fill=tk.X, pady=(15,0))
        
        # Botón para el cierre de turno / Cuadre de caja
        btn_caja = tk.Button(
            self.frame_panel,
            text="Reporte de Caja (Hoy)",
            font=("Arial", 10, "bold"),
            bg="#ffcc80",
            fg="#e65100",
            command=lambda: VentanaReporteCaja(self)
        )
        btn_caja.pack(fill=tk.X, pady=(10, 0))
        
    def cambiar_usuario_activo(self,event):
        """Se ejecuta cada vez que el cajero elige un nombre distinto en la lista desplegable"""
        seleccion = self.combo_usuarios.get()
        
        id_seleccionado = int(seleccion.split(" - ")[0])
        db = DBManager()
        datos_usr = db.obtener_usuario(id_seleccionado)
        
        if datos_usr:
            self.usuario_prueba = Usuario(
                datos_usr["id_usuario"],
                datos_usr["alias_gamer"],
                datos_usr["rango_cuenta"],
                datos_usr["saldo_billetera"]
            )
        self.dibujar_panel_usuario()
    
    def iniciar_sesion(self, maquina_seleccionada: EstacionTrabajo):
        """Se ejecuta cuando asignamos una pc"""
        
        #Calculamos cuanto cuesta el primer minuto de la maquiana selecciona. Actua como variable de clase
        costo_minimo = maquina_seleccionada.calcular_tarifa(1)
        
        #Validacion de saldo
        if self.usuario_prueba.saldo_billetera < costo_minimo:
            messagebox.showwarning(
                "Saldo insuficiente", 
                f"Para usar esta PC ({maquina_seleccionada.categoria}), el usuario necesita un minimo de S/{costo_minimo:.2f}.\n\n"
                f"Saldo actual: S/ {self.usuario_prueba.saldo_billetera:.2f}. Por favor recargue la billetera."
            )
            return #Cortamos la ejecucion para que no se inicie la sesion si no tiene saldo
        
        nueva_sesion = Sesion(id_sesion=999, usuario=self.usuario_prueba, estacion=maquina_seleccionada)
        
        self.sesiones_activas[maquina_seleccionada.id_estacion] = nueva_sesion
        
        maquina_seleccionada.estado = "Ocupada"
        #avisamos a la base de datos
        db = DBManager()
        db.actualizar_estado_pc(maquina_seleccionada.id_estacion, "Ocupada")
        
        print(f"Sesión iniciada en {maquina_seleccionada.codigo_pc} por {nueva_sesion.usuario.alias_gamer}")
        # Confirmamos al usuario que la sesión ha sido iniciada
        messagebox.showinfo("Sesión Iniciada", f"Se asignó la {maquina_seleccionada.codigo_pc} a {self.usuario_prueba.alias_gamer}.\n¡Disfruta tu tiempo de juego!")
        
        self.refrescar_interfaz()
        
        
    def refrescar_interfaz(self):
        """"Limpia o destruye los widgets y vuelve a dibujar el mapa de las PCs"""
        
        # winfo_children() obtiene todos los recuadros dentro del frame_mapa
        for widget in self.frame_mapa.winfo_children():
            widget.destroy()
            
        self.dibujar_mapa_pcs()
        
    def cerrar_sesion(self, maquina_seleccionada: EstacionTrabajo, es_corte_automatico=False):
        """Se ejecuta al hacer clic en Cerrar Sesión o automaticamente por el saldo del usuario"""
        # Buscamos en nuestro registro las sesion actual
        sesion_actual = self.sesiones_activas.get(maquina_seleccionada.id_estacion)
           
        if sesion_actual:
            usuario_original = sesion_actual.usuario
            try:
                # Intentamos hacer el cobro en la memoria
                sesion_actual.finalizar_sesion()
                
                # Guardamos el nuevo saldo en la base de datos
                db = DBManager()
                db.actualizar_saldo_usuario(usuario_original.id_usuario, usuario_original.saldo_billetera)
                
                db.guardar_historial_sesion(
                    usuario_original.id_usuario,
                    maquina_seleccionada.id_estacion,
                    sesion_actual.hora_inicio,
                    sesion_actual.hora_fin,
                    sesion_actual.monto_cobrado
                )
                if not es_corte_automatico:
                    messagebox.showinfo("Sesión Finalizada", f"Cobro a usuario '{usuario_original.alias_gamer}' exitoso.\nNuevo saldo: S/ {usuario_original.saldo_billetera:.2f}")        

            except SaldoInsuficienteError as e:
                if es_corte_automatico:
                    db.actualizar_saldo_usuario(usuario_original.id_usuario, 0.00)
                    
                    db.guardar_historial_sesion(
                        usuario_original.id_usuario, 
                        maquina_seleccionada.id_estacion,
                        sesion_actual.hora_inicio, 
                        datetime.now, 
                        usuario_original.saldo_billetera
                    )
                    messagebox.showwarning(
                        "Corte Automatico",
                        f"La sesión en {maquina_seleccionada.codigo_pc} se ha cerrado automaticamente.\n\n"
                        f"El gamer {usuario_original.alias_gamer} consumió todo su saldo."
                    )    
                else:
                    messagebox.showerror("Error de Facturacion", f"Operacion denegada:\n{e}")
                    return #Cortamos la ejecucion para que la PC no se libere si no pagó
            
            # Si todo salió bien, liberamos la PC y actualizamos la base de datos    
            del self.sesiones_activas[maquina_seleccionada.id_estacion]
            db = DBManager()
            db.actualizar_estado_pc(maquina_seleccionada.id_estacion, "Disponible")
        
        self.dibujar_panel_usuario()
        self.refrescar_interfaz()
        
    def actualizar_cronometros(self):
        """Calcula el tiempo transcurrido de cada sesión y actualiza la interfaz visual"""
        tiempo_actual = datetime.now()
        
        # Iteramos solo sobre las máquinas que tienen una sesión activa
        for id_estacion, sesion in list(self.sesiones_activas.items()):
            if id_estacion in self.labels_cronometros:
                # Calculamos cuántos segundos han pasado
                diferencia = tiempo_actual - sesion.hora_inicio
                segundos_totales = int(diferencia.total_seconds())
                
                # Convertimos los segundos a formato HH:MM:SS
                horas = segundos_totales // 3600
                minutos = (segundos_totales % 3600) // 60
                segundos = segundos_totales % 60
                
                # Formateamos el texto
                texto_reloj = f"⏱️ {horas:02d}:{minutos:02d}:{segundos:02d}"
                self.labels_cronometros[id_estacion].config(text=texto_reloj, fg="#333333")
                
                minutos_cobro = (segundos_totales // 60) + 1
                
                costo_actual = sesion.estacion.calcular_tarifa(minutos_cobro)

                if costo_actual > sesion.usuario.saldo_billetera:
                    self.labels_cronometros[id_estacion].config(text="Saldo Agotado", fg="red")
                    self.cerrar_sesion(sesion.estacion, es_corte_automatico=True)
                    
                    messagebox.showwarning(
                        "Corte Automático",
                        f"La sesión en la {sesion.estacion.codigo_pc} se ha cerrado automaticamente.\n\n"
                        f"El gamer {sesion.usuario.alias_gamer} ha consumido su saldo."
                    )
                    
        #Le decimos a Tkinter que vuelva a ejecutar esta función en 1000 milisegundos (1 segundo)
        self.after(1000, self.actualizar_cronometros)
    
if __name__ == "__main__":
    app = AppCyberReinoso()
    app.mainloop()