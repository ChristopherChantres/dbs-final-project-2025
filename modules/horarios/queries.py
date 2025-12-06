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
                h.id_horario,
                h.hora_inicio,
                h.duracion_minutos,
                h.dia_semana,
                s.id_salon,
                s.tipo           AS tipo_salon,
                s.capacidad,
                m.titulo         AS materia,
                c.clave_materia  AS curso_clave,
                c.seccion        AS curso_seccion,
                c.profesor,
                p.id_periodo,
                p.fecha_inicio,
                p.fecha_fin
            FROM horario h
            JOIN curso c
                ON h.clave_materia = c.clave_materia
               AND h.seccion_curso = c.seccion
               AND h.id_periodo = c.id_periodo
            JOIN materia m
                ON m.clave = c.clave_materia
            JOIN salon s
                ON s.id_salon = h.id_salon
            JOIN periodo p
                ON p.id_periodo = c.id_periodo
            ORDER BY p.id_periodo, c.clave_materia, c.seccion, h.hora_inicio;
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
                h.id_horario,
                h.hora_inicio,
                h.duracion_minutos,
                h.dia_semana,
                s.id_salon,
                s.tipo AS tipo_salon,
                m.titulo AS materia,
                c.clave_materia AS curso_clave,
                c.seccion AS curso_seccion,
                c.profesor
            FROM horario h
            JOIN curso c
                ON h.clave_materia = c.clave_materia
               AND h.seccion_curso = c.seccion
               AND h.id_periodo = c.id_periodo
            JOIN materia m
                ON m.clave = c.clave_materia
            JOIN salon s
                ON s.id_salon = h.id_salon
            WHERE c.id_periodo = %s
        """

        params = [id_periodo]

        
        if dia_semana:
            query += " AND h.dia_semana = %s"
            params.append(dia_semana)

        query += " ORDER BY h.hora_inicio ASC;"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print(" Error MySQL:", err)
        return pd.DataFrame()

