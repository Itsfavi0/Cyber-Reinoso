from abc import ABC, abstractmethod
from datetime import datetime

class SaldoInsuficienteError(Exception):
    """Excepción para controlar transacciones denegadas por falta de dinero."""
    pass

class Usuario:
    def __init__(self, id_usuario, alias_gamer, rango_cuenta, saldo_billetera, minutos_acumulados=0):
        self.id_usuario = id_usuario
        self.alias_gamer = alias_gamer
        self.rango_cuenta = str(rango_cuenta)
        self.__saldo_billetera = float(saldo_billetera)
        self.minutos_acumulados = int(minutos_acumulados)
        #calculamos los minutos para tener el rango
        self.rango_cuenta = self.evaluar_rango_por_minutos()
        
    @property
    def saldo_billetera(self):
        return self.__saldo_billetera
    
    @property
    def porcentaje_descuento(self):
        """Retorna el porcentaje de descuento aplicable según el rango actual del jugador"""
        tabla_beneficios = {
            "Bronce": 0.0,       # 0% de descuento
            "Plata": 0.05,      # 5% de descuento
            "Oro": 0.10,        # 10% de descuento
            "Global VIP": 0.20  # 20% de descuento
        }
        return tabla_beneficios.get(self.rango_cuenta, 0.0)
    
    def evaluar_rango_por_minutos(self):
        """Lógica de negocio: Define el rango del jugador según su tiempo invertido"""
        if self.minutos_acumulados < 600:
            return "Bronce"
        elif self.minutos_acumulados < 3000:
            return "Plata"
        elif self.minutos_acumulados < 6000:
            return "Oro"
        else:
            return "Global VIP"
        
    def agregar_minutos_jugados(self, minutos):
        """Suma los minutos de la sesión terminada y recalcula el rango"""
        rango_anterior = self.rango_cuenta
        self.minutos_acumulados += minutos
        self.rango_cuenta = self.evaluar_rango_por_minutos()
        
        # Retorna True si el usuario acaba de subir de rango para mostrarle una alerta de felicitación
        return rango_anterior != self.rango_cuenta
    
    def recargar_saldo(self, monto: float):
        if monto <= 0:
            raise ValueError("El monto a recargar debe ser mayor a cero.")
        self.__saldo_billetera += monto
        
    def descontar_saldo(self, costo: float):
        if costo > self.saldo_billetera:
            raise SaldoInsuficienteError(f"Operación denegada. {self.alias_gamer} no tiene saldo suficiente.")
        self.__saldo_billetera -= costo

    def descontar_saldo_hasta_cero(self, costo: float):
        """Descuenta el saldo del usuario; si el costo es mayor, descuenta lo que queda y retorna lo cobrado."""
        if costo > self.saldo_billetera:
            cobrado = self.__saldo_billetera
            self.__saldo_billetera = 0.0
            return cobrado
        else:
            self.__saldo_billetera -= costo
            return costo
        
    def __str__(self):
        return f"Gamer: {self.alias_gamer} | Rango: {self.rango_cuenta} | Saldo: S/{self.saldo_billetera:.2f}"

# Superclase Abstracta
class EstacionTrabajo(ABC):
    total_pcs_registradas = 0
    
    def __init__(self, id_estacion : int, codigo_pc: str, especificaciones=None):
        self.id_estacion = id_estacion
        self.codigo_pc = codigo_pc
        self.__estado = "Disponible"
        self.especificaciones = especificaciones or {}

        EstacionTrabajo.total_pcs_registradas += 1
        
    @property
    def estado(self):
        return self.__estado
    
    @estado.setter
    def estado(self, nuevo_estado : str):
        estados_permitidos = ["Disponible", "Ocupada", "Mantenimiento", "Hibernación"]
        if nuevo_estado not in estados_permitidos:
            raise ValueError(f"Estado '{nuevo_estado}' no es válido")
        self.__estado = nuevo_estado
        
    @property
    @abstractmethod
    def categoria(self) -> str:
        pass
    
    @abstractmethod
    def calcular_tarifa(self, minutos : int) -> float:
        pass
    
# Subclases
class PC_Regular(EstacionTrabajo):
    def __init__(self, id_estacion, codigo_pc, especificaciones=None):
        super().__init__(id_estacion, codigo_pc, especificaciones)

    @property
    def categoria(self) -> str:
        return "Regular"
    
    def calcular_tarifa(self, minutos) -> float:
        tarifa_minuto = 2.00 / 60
        return round(minutos * tarifa_minuto, 2)

class PC_eSports(EstacionTrabajo):
    def __init__(self, id_estacion, codigo_pc, especificaciones=None):
        super().__init__(id_estacion, codigo_pc, especificaciones)

    @property
    def categoria(self) -> str:
        return "eSports"
    
    def calcular_tarifa(self, minutos) -> float:
        tarifa_minuto = 3.00 / 60
        return round(minutos * tarifa_minuto, 2)

class PC_StreamingVIP(EstacionTrabajo):
    def __init__(self, id_estacion, codigo_pc, especificaciones=None):
        super().__init__(id_estacion, codigo_pc, especificaciones)

    @property
    def categoria(self) -> str:
        return "Streaming VIP"
    
    def calcular_tarifa(self, minutos) -> float:
        tarifa_minuto = 5.00 / 60
        return round(minutos * tarifa_minuto, 2)
    
class Sesion:
    def __init__(self, id_sesion: int, usuario: Usuario, estacion: EstacionTrabajo, hora_inicio=None):
        self.id_sesion = id_sesion
        self.usuario = usuario
        self.estacion = estacion
        
        # Si se recupera de la BD, usamos su hora de inicio guardada; si es nueva, usamos datetime.now()
        self.hora_inicio = hora_inicio if hora_inicio else datetime.now()
        self.hora_fin = None
        self.monto_cobrado = 0.0
        
        # Al iniciar una sesion la maquina cambia de estado a ocupada
        self.estacion.estado = "Ocupada"
        
    def finalizar_sesion(self, es_corte_automatico=False):
        """Detenemos el cronómetro, calcula los minutos y cobra al usuario."""
        if self.hora_fin is not None:
            raise ValueError("Esta sesión ya fue finalizada anteriormente.")
        
        self.hora_fin = datetime.now()
        
        diferencia = self.hora_fin - self.hora_inicio
        minutos_consumidos = int(diferencia.total_seconds() / 60)
        
        if minutos_consumidos == 0:
            minutos_consumidos = 1
        
        costo_base = self.estacion.calcular_tarifa(minutos_consumidos)
        
        descuento = costo_base * self.usuario.porcentaje_descuento
        monto_a_cobrar = costo_base - descuento
        
        if es_corte_automatico or monto_a_cobrar > self.usuario.saldo_billetera:
            self.monto_cobrado = self.usuario.descontar_saldo_hasta_cero(monto_a_cobrar)
        else:
            self.usuario.descontar_saldo(monto_a_cobrar)
            self.monto_cobrado = monto_a_cobrar
            
        self.estacion.estado = "Disponible"
        
    def __add__(self, otra_sesion):
        """Permite sumar objetos Sesion directamente"""
        if isinstance(otra_sesion, Sesion):
            return self.monto_cobrado + otra_sesion.monto_cobrado
        raise TypeError("Solo puedes sumar un objeto Sesion con otro objeto Sesion")