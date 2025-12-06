from datetime import date

def obtener_fechas_periodo(tipo: str, anio: int) -> tuple[date, date]:
    """
    Calcula fecha inicio y fin basado en el tipo de periodo.
    OTOÑO: Ago 1 - Dic 10
    PRIMAVERA: Ene 15 - May 20
    """
    if tipo == "OTOÑO":
        return date(anio, 8, 1), date(anio, 12, 10)
    else:  # PRIMAVERA
        return date(anio, 1, 15), date(anio, 5, 20)

