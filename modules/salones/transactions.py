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