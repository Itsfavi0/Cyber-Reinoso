"""
CAPA DE NEGOCIO
Este archivo define la estructura de objetos puramente en memoria RAM y las reglas de negocio 
del Lan Center, aislando por completo la lógica comercial de las pantallas (UI) y de la base de datos.
"""

from abc import ABC, abstractmethod
from datetime import datetime

# =========================================================================
# EXCEPCIONE PERSONALIZADA
# =========================================================================
class SaldoInsuficienteError(Exception):
    """Excepción para controlar transacciones denegadas por falta de dinero."""
    pass

# =========================================================================
# ENTIDAD: USUARIO (Gamer y Fidelización)
# =========================================================================
class Usuario:
    def __init__(self, id_usuario, alias_gamer, rango_cuenta, saldo_billetera, minutos_acumulados=0, estado = 1):
        # 'self' hace referencia al objeto específico que se está creando en memoria.
        self.id_usuario = id_usuario
        self.alias_gamer = alias_gamer
        
        # str(), float(), int() son 'Casteos' (conversiones explícitas de tipo de dato)
        # Garantizan que los datos que vienen de la BD como textos u objetos raros pesen y operen correctamente.
        self.rango_cuenta = str(rango_cuenta)
        
        # El doble guion bajo '__' convierte la variable en PRIVADA.
        self.__saldo_billetera = float(saldo_billetera)
        self.minutos_acumulados = int(minutos_acumulados)
        self.estado = int(estado)

        #Cada vez que Python reconstruye al usuario, evalúa instantáneamente su nivel.
        self.rango_cuenta = self.evaluar_rango_por_minutos()
        
    @property
    def saldo_billetera(self):
        """
        DECORADOR @property (Getter): Permite leer el saldo privado '__saldo_billetera'
        desde fuera de la clase de forma segura como si fuera un atributo público (usuario.saldo_billetera),
        pero bloquea cualquier intento de asignación directa (usuario.saldo_billetera = 500) provocando un error.
        """
        return self.__saldo_billetera
    
    @property
    def porcentaje_descuento(self):
        """
        Usa una estructura de Diccionario (Llave: Valor) para mapear beneficios.
        Es mucho más eficiente (Complejidad O(1)) que usar múltiples bloques 'if/elif' anidados.
        """
        tabla_beneficios = {
            "Bronce": 0.0,      # 0% de descuento
            "Plata": 0.05,      # 5% de descuento
            "Oro": 0.10,        # 10% de descuento
            "Diamante": 0.15    # 15% de descuento
        }
        # .get() busca la llave en el diccionario. Si no existe, devuelve el valor por defecto (0.0)
        return tabla_beneficios.get(self.rango_cuenta, 0.0)
    
    def evaluar_rango_por_minutos(self):
        """
        REGLA DE NEGOCIO: Define la escala de fidelización según el tiempo del gamer.
        Si las metas de minutos cambian en el futuro, solo se modifica este método.
        """        
        if self.minutos_acumulados < 600:
            return "Bronce"
        elif self.minutos_acumulados < 3000:
            return "Plata"
        elif self.minutos_acumulados < 6000:
            return "Oro"
        else:
            return "Diamante"
        
    def agregar_minutos_jugados(self, minutos):
        """
        ALGORITMO DE LOGRO: Almacena temporalmente el rango previo para compararlo 
        con el nuevo cálculo. Retorna un booleano (True/False) que la UI usa para 
        disparar una alerta visual de felicitación al usuario en caliente.
        """
        rango_anterior = self.rango_cuenta
        self.minutos_acumulados += minutos
        self.rango_cuenta = self.evaluar_rango_por_minutos()
        
        # Retorna True si el usuario acaba de subir de rango para mostrarle una alerta de felicitación
        return rango_anterior != self.rango_cuenta
    
    def recargar_saldo(self, monto: float):
        # Validamos las entradas antes de operar en la RAM.
        if monto <= 0:
            raise ValueError("El monto a recargar debe ser mayor a cero.")
        self.__saldo_billetera += monto
        
    def descontar_saldo(self, costo: float):
        # Lanza nuestra excepción si la operación no es viable económicamente.
        if costo > self.saldo_billetera:
            raise SaldoInsuficienteError(f"Operación denegada. {self.alias_gamer} no tiene saldo suficiente.")
        self.__saldo_billetera -= costo

    def descontar_saldo_hasta_cero(self, costo: float):
        """
        ALGORITMO DE CORTE AUTOMÁTICO (Kill Switch): Si el costo del tiempo supera lo que tiene el usuario,
        vaciamos la billetera por completo, capturamos exactamente cuántos céntimos se pudieron cobrar,
        y devolvemos ese monto para actualizar las métricas de caja en SQL.
        """
        if costo > self.saldo_billetera:
            cobrado = self.__saldo_billetera
            self.__saldo_billetera = 0.0
            return cobrado
        else:
            self.__saldo_billetera -= costo
            return costo
        
    def __str__(self):
        """
        SOBREESCRITURA DE MÉTODO: Modifica el comportamiento nativo de print(usuario).
        En vez de mostrar un puntero de memoria ilegible, devuelve una cadena formateada limpia.
        ':.2f' le dice a Python que formatee el número flotante a exactamente 2 decimales.
        """
        return f"Gamer: {self.alias_gamer} | Rango: {self.rango_cuenta} | Saldo: S/{self.saldo_billetera:.2f}"

# =========================================================================
# ENTIDAD: ESTACIÓN DE TRABAJO (Infraestructura de Hardware)
# =========================================================================
class EstacionTrabajo(ABC):
    """
    CLASE BASE ABSTRACTA (ABC): No se puede instanciar directamente en el mapa (no puedes hacer estacion = EstacionTrabajo()).
    Su único propósito es definir un molde genérico y contratos obligatorios para sus hijas mediante decoradores.
    """
    # ATRIBUTO DE CLASE: Variable global compartida por todas las instancias de computadoras.
    # Funciona como un contador estático en memoria RAM de cuántas máquinas se han mapeado al iniciar.
    total_pcs_registradas = 0
    
    def __init__(self, id_estacion : int, codigo_pc: str, tarifa_hora: float, especificaciones=None):
        self.id_estacion = id_estacion
        self.codigo_pc = codigo_pc
        self.tarifa_hora = float(tarifa_hora)
        self.__estado = "Disponible"
        
        # 'or {}'. Si 'especificaciones' llega vacío (None),
        # Python le asigna un diccionario vacío para evitar que los métodos de la UI tiren un AttributeError.
        self.especificaciones = especificaciones or {}

        # Incrementamos el contador estático global de la clase
        EstacionTrabajo.total_pcs_registradas += 1
        
    @property
    def estado(self):
        return self.__estado
    
    @estado.setter
    def estado(self, nuevo_estado : str):
        """
        SETTER CON VALIDACIÓN: Protege los estados permitidos de los módulos. 
        Si un programador escribe mal un estado en el backend (ej. 'disponible' en minúscula),
        el sistema frena la asignación impidiendo estados corruptos en el mapa de PCs.
        """
        estados_permitidos = ["Disponible", "Ocupada", "Mantenimiento", "Hibernación"]
        if nuevo_estado not in estados_permitidos:
            raise ValueError(f"Estado '{nuevo_estado}' no es válido")
        self.__estado = nuevo_estado
        
    @property
    @abstractmethod
    def categoria(self) -> str:
        """
        MÉTODO ABSTRACTO: Fuerza a todas las subclases hijas a implementar una propiedad 'categoria'.
        Si alguna hija no lo hace, Python frena la ejecución al compilar.
        """
        pass
    
    @abstractmethod
    def calcular_tarifa(self, minutos : int) -> float:
        """Contrato obligatorio para que cada tipo de gama calcule el costo a su propio ratio."""
        pass
    
# =========================================================================
# SUBCLASES ESPECIALIZADAS (Aplicación de Polimorfismo)
# =========================================================================
class PC_Regular(EstacionTrabajo):
    def __init__(self, id_estacion, codigo_pc, tarifa_hora, especificaciones=None):
        # 'super().__init__' invoca al constructor de la clase padre (EstacionTrabajo)
        # para inicializar los atributos base sin duplicar código.
        super().__init__(id_estacion, codigo_pc, tarifa_hora, especificaciones)

    @property
    def categoria(self) -> str:
        return "Regular"
    
    def calcular_tarifa(self, minutos) -> float:
        """POLIMORFISMO: PC_Regular ejecuta el cálculo bajo su tarifa dinámica configurada en la BD."""
        tarifa_minuto = self.tarifa_hora / 60
        return round(minutos * tarifa_minuto, 2)

class PC_eSports(EstacionTrabajo):
    def __init__(self, id_estacion, codigo_pc, tarifa_hora, especificaciones=None):
        super().__init__(id_estacion, codigo_pc, tarifa_hora, especificaciones)

    @property
    def categoria(self) -> str:
        return "eSports"
    
    def calcular_tarifa(self, minutos) -> float:
        """POLIMORFISMO: PC_eSports ejecuta el cálculo bajo su tarifa dinámica configurada en la BD."""
        tarifa_minuto = self.tarifa_hora / 60
        return round(minutos * tarifa_minuto, 2)

class PC_StreamingVIP(EstacionTrabajo):
    def __init__(self, id_estacion, codigo_pc, tarifa_hora, especificaciones=None):
        super().__init__(id_estacion, codigo_pc, tarifa_hora, especificaciones)

    @property
    def categoria(self) -> str:
        return "Streaming VIP"
    
    def calcular_tarifa(self, minutos) -> float:
        """POLIMORFISMO: PC_StreamingVIP ejecuta el cálculo bajo su tarifa dinámica configurada en la BD."""
        tarifa_minuto = self.tarifa_hora / 60
        return round(minutos * tarifa_minuto, 2)

# =========================================================================
# ENTIDAD: SESIÓN (Control de Tiempos y Consumo)
# =========================================================================
class Sesion:
    def __init__(self, id_sesion: int, usuario: Usuario, estacion: EstacionTrabajo, hora_inicio=None):
        self.id_sesion = id_sesion
        self.usuario = usuario      # Agregamos un objeto Usuario entero (Asociación/Agregación)
        self.estacion = estacion    # Agregamos un objeto EstacionTrabajo entero (Asociación/Agregación)
        
        # INICIALIZACIÓN FLEXIBLE: Si levantamos una sesión activa desde SQL, usamos su hora guardada.
        # Si es un click nuevo en la UI, capturamos el tiempo exacto del sistema en ese milisegundo.
        self.hora_inicio = hora_inicio if hora_inicio else datetime.now()
        self.hora_fin = None
        self.monto_cobrado = 0.0
        
        # EFECTO COLATERAL CONTROLADO: Al crear una sesión, cambiamos automáticamente 
        # el estado de la PC asociada, notificando a la interfaz gráfica del cambio.
        self.estacion.estado = "Ocupada"
        
    def finalizar_sesion(self, es_corte_automatico=False):
        """
        ALGORITMO DE AUDITORÍA Y COBRO: Detiene el tiempo, calcula los minutos reales 
        transcurridos, descuenta el beneficio de rango VIP, y altera los saldos del objeto.
        """
        if self.hora_fin is not None:
            raise ValueError("Esta sesión ya fue finalizada anteriormente.")
        
        self.hora_fin = datetime.now()
        
        # CÁLCULO DE TIEMPO
        diferencia = self.hora_fin - self.hora_inicio
        minutos_consumidos = int(diferencia.total_seconds() / 60)
        
        # Si el cliente abrió y cerró la sesión en menos de un minuto,
        # se le cobra como mínimo 1 minuto completo para evitar consumos de S/ 0.00.
        if minutos_consumidos == 0:
            minutos_consumidos = 1
            
        # Python sabe exactamente a qué tarifa llamará (Regular/eSports/VIP) 
        # basándose en el tipo de objeto real que esté guardado dentro de 'self.estacion'.
        costo_base = self.estacion.calcular_tarifa(minutos_consumidos)
        
        # APLICACIÓN DE FIDELIZACIÓN (Producido en memoria RAM)
        descuento = costo_base * self.usuario.porcentaje_descuento
        monto_a_cobrar = costo_base - descuento
        
        # GESTIÓN TRANSACCIONAL SEGÚN EL DISPARADOR (Trigger)
        if es_corte_automatico or monto_a_cobrar > self.usuario.saldo_billetera:
            self.monto_cobrado = self.usuario.descontar_saldo_hasta_cero(monto_a_cobrar)
        else:
            self.usuario.descontar_saldo(monto_a_cobrar)
            self.monto_cobrado = monto_a_cobrar
            
        # RESTAURACIÓN DEL MAPA: La PC vuelve a estar disponible para el próximo cliente.
        self.estacion.estado = "Disponible"
        
    def __add__(self, otra_sesion):
        """
        SOBRECARGA DE OPERADORES (MÉTODO MÁGICO __add__): Permite sumar dos objetos 
        de tipo Sesion directamente con el símbolo '+' (sesion1 + sesion2).
        Retorna la suma acumulada del dinero cobrado, ideal para consolidar los reportes de caja de hoy.
        """
        if isinstance(otra_sesion, Sesion):
            return self.monto_cobrado + otra_sesion.monto_cobrado
        raise TypeError("Solo puedes sumar un objeto Sesion con otro objeto Sesion")