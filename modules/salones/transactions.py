import mysql.connector
from config.db import get_connection
from modules.models import TipoSalon

def crear_salon(id_salon: str, capacidad: int, tipo: TipoSalon) -> tuple[bool, str]:
    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()
        query = "INSERT INTO salon (id_salon, capacidad, tipo) VALUES (%s, %s, %s)"
        cursor.execute(query, (id_salon, capacidad, tipo))
        conn.commit()
        return True, "Salon creado correctamente"
    except mysql.connector.Error as err:
        conn.rollback()
        print(" Error SQL:", err)
        return False, f"Error al crear el salon: {err}"
    finally:
        # Cerramos el cursor para liberar memoria
        # Pero mantenemos la conexión (conn) abierta.
        if cursor:
            cursor.close()

def borrar_salon(id_salon: str) -> tuple[bool, str]:
    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM horario WHERE id_salon = %s", (id_salon,))
        cursor.execute("DELETE FROM reservacion WHERE id_salon = %s", (id_salon,))
        query = "DELETE FROM salon WHERE id_salon = %s"
        cursor.execute(query, (id_salon,))
        
        conn.commit()
        return True, "Salon borrado correctamente (incluyendo horarios y reservaciones)"
        
    except mysql.connector.Error as err:
        conn.rollback()
        print(" Error SQL:", err)
        # Check specifically for FK errors if cascading fails or isn't used
        if err.errno == 1451:
            return False, "No se puede borrar: el salón tiene registros asociados."
        return False, f"Error al borrar el salon: {err}"
    finally:
        if cursor:
            cursor.close()