from dataclasses import dataclass
from datetime import date, time
from enum import Enum
from typing import Optional

# Enums basados en las restricciones del esquema
class TipoPeriodo(str, Enum):
    OTONO = "OTOÑO"
    PRIMAVERA = "PRIMAVERA"

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