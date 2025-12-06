# ⚠️ ACID Logic: create_secure_reservation()
from config.db import get_connection
import mysql.connector
def create_secure_reservation(reservation_data):
    # Implement transaction logic for reservation
    pass
def get_available_salons(idPeriodo, hora_inicio, duracion_min, dia):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

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
                JOIN Curso c 
                    ON h.curso_clave = c.clave
                   AND h.curso_seccion = c.seccion
                WHERE 
                    c.idPeriodo = %s
                    AND FIND_IN_SET(%s, h.diasSemana)
                    AND h.hora < ADDTIME(%s, SEC_TO_TIME(%s * 60))
                    AND %s < ADDTIME(h.hora, SEC_TO_TIME(h.duracion * 60))
            )
            ORDER BY s.idSalon;
        """

        params = (idPeriodo, dia, hora_inicio, duracion_min, hora_inicio)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows

    except mysql.connector.Error as err:
        print(" Error MySQL:", err)
        return {"error": str(err)}