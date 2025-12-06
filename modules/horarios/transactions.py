import mysql.connector
from datetime import time
from config.db import get_connection


def crear_horario(
    id_salon: str,
    hora_inicio: time,
    duracion_min: int,
    dias_semana: str,
    curso_clave: str,
    curso_seccion: int,
) -> tuple[bool, str]:
   

    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        hora_str = hora_inicio.strftime("%H:%M:%S")

       
        conflicto_sql = """
            SELECT idHorario
            FROM Horario
            WHERE idSalon    = %s
              AND diasSemana = %s
              -- traslape de intervalos de tiempo
              AND hora < ADDTIME(%s, SEC_TO_TIME(%s * 60))
              AND %s < ADDTIME(hora, SEC_TO_TIME(duracion * 60))
            FOR UPDATE;
        """
        conflicto_params = (id_salon, dias_semana, hora_str, duracion_min, hora_str)
        cursor.execute(conflicto_sql, conflicto_params)

        if cursor.fetchone():
            conn.rollback()
            return False, "Ya existe un horario que se traslapa en ese salón y días."

        
        insert_sql = """
            INSERT INTO Horario (
                idSalon,
                hora,
                duracion,
                diasSemana,
                curso_clave,
                curso_seccion
            )
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        insert_params = (
            id_salon,
            hora_str,
            duracion_min,
            dias_semana,
            curso_clave,
            curso_seccion,
        )
        cursor.execute(insert_sql, insert_params)

        conn.commit()
        return True, "Horario creado correctamente"

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return False, f"Error al crear el horario: {err}"

    finally:
        if cursor:
            cursor.close()
def actualizar_horario(
    id_horario: int,
    id_salon: str,
    hora_inicio: time,
    duracion_min: int,
    dias_semana: str,
) -> tuple[bool, str]:
   
    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        hora_str = hora_inicio.strftime("%H:%M:%S")

        # 1) Checar traslape, excluyendo el propio idHorario
        conflicto_sql = """
            SELECT idHorario
            FROM Horario
            WHERE idSalon    = %s
              AND diasSemana = %s
              AND idHorario <> %s
              AND hora < ADDTIME(%s, SEC_TO_TIME(%s * 60))
              AND %s < ADDTIME(hora, SEC_TO_TIME(duracion * 60))
            FOR UPDATE;
        """
        conflicto_params = (id_salon, dias_semana, id_horario,
                            hora_str, duracion_min, hora_str)
        cursor.execute(conflicto_sql, conflicto_params)

        if cursor.fetchone():
            conn.rollback()
            return False, "El nuevo horario se traslapa con otro ya existente en ese salón."

       
        update_sql = """
            UPDATE Horario
            SET idSalon    = %s,
                hora       = %s,
                duracion   = %s,
                diasSemana = %s
            WHERE idHorario = %s;
        """
        update_params = (id_salon, hora_str, duracion_min, dias_semana, id_horario)
        cursor.execute(update_sql, update_params)

        if cursor.rowcount == 0:
            conn.rollback()
            return False, "No se encontró el horario a actualizar."

        conn.commit()
        return True, "Horario actualizado correctamente"

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return False, f"Error al actualizar el horario: {err}"

    finally:
        if cursor:
            cursor.close()

def eliminar_horario(id_horario: int) -> tuple[bool, str]:
    

    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        delete_sql = """
            DELETE FROM Horario
            WHERE idHorario = %s;
        """
        cursor.execute(delete_sql, (id_horario,))

        if cursor.rowcount == 0:
            conn.rollback()
            return False, "No se encontró el horario a eliminar."

        conn.commit()
        return True, "Horario eliminado correctamente"

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return False, f"Error al eliminar el horario: {err}"

    finally:
        if cursor:
            cursor.close()
