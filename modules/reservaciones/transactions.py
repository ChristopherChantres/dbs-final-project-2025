from config.db import get_connection
import mysql.connector
from datetime import date, time
from config.db import get_connection
def crear_reservacion(
    id_usuario: int,
    id_salon: str,
    fecha: date,
    hora_inicio: time,
    duracion_min: int,
    id_periodo: int,
) -> tuple[bool, str]:
   

    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        hora_str = hora_inicio.strftime("%H:%M:%S")

       
        conflicto_sql = """
            SELECT idReservacion
            FROM Reservacion
            WHERE idSalon = %s
              AND fecha   = %s
              -- Chequeo de traslape
              AND hora < ADDTIME(%s, SEC_TO_TIME(%s * 60))
              AND %s < ADDTIME(hora, SEC_TO_TIME(duracion * 60))
            FOR UPDATE;
        """
        conflicto_params = (id_salon, fecha, hora_str, duracion_min, hora_str)
        cursor.execute(conflicto_sql, conflicto_params)

        if cursor.fetchone():
            conn.rollback()
            return False, "El salón ya tiene una reservación que se traslapa con ese horario."

        
        insert_sql = """
            INSERT INTO Reservacion (idUsuario, idSalon, idPeriodo, fecha, hora, duracion)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        insert_params = (id_usuario, id_salon, id_periodo, fecha, hora_str, duracion_min)
        cursor.execute(insert_sql, insert_params)

        conn.commit()
        return True, "Reservación creada correctamente"

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return False, f"Error al crear la reservación: {err}"

    finally:
        if cursor:
            cursor.close()

def cancelar_reservacion(id_reservacion: int) -> tuple[bool, str]:
    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        delete_sql = """
            DELETE FROM Reservacion
            WHERE idReservacion = %s;
        """
        cursor.execute(delete_sql, (id_reservacion,))

        if cursor.rowcount == 0:
            conn.rollback()
            return False, "No se encontró la reservación a cancelar."

        conn.commit()
        return True, "Reservación cancelada correctamente"

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return False, f"Error al cancelar la reservación: {err}"

    finally:
        if cursor:
            cursor.close()


    