# ⚠️ ACID Logic: create_secure_reservation()
import pandas as pd
from config.db import get_connection
import mysql.connector
from datetime import date, time


def buscar_disponibilidad_salones(fecha: date, hora_inicio: time, duracion_min: int) -> pd.DataFrame:
   
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        
        hora_str = hora_inicio.strftime("%H:%M:%S")

        query = """
            SELECT 
                s.idSalon,
                s.tipo,
                s.capacidad
            FROM Salon s
            WHERE s.idSalon NOT IN (
                SELECT 
                    h.idSalon
                FROM Horario h
                WHERE 
                    FIND_IN_SET(
                        DAYNAME(%s),
                        REPLACE(h.diasSemana, '-', ',')
                    )
                    -- Chequeo de traslape
                    AND h.hora < ADDTIME(%s, SEC_TO_TIME(%s * 60))
                    AND %s < ADDTIME(h.hora, SEC_TO_TIME(h.duracion * 60))
            )
            ORDER BY s.idSalon;
        """

        params = (fecha, hora_str, duracion_min, hora_str)
        cursor.execute(query, params)
        rows = cursor.fetchall()

        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print("❌ Error SQL:", err)
        return pd.DataFrame()



def obtener_ocupacion_salon(id_salon: str) -> pd.DataFrame:
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                s.idSalon,
                s.tipo,
                s.capacidad,
                h.idHorario,
                h.hora,
                h.duracion,
                h.diasSemana,
                m.titulo AS materia,
                c.clave AS curso_clave,
                c.seccion,
                c.profesor,
                p.idPeriodo,
                p.fecha_inicio,
                p.fecha_fin
            FROM Horario h
            JOIN Salon s         ON h.idSalon = s.idSalon
            JOIN Curso c         ON h.curso_clave = c.clave
                                 AND h.curso_seccion = c.seccion
            JOIN Materia m       ON m.clave = c.clave
            JOIN Periodo p       ON p.idPeriodo = c.idPeriodo
            WHERE s.idSalon = %s
            ORDER BY h.hora;
        """

        cursor.execute(query, (id_salon,))
        rows = cursor.fetchall()

        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print(" Error SQL:", err)
        return pd.DataFrame()
    
def obtener_mis_reservaciones(id_usuario: str) -> pd.DataFrame:
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                r.idPeriodo,
                r.idSalon,
                r.fecha,
                r.duracion,
                u.nombre AS usuario
            FROM Reservacion r
            JOIN Usuario u ON u.idUsuario = %s
            WHERE r.idUsuario = %s
            ORDER BY r.fecha DESC;
        """

        cursor.execute(query, (id_usuario, id_usuario))
        rows = cursor.fetchall()

        return pd.DataFrame(rows)

    except mysql.connector.Error as err:
        print(" Error SQL:", err)
        return pd.DataFrame()
