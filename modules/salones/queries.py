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
                id_salon,
                capacidad,
                tipo
            FROM salon
            ORDER BY id_salon;
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
                id_salon,
                capacidad,
                tipo
            FROM salon
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
    

def obtener_periodos() -> pd.DataFrame:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id_periodo FROM periodo ORDER BY fecha_inicio DESC;"
        cursor.execute(query)
        rows = cursor.fetchall()
        return pd.DataFrame(rows)
    except mysql.connector.Error as err:
        print(" Error SQL:", err)
        return pd.DataFrame()


def obtener_top_salones_ocupados(periodo_id: str, limit: int = 5) -> pd.DataFrame:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                s.id_salon,
                s.tipo,
                s.capacidad,
                COALESCE(SUM(h.duracion_minutos), 0) AS horas_ocupadas
            FROM salon s
            JOIN horario h ON h.id_salon = s.id_salon
            WHERE h.id_periodo = %s
            GROUP BY s.id_salon, s.tipo, s.capacidad
            ORDER BY horas_ocupadas DESC
            LIMIT %s;
        """

        cursor.execute(query, (periodo_id, limit))
        rows = cursor.fetchall()
        
        if rows:
            for row in rows:
                 # Convertir minutos a horas (float)
                if row['horas_ocupadas']:
                    row['horas_ocupadas'] = float(row['horas_ocupadas']) / 60.0
                else:
                    row['horas_ocupadas'] = 0.0
        
        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print(" Error SQL:", err)
        return pd.DataFrame()
    