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
        
    def __str__(self):
        return f"Gamer: {self.alias_gamer} | Rango: {self.rango_cuenta} | Saldo: S/{self.saldo_billetera:.2f}"

# Superclase Abstracta
class EstacionTrabajo(ABC):
    total_pcs_registradas = 0
    
    def __init__(self, id_estacion : int, codigo_pc: str):
        self.id_estacion = id_estacion
        self.codigo_pc = codigo_pc
        self.__estado = "Disponible"
        
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
        
    def __add__(self, otra_sesion):
        """Permite sumar objetos Sesion directamente"""
        if isinstance(otra_sesion, Sesion):
            return self.monto_cobrado + otra_sesion.monto_cobrado
        raise TypeError("Solo puedes sumar un objeto Sesion con otro objeto Sesion")
    
# --- PRUEBAS ---
if __name__ == "__main__":
    import time
    
    # 1. Creamos dos usuarios de prueba
    gamer1 = Usuario(1, "Favio", "VIP", 50.00)
    gamer2 = Usuario(2, "Sandro", "Regular", 20.00)
    
    # Imprimimos al usuario para probar el __str__
    print(gamer1)
    
    # 2. Asignamos máquinas
    pc1 = PC_VIP(1, "PC-01")
    pc2 = PC_Regular(2, "PC-02")
    
    print(f"Total de PCs registradas en la clase: {EstacionTrabajo.total_pcs_registradas}")
    
    # 3. Iniciamos las sesiones
    sesion1 = Sesion(101, gamer1, pc1)
    sesion2 = Sesion(102, gamer2, pc2)
    
    print("Simulando tiempo de juego (espera 2 segundos)...")
    time.sleep(2)
    
    # 4. Finalizamos las sesiones (esto calcula el dinero)
    sesion1.finalizar_sesion()
    sesion2.finalizar_sesion()
    
    # 5. Sumamos los objetos directamente, Python sabe que debe sumar los montos
    total_grupal = sesion1 + sesion2
    
    print(f"Cobro PC 1: S/ {sesion1.monto_cobrado:.2f}")
    print(f"Cobro PC 2: S/ {sesion2.monto_cobrado:.2f}")
    print(f"Total a cobrar al grupo (usando s1 + s2): S/ {total_grupal:.2f}")