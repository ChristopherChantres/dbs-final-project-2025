import mysql.connector
from datetime import time
from typing import List, Optional
from config.db import get_connection


def crear_horario(
    id_salon: str,
    hora_inicio: time,
    duracion_min: int,
    dias_semana: List[str],
    curso_clave: str,
    curso_seccion: int,
    id_periodo: str,
) -> tuple[bool, str]:
   

    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        hora_str = hora_inicio.strftime("%H:%M:%S")

        if not dias_semana:
             return False, "Debe seleccionar al menos un día."

        # Validar que el salon exista
        cursor.execute("SELECT id_salon FROM salon WHERE id_salon = %s", (id_salon,))
        if not cursor.fetchone():
            return False, "El salón especificado no existe."

        for dia in dias_semana:
            conflicto_sql = """
                SELECT id_horario
                FROM horario
                WHERE id_salon    = %s
                  AND dia_semana = %s
                  AND id_periodo = %s
                  -- traslape de intervalos de tiempo
                  AND hora_inicio < ADDTIME(%s, SEC_TO_TIME(%s * 60))
                  AND %s < ADDTIME(hora_inicio, SEC_TO_TIME(duracion_minutos * 60))
                FOR UPDATE;
            """
            conflicto_params = (id_salon, dia, id_periodo, hora_str, duracion_min, hora_str)
            cursor.execute(conflicto_sql, conflicto_params)

            if cursor.fetchone():
                conn.rollback()
                return False, f"Ya existe un horario que se traslapa en ese salón para el día {dia}."

            insert_sql = """
                INSERT INTO horario (
                    id_salon,
                    hora_inicio,
                    duracion_minutos,
                    dia_semana,
                    clave_materia,
                    seccion_curso,
                    id_periodo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            insert_params = (
                id_salon,
                hora_str,
                duracion_min,
                dia,
                curso_clave,
                curso_seccion,
                id_periodo,
            )
            cursor.execute(insert_sql, insert_params)

        conn.commit()
        return True, "Horarios creados correctamente"

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
    dia_semana: str,
) -> tuple[bool, str]:
   
    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        hora_str = hora_inicio.strftime("%H:%M:%S")

        # Obtener el id_periodo del horario actual para validar conflicto en el mismo periodo
        cursor.execute("SELECT id_periodo FROM horario WHERE id_horario = %s", (id_horario,))
        row = cursor.fetchone()
        if not row:
             conn.rollback()
             return False, "No se encontró el horario a actualizar."
        
        current_periodo = row[0]

        # 1) Checar traslape, excluyendo el propio idHorario
        
        conflicto_sql = """
            SELECT id_horario
            FROM horario
            WHERE id_salon    = %s
              AND dia_semana = %s
              AND id_periodo = %s
              AND id_horario <> %s
              AND hora_inicio < ADDTIME(%s, SEC_TO_TIME(%s * 60))
              AND %s < ADDTIME(hora_inicio, SEC_TO_TIME(duracion_minutos * 60))
            FOR UPDATE;
        """
        conflicto_params = (id_salon, dia_semana, current_periodo, id_horario,
                            hora_str, duracion_min, hora_str)
        cursor.execute(conflicto_sql, conflicto_params)

        if cursor.fetchone():
            conn.rollback()
            return False, "El nuevo horario se traslapa con otro ya existente en ese salón."

       
        update_sql = """
            UPDATE horario
            SET id_salon    = %s,
                hora_inicio       = %s,
                duracion_minutos   = %s,
                dia_semana = %s
            WHERE id_horario = %s;
        """
        update_params = (id_salon, hora_str, duracion_min, dia_semana, id_horario)
        cursor.execute(update_sql, update_params)

        if cursor.rowcount == 0:
            conn.rollback()
            return False, "No se pudo actualizar el horario."

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
            DELETE FROM horario
            WHERE id_horario = %s;
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
