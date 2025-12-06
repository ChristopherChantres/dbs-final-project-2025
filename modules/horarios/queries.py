# Complex SQL: JOINs for readable view
# modules/horarios/queries.py
from config.db import get_connection
import mysql.connector  # importante para capturar errores específicos

def get_schedule_view():
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                h.idHorario,
                m.titulo              AS materia,
                c.clave               AS curso_clave,
                c.seccion             AS curso_seccion,
                c.profesor,
                p.idPeriodo,
                p.fecha_inicio,
                p.fecha_fin,
                s.idSalon,
                s.capacidad,
                s.tipo                 AS tipo_salon,
                h.hora,
                h.duracion,
                h.diasSemana
            FROM Horario h
            JOIN Curso   c ON h.curso_clave   = c.clave
                          AND h.curso_seccion = c.seccion
            JOIN Materia m ON c.clave        = m.clave
            JOIN Periodo p ON c.idPeriodo    = p.idPeriodo
            JOIN Salon   s ON h.idSalon      = s.idSalon
            ORDER BY p.idPeriodo, c.clave, c.seccion, h.hora;
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    except mysql.connector.Error as err:
        print(" ERROR en MySQL:", err)
        return {"error": str(err)}

    except Exception as e:
        print(" ERROR inesperado:", e)
        return {"error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
