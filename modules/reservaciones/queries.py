# ⚠️ ACID Logic: create_secure_reservation()
import pandas as pd
from config.db import get_connection
import mysql.connector
from datetime import date, time

def obtener_disponibilidad_salones(fecha: date, hora_inicio: time, duracion_min: int) -> pd.DataFrame:
    """
    Returns available classrooms by checking against both:
    1. Recurring class schedules (Horario) active during the period of the given date.
    2. One-time reservations (Reservacion) on the specific date.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Helper: Map Python weekday (0=Monday) to DB Enum ('Lunes', etc.)
        dias_semana = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
        dia_nombre = dias_semana[fecha.weekday()]
        
        hora_str = hora_inicio.strftime("%H:%M:%S")

        # Logic: 
        # Exclude salons where (StartRequested < EndExisting) AND (StartExisting < EndRequested)
        # For Horario: We also check if 'fecha' is within the Period range (fecha_inicio, fecha_fin).

        query = """
            SELECT 
                s.id_salon,
                s.tipo,
                s.capacidad
            FROM salon s
            WHERE s.id_salon NOT IN (
                -- Check Recurring Classes (Horario)
                SELECT h.id_salon
                FROM horario h
                JOIN periodo p ON h.id_periodo = p.id_periodo
                WHERE h.dia_semana = %s
                  AND %s BETWEEN p.fecha_inicio AND p.fecha_fin
                  -- Overlap check:
                  AND h.hora_inicio < ADDTIME(%s, SEC_TO_TIME(%s * 60))
                  AND %s < ADDTIME(h.hora_inicio, SEC_TO_TIME(h.duracion_minutos * 60))
                
                UNION
                
                -- Check One-time Reservations (Reservacion)
                SELECT r.id_salon
                FROM reservacion r
                WHERE r.fecha = %s
                  -- Overlap check:
                  AND r.hora_inicio < ADDTIME(%s, SEC_TO_TIME(%s * 60))
                  AND %s < ADDTIME(r.hora_inicio, SEC_TO_TIME(r.duracion_minutos * 60))
            )
            ORDER BY s.id_salon;
        """

        # Params must match the %s order exactly:
        # Part 1 (Horario): dia_nombre, fecha, hora_str, duracion_min, hora_str
        # Part 2 (Reservacion): fecha, hora_str, duracion_min, hora_str
        params = (
            dia_nombre, fecha, hora_str, duracion_min, hora_str,
            fecha, hora_str, duracion_min, hora_str
        )
        
        cursor.execute(query, params)
        rows = cursor.fetchall()

        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print("❌ Error SQL:", err)
        return pd.DataFrame()
    finally:
        if cursor:
            cursor.close()


def obtener_ocupacion_salon(id_salon: str) -> pd.DataFrame:
    """
    Obtiene la ocupación de un salón en un día específico.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Fixed column names (camelCase -> snake_case) and JOIN logic
        query = """
            SELECT 
                s.id_salon,
                s.tipo,
                s.capacidad,
                h.id_horario,
                h.hora_inicio,
                h.duracion_minutos,
                h.dia_semana,
                m.titulo AS materia,
                c.clave_materia AS curso_clave,
                c.seccion AS seccion,
                c.profesor,
                p.id_periodo,
                p.fecha_inicio,
                p.fecha_fin
            FROM horario h
            JOIN salon s         ON h.id_salon = s.id_salon
            JOIN curso c         ON h.clave_materia = c.clave_materia
                                 AND h.seccion_curso = c.seccion
                                 AND h.id_periodo = c.id_periodo
            JOIN materia m       ON m.clave = c.clave_materia
            JOIN periodo p       ON p.id_periodo = c.id_periodo
            WHERE s.id_salon = %s
            ORDER BY h.dia_semana, h.hora_inicio;
        """

        cursor.execute(query, (id_salon,))
        rows = cursor.fetchall()

        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print("❌ Error SQL:", err)
        return pd.DataFrame()
    finally:
        if cursor:
            cursor.close()

def obtener_mis_reservaciones(id_usuario: str) -> pd.DataFrame:
    """
    Obtiene las reservaciones de un usuario.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Fixed table/column names and JOIN condition
        query = """
            SELECT 
                r.id_reservacion,
                r.id_periodo,
                r.id_salon,
                r.fecha,
                r.hora_inicio,
                r.duracion_minutos,
                r.motivo,
                u.nombre AS usuario
            FROM reservacion r
            JOIN usuario u ON r.id_usuario = u.id_usuario
            WHERE r.id_usuario = %s
            ORDER BY r.fecha DESC;
        """

        cursor.execute(query, (id_usuario,))
        rows = cursor.fetchall()

        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print("❌ Error SQL:", err)
        return pd.DataFrame()
    finally:
        if cursor:
            cursor.close()