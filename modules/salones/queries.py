import pandas as pd
from typing import Optional

def obtener_catalogo_salones() -> pd.DataFrame:
    """
    Retorna la lista completa de salones con su ID, capacidad y tipo.
    """
    pass

def obtener_salones_avanzado(capacidad_min: int = 0, tipo: Optional[str] = None) -> pd.DataFrame:
    """
    Filtra los salones. Si 'tipo' es None, trae todos los tipos que cumplan la capacidad.
    """
    pass

def obtener_top_salones_ocupados(limit: int = 5) -> pd.DataFrame:
    """
    Calcula cuáles son los salones con más horas reservadas/ocupadas.
    Retorna un DataFrame listo para graficar en Streamlit.
    """
    pass