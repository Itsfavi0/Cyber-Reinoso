import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from conexion import DBManager
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
            
        
        self.lista_productos = db.obtener_productos()    
            
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
            command=self.abrir_ventana_recarga
        )
        btn_recargar.pack(anchor="w", pady=(0, 15))
        
        #Kiosco
        self.frame_tienda = tk.LabelFrame(self.frame_panel, text="Kiosco Cyber", font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
        self.frame_tienda.pack(fill=tk.BOTH, expand=True, padx=10,pady=10)
        
        self.dibujar_productos_tienda()
        
        #Boton para registrar usuarios
        btn_registrar = tk.Button(
            self.frame_panel,
            text="Registrar nuevo Usuario",
            font=("Arial", 10, "bold"),
            bg="#e1bee7",
            fg="#4a148c",
            command=self.abrir_ventana_registro
        )
        btn_registrar.pack(fill=tk.X, pady=(15,0))
        
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
    
    def dibujar_productos_tienda(self):
        """Limpia los botones actuales del kiosco y los vuelve a renderizar con el stock real"""
        for widget in self.frame_tienda.winfo_children():
            widget.destroy()
        
        lbl_igv = tk.Label(self.frame_tienda, text="* Todos los precios incluyen IGV", font=("Arial", 8, "italic"), bg="#f0f0f0", fg="#555555")
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
                texto_boton = f"{nombre} ({stock} und)- S/{precio:.2f}"
                estado_boton = tk.NORMAL
            else:
                texto_boton = f"{nombre} (AGOTADO) - S/{precio:.2f}"
                estado_boton = tk.DISABLED
                color_boton = "#e0e0e0"
            
            btn_prod = tk.Button(
                self.frame_tienda, 
                text=texto_boton, 
                bg=color_boton, 
                width=25,
                state=estado_boton,
                command=lambda n=nombre, p=precio: self.comprar_producto(n,p)
            )
            
            btn_prod.pack(pady=5, anchor=tk.CENTER)
    
    def iniciar_sesion(self, maquina_seleccionada: EstacionTrabajo):
        """Se ejecuta cuando asignamos una pc"""
        
        #Validacion de saldo
        if self.usuario_prueba.saldo_billetera <= 0:
            messagebox.showwarning("Saldo insuficiente", "El usuario no tiene saldo para iniciar una sesión. Por favor recargue la billetera.")
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
        
    def comprar_producto(self, nombre_producto, precio):
        """"Procesa la venta de un producto del kiosko y lo descuenta del saldo"""
        #Validacion
        if self.usuario_prueba.saldo_billetera < precio:
            messagebox.showwarning("Saldo Insuficiente", f"No hay saldo suficiente para comprar {nombre_producto}.")
            return
        
        self.usuario_prueba.descontar_saldo(precio)
        
        db = DBManager()
        db.actualizar_saldo_usuario(self.usuario_prueba.id_usuario, self.usuario_prueba.saldo_billetera)
        #restamos el stock
        db.restar_stock_producto(nombre_producto)
        
        #actualizamos la memoria local
        self.lista_productos = db.obtener_productos()
        
        self.lbl_saldo_valor.config(text=f"S/ {self.usuario_prueba.saldo_billetera:.2f}")
        self.dibujar_productos_tienda() #Redibujamos los productos
        
        messagebox.showinfo("Venta exitosa", f"Se vendió: {nombre_producto}\nTotal cobrado: S/{precio:.2f}\nNuevo Saldo: S/{self.usuario_prueba.saldo_billetera:.2f}")
       
    def abrir_ventana_registro(self):
        """Crea una ventana emergente flotante para ingresar los datos del nuevo Usuario"""
        ventana_reg = tk.Toplevel(self)
        ventana_reg.title("Registrar Nuevo Usuario")
        #ventana_reg.geometry("350x320")
        ventana_reg.config(bg="#f4f4f9")
        ventana_reg.resizable(False,False)
        
        #Bloquea la ventana principal hasta que se cierre la emergente
        ventana_reg.grab_set()
        
        #Diseño
        lbl_v_titulo = tk.Label(ventana_reg, text="Ficha de Nuevo Gamer", font=("Arial", 14, "bold"), bg="#f4f4f9", fg="#333333")
        lbl_v_titulo.pack(pady=15)
        
        #alias
        tk.Label(ventana_reg, text="Alias Gamer:", font=("Arial", 10), bg="#f4f4f9").pack(anchor="w", padx=30)
        entry_alias = tk.Entry(ventana_reg, font=("Arial", 11), width=30)
        entry_alias.pack(pady=(2,10), padx=30)
        
        #rango
        tk.Label(ventana_reg, text="Rango Cuenta:", font=("Arial", 10), bg="#f4f4f9").pack(anchor="w", pady=30)
        rango_var = tk.StringVar(value="Regular")
        menu_rango = tk.OptionMenu(ventana_reg, rango_var, "Regular", "VIP")
        menu_rango.config(font=("Arial", 10), width=26, bg="#ffffff")
        menu_rango.pack(pady=(2,10), padx=30)
        
        #saldo inicial
        tk.Label(ventana_reg, text="Saldo Inicial (S/):", font=("Arial", 10), bg="#f4f4f9").pack(anchor="w", pady=30)
        entry_saldo = tk.Entry(ventana_reg, font=("Arial", 11), width=30)
        entry_saldo.insert(0, "0.00")
        entry_saldo.pack(pady=(2,15), padx=30)
        entry_saldo.bind("<FocusIn>", lambda event: (entry_saldo.delete(0, tk.END), entry_saldo.config(fg="#000000")) if entry_saldo.get() == "0.00" else None)
        entry_saldo.bind("<FocusOut>", lambda event: (entry_saldo.insert(0, "0.00"), entry_saldo.config(fg="#555555")) if entry_saldo.get().strip() == "" else None)
        
        #boton guardar
        btn_guardar = tk.Button(
            ventana_reg, 
            text="Guardar Usuario",
            font=("Arial", 11, "bold"),
            bg="#c8e6c9", 
            fg="#1b5e20",
            command=lambda: self.procesar_registro_usuario(entry_alias.get(), rango_var.get(), entry_saldo.get(), ventana_reg)
        )
        btn_guardar.pack(pady=10)
        
    def procesar_registro_usuario(self, alias, rango, saldo_texto, ventana):
        """"Valida las entradas del cajero y las manda a nuestro DAO"""
        #validacion alias vacio
        if not alias.strip():
            messagebox.showwarning("Formulario Incompleto", "El campo 'Alias Gamer' no puede estar vacío", parent=ventana)
            return
        
        try:
            saldo_inicial = float(saldo_texto)
            if saldo_inicial < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Error de Formato", "El saldo debe ser un número positivo válido", parent=ventana)
            return
        
        db = DBManager()
        exito = db.registrar_usuario(alias.strip(), rango, saldo_inicial)
        
        if exito:
            messagebox.showinfo("Registro Exitoso", f"El Usuario '{alias}' ha sido incorporado al sistema correctamente")
            ventana.destroy()
        else:
            messagebox.showerror("Error del Sistema", "No se pudo completar el registro en la Base de Datos.", parent=ventana)            
     
    def abrir_ventana_recarga(self):
        """Abre una ventana modal para inyectar saldo al usuario activo"""
        usuario_actual = self.usuario_prueba
        
        ventana_recarga = tk.Toplevel(self)
        ventana_recarga.title("Recarga de billetera")
        ventana_recarga.geometry("300x250")
        ventana_recarga.config(bg="#f4f4f9")
        ventana_recarga.resizable(False, False)
        ventana_recarga.grab_set() #ventana modal
        
        tk.Label(ventana_recarga, text="Caja - Recarga Saldo", font=("Arial", 12, "bold"), bg="#f4f4f9").pack(pady=15)
        tk.Label(ventana_recarga, text=f"Gamer: {usuario_actual.alias_gamer}", font=("Arial", 11), bg="#f4f4f9").pack()
        tk.Label(ventana_recarga, text=f"Saldo Actual: S/ {usuario_actual.saldo_billetera:.2f}", font=("Arial", 10), fg="gray", bg="#f4f4f9").pack(pady=(0, 15))
        
        tk.Label(ventana_recarga, text="Monto a recargar (S/):", font=("Arial", 10, "bold"), bg="#f4f4f9").pack()
        
        entry_monto = tk.Entry(ventana_recarga, font=("Arial", 14), width=15, justify="center")
        entry_monto.pack(pady=10)
        entry_monto.focus()
        
        btn_confirmar = tk.Button(
            ventana_recarga,
            text="Confirmar Recarga",
            bg="#c8e6c9",
            font=("Arial", 10, "bold"),
            command=lambda: self.procesar_recarga(entry_monto.get(), ventana_recarga)
        )
        btn_confirmar.pack(pady=15)
        
    def procesar_recarga(self, monto_texto, ventana):
        """"Valida el dinero, actualiza el modelo y guarda en la base de datos"""
        try:
            monto = float(monto_texto)
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "Ingresa un monto numérico mayor a cero")
            return
        
        self.usuario_prueba.recargar_saldo(monto)
        
        db = DBManager()
        db.actualizar_saldo_usuario(self.usuario_prueba.id_usuario, self.usuario_prueba.saldo_billetera)
        
        self.dibujar_panel_usuario()
        messagebox.showinfo("Recarga Exitosa", f"Se ha recargado S/ {monto:.2f} a la billetera de {self.usuario_prueba.alias_gamer}.\nNuevo saldo: S/ {self.usuario_prueba.saldo_billetera:.2f}")
        ventana.destroy()
            
    def cerrar_sesion(self, maquina_seleccionada: EstacionTrabajo):
        """Se ejecuta al hacer clic en Cerrar Sesión"""
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
                
                messagebox.showinfo("Sesión Finalizada", f"Cobro a usuario '{usuario_original.alias_gamer}' exitoso.\nNuevo saldo: S/ {usuario_original.saldo_billetera:.2f}")        

            except SaldoInsuficienteError as e:
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
        for id_estacion, sesion in self.sesiones_activas.items():
            if id_estacion in self.labels_cronometros:
                # Calculamos cuántos segundos han pasado
                diferencia = tiempo_actual - sesion.hora_inicio
                segundos_totales = int(diferencia.total_seconds())
                
                # Convertimos los segundos a formato HH:MM:SS
                horas = segundos_totales // 3600
                minutos = (segundos_totales % 3600) // 60
                segundos = segundos_totales % 60
                
                # Formateamos el texto (ej: ⏱️ 00:05:09)
                texto_reloj = f"⏱️ {horas:02d}:{minutos:02d}:{segundos:02d}"
                
                # Actualizamos la etiqueta en la pantalla
                self.labels_cronometros[id_estacion].config(text=texto_reloj)
                
        #Le decimos a Tkinter que vuelva a ejecutar esta función en 1000 milisegundos (1 segundo)
        self.after(1000, self.actualizar_cronometros)
    
    
    
if __name__ == "__main__":
    app = AppCyberReinoso()
    app.mainloop()