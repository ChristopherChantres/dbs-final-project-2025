from config.db import get_connection
import mysql.connector

def crear_reservacion(id_usuario, id_salon, fecha):
    """
    Crea una reservación en la base de datos.
    """

def cancelar_reservacion(id_reservacion: int) -> tuple[bool, str]:
    """
    Elimina una reservación existente.
    """

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reservacion WHERE id_reservacion=%s", (id_reservacion))
        conn.commit()
        return (True, "Reservación cancelada correctamente")
    except Exception:
        conn.rollback()
        return (False, "Error al cancelar la reservación")