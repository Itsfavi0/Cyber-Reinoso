from abc import ABC, abstractmethod

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