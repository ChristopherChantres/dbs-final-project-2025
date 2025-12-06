import pandas as pd
from typing import Optional
import mysql.connector
from config.db import get_connection

def obtener_catalogo_salones() -> pd.DataFrame:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                idSalon,
                capacidad,
                tipo
            FROM Salon
            ORDER BY idSalon;
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print(" Error SQL:", err)
        return pd.DataFrame()
    

def obtener_salones_avanzado(capacidad_min: int = 0, tipo: Optional[str] = None) -> pd.DataFrame:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                idSalon,
                capacidad,
                tipo
            FROM Salon
            WHERE capacidad >= %s
        """

        params = [capacidad_min]

        
        if tipo is not None:
            query += " AND tipo = %s"
            params.append(tipo)

        query += " ORDER BY capacidad DESC;"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print(" Error SQL:", err)
        return pd.DataFrame()
    

def obtener_top_salones_ocupados(limit: int = 5) -> pd.DataFrame:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                s.idSalon,
                s.tipo,
                s.capacidad,
                SUM(h.duracion) AS horas_ocupadas
            FROM Salon s
            JOIN Horario h ON h.idSalon = s.idSalon
            GROUP BY s.idSalon, s.tipo, s.capacidad
            ORDER BY horas_ocupadas DESC
            LIMIT %s;
        """

        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print(" Error SQL:", err)
        return pd.DataFrame()
    