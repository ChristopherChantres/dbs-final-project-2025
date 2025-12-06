# Complex SQL: JOINs for readable view
# modules/horarios/queries.py
from config.db import get_connection
import mysql.connector
import pandas as pd

def obtener_horario_completo() -> pd.DataFrame:
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                h.idHorario,
                h.hora,
                h.duracion,
                h.diasSemana,
                s.idSalon,
                s.tipo           AS tipo_salon,
                s.capacidad,
                m.titulo         AS materia,
                c.clave          AS curso_clave,
                c.seccion        AS curso_seccion,
                c.profesor,
                p.idPeriodo,
                p.fecha_inicio,
                p.fecha_fin
            FROM Horario h
            JOIN Curso c
                ON h.curso_clave = c.clave
               AND h.curso_seccion = c.seccion
            JOIN Materia m
                ON m.clave = c.clave
            JOIN Salon s
                ON s.idSalon = h.idSalon
            JOIN Periodo p
                ON p.idPeriodo = c.idPeriodo
            ORDER BY p.idPeriodo, c.clave, c.seccion, h.hora;
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print(" Error MySQL:", err)
        return pd.DataFrame()

    except Exception as e:
        print(" Error inesperado:", e)
        return pd.DataFrame()

def filtrar_horario(id_periodo: str, dia_semana: str = None) -> pd.DataFrame:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT
                h.idHorario,
                h.hora,
                h.duracion,
                h.diasSemana,
                s.idSalon,
                s.tipo AS tipo_salon,
                m.titulo AS materia,
                c.clave AS curso_clave,
                c.seccion AS curso_seccion,
                c.profesor
            FROM Horario h
            JOIN Curso c
                ON h.curso_clave = c.clave
               AND h.curso_seccion = c.seccion
            JOIN Materia m
                ON m.clave = c.clave
            JOIN Salon s
                ON s.idSalon = h.idSalon
            WHERE c.idPeriodo = %s
        """

        params = [id_periodo]

        
        if dia_semana:
            query += " AND FIND_IN_SET(%s, REPLACE(h.diasSemana, '-', ','))"
            params.append(dia_semana)

        query += " ORDER BY h.hora ASC;"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print(" Error MySQL:", err)
        return pd.DataFrame()

