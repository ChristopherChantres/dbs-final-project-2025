from dataclasses import dataclass
from datetime import date, time
from enum import Enum
from typing import Optional

# Enums basados en las restricciones del esquema
class Rol(str, Enum):
    ESTUDIANTE = "Estudiante"
    PROFESOR = "Profesor"
    ADMINISTRADOR = "Administrador"

class TipoSalon(str, Enum):
    AULA = "Aula"
    LABORATORIO = "Laboratorio"
    AUDITORIO = "Auditorio"

class DiaSemana(str, Enum):
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miercoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sabado"
    DOMINGO = "Domingo"

# Tipo de retorno de las funciones [bool, str] para las transacciones
# class RetornoTransaccion(str, Enum):
#     BOOL: bool
#     MSJ: str

# Modelos de dominio

@dataclass
class Periodo:
    id_periodo: str
    fecha_inicio: date
    fecha_fin: date

@dataclass
class Materia:
    clave: str
    titulo: str

@dataclass
class Salon:
    id_salon: str
    capacidad: int
    tipo: TipoSalon

@dataclass
class Usuario:
    id_usuario: str
    nombre: str
    rol: Rol

@dataclass
class Curso:
    clave_materia: str
    seccion: int
    id_periodo: str
    profesor: Optional[str] = None

@dataclass
class Horario:
    id_horario: Optional[int]
    clave_materia: str
    seccion_curso: int
    id_periodo: str
    id_salon: str
    dia_semana: DiaSemana
    hora_inicio: time
    duracion_minutos: int

@dataclass
class Reservacion:
    id_reservacion: Optional[int]
    id_usuario: str
    id_salon: str
    id_periodo: str
    fecha: date
    hora_inicio: time
    duracion_minutos: int
    motivo: Optional[str] = None

