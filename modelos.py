from abc import ABC, abstractmethod
from datetime import datetime

class SaldoInsuficienteError(Exception):
    """Excepción para controlar transacciones denegadas por falta de dinero."""
    pass

class Usuario:
    def __init__(self, id_usuario: int, alias_gamer: str, rango_cuenta: str, saldo_inicial: float):
        self.id_usuario = id_usuario
        self.alias_gamer = alias_gamer
        self.rango_cuenta = rango_cuenta
        self.__estado_billetera = saldo_inicial
        
    @property
    def estado_billetera(self):
        return self.__estado_billetera
    
    def recargar_saldo(self, monto: float):
        if monto <= 0:
            raise ValueError("El monto a recargar debe ser mayor a cero.")
        self.__estado_billetera += monto
        
    def descontar_saldo(self, costo: float):
        if costo >= self.estado_billetera:
            raise SaldoInsuficienteError(f"Operación denegada. {self.alias_gamer} no tiene saldo suficiente.")
        self.__estado_billetera -= costo

# Superclase Abstracta
class EstacionTrabajo(ABC):
    def __init__(self, id_estacion : int, codigo_pc: str):
        self.id_estacion = id_estacion
        self.codigo_pc = codigo_pc
        self.__estado = "Disponible"
        
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
    @property
    def categoria(self) -> str:
        return "Regular"
    
    def calcular_tarifa(self, minutos) -> float:
        tarifa_minuto = 2.00/60
        return round(minutos * tarifa_minuto, 2)
    
class PC_VIP(EstacionTrabajo):
    @property
    def categoria(self) -> str:
        return "VIP"
    
    def calcular_tarifa(self, minutos) -> float:
        tarifa_minuto = 3.50/60
        return round(minutos * tarifa_minuto, 2)
    
class Sesion:
    def __init__(self, id_sesion: int, usuario: Usuario, estacion: EstacionTrabajo):
        self.id_sesion = id_sesion
        self.usuario = usuario
        self.estacion = estacion
        
        self.hora_inicio = datetime.now()
        self.hora_fin = None
        self.monto_cobrado = 0.0
        
        self.estacion_estado = "Ocupada"
        
    def finalizar_sesion(self):
        """Detenemos el cronómetro, calcula los minutos y cobra al usuario."""
        if self.hora_fin is not None:
            raise ValueError("Esta sesión ya fue finalizada anteriormente.")
        
        self.hora_fin = datetime.now()
        
        diferencia = self.hora_fin - self.hora_inicio
        minutos_consumidos = int(diferencia.total_seconds() / 60)
        
        if minutos_consumidos == 0:
            minutos_consumidos = 1
            
        self.monto_cobrado = self.estacion.calcular_tarifa(minutos_consumidos)
        
        self.usuario.descontar_saldo(self.monto_cobrado)
        self.estacion.estado = "Disponible"