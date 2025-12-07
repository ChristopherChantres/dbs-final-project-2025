from config.db import get_connection
import mysql.connector
from datetime import date, time, timedelta, datetime

# Mapeo de días para coincidir con la base de datos (ENUM en español)
DIAS_SEMANA = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']

def _verificar_conflicto(cursor, id_salon: str, fecha: date, hora_inicio: time, duracion_min: int) -> bool:
    """
    Verifica si existe conflicto con Horarios (clases) o Reservaciones existentes.
    Retorna True si hay conflicto, False si está libre.
    """
    hora_str = hora_inicio.strftime("%H:%M:%S")
    dia_nombre = DIAS_SEMANA[fecha.weekday()]

    # 1. Verificar conflicto con Horarios (Clases recurrentes)
    # Debemos verificar si la fecha cae dentro del periodo de la clase y coincide el día/hora.
    sql_horario = """
        SELECT h.id_horario
        FROM horario h
        JOIN periodo p ON h.id_periodo = p.id_periodo
        WHERE h.id_salon = %s
          AND h.dia_semana = %s
          AND %s BETWEEN p.fecha_inicio AND p.fecha_fin
          -- Chequeo de traslape de horas
          AND h.hora_inicio < ADDTIME(%s, SEC_TO_TIME(%s * 60))
          AND %s < ADDTIME(h.hora_inicio, SEC_TO_TIME(h.duracion_minutos * 60))
        LIMIT 1;
    """
    # Params: id_salon, dia_semana, fecha, hora_inicio_str, duracion_min, hora_inicio_str
    cursor.execute(sql_horario, (id_salon, dia_nombre, fecha, hora_str, duracion_min, hora_str))
    if cursor.fetchone():
        return True

    # 2. Verificar conflicto con otras Reservaciones (Eventos únicos)
    sql_reservacion = """
        SELECT id_reservacion
        FROM reservacion
        WHERE id_salon = %s
          AND fecha = %s
          -- Chequeo de traslape
          AND hora_inicio < ADDTIME(%s, SEC_TO_TIME(%s * 60))
          AND %s < ADDTIME(hora_inicio, SEC_TO_TIME(duracion_minutos * 60))
        LIMIT 1;
    """
    # Params: id_salon, fecha, hora_inicio_str, duracion_min, hora_inicio_str
    cursor.execute(sql_reservacion, (id_salon, fecha, hora_str, duracion_min, hora_str))
    if cursor.fetchone():
        return True

    return False

def crear_reservacion(
    id_usuario: str,
    id_salon: str,
    fecha: date,
    hora_inicio: time,
    duracion_min: int,
    id_periodo: str,
    motivo: str
) -> tuple[bool, str]:
    """
    a) Registrar una reservación individual para una fecha y hora exacta.
       Verifica conflictos con reservaciones y horarios.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        # Verificar conflictos
        if _verificar_conflicto(cursor, id_salon, fecha, hora_inicio, duracion_min):
            conn.rollback()
            return False, "El salón no está disponible en el horario seleccionado (conflicto con clase o reservación)."

        # Insertar
        hora_str = hora_inicio.strftime("%H:%M:%S")
        insert_sql = """
            INSERT INTO reservacion (id_usuario, id_salon, id_periodo, fecha, hora_inicio, duracion_minutos, motivo)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_sql, (id_usuario, id_salon, id_periodo, fecha, hora_str, duracion_min, motivo))

        conn.commit()
        return True, "Reservación creada correctamente"

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return False, f"Error al crear la reservación: {err}"

    finally:
        if cursor:
            cursor.close()

def crear_reservacion_periodica(
    id_usuario: str,
    id_salon: str,
    dia_semana: str, # 'Lunes', 'Martes', etc.
    hora_inicio: time,
    duracion_min: int,
    id_periodo: str,
    motivo: str
) -> tuple[bool, str]:
    """
    b) Reservar un salón para un día de la semana por todo un periodo.
       Ejemplo: "Todos los martes del periodo Primavera 2024 a las 14:00".
       Si una falla, todas se cancelan (atomicidad).
    """
    conn = None
    cursor = None

    # Validar día de semana input
    if dia_semana not in DIAS_SEMANA:
        return False, f"Día inválido. Debe ser uno de: {', '.join(DIAS_SEMANA)}"

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        # 1. Obtener fechas del periodo
        cursor.execute("SELECT fecha_inicio, fecha_fin FROM periodo WHERE id_periodo = %s", (id_periodo,))
        periodo_row = cursor.fetchone()
        
        if not periodo_row:
            return False, "Periodo no encontrado."
        
        fecha_inicio_p, fecha_fin_p = periodo_row # Son objetos date

        # 2. Iterar por todas las fechas del periodo
        curr_date = fecha_inicio_p
        reservas_creadas = 0
        
        target_weekday = DIAS_SEMANA.index(dia_semana) # 0 for Lunes, etc.
        hora_str = hora_inicio.strftime("%H:%M:%S")

        while curr_date <= fecha_fin_p:
            if curr_date.weekday() == target_weekday:
                # Verificar conflicto para esta fecha específica
                if _verificar_conflicto(cursor, id_salon, curr_date, hora_inicio, duracion_min):
                    conn.rollback()
                    return False, f"Conflicto detectado en la fecha {curr_date}. No se realizó ninguna reservación."
                
                # Insertar
                insert_sql = """
                    INSERT INTO reservacion (id_usuario, id_salon, id_periodo, fecha, hora_inicio, duracion_minutos, motivo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_sql, (id_usuario, id_salon, id_periodo, curr_date, hora_str, duracion_min, motivo))
                reservas_creadas += 1
            
            curr_date += timedelta(days=1)

        if reservas_creadas == 0:
            conn.rollback()
            return False, "No se encontraron días correspondientes en el periodo seleccionado."

        conn.commit()
        return True, f"Se crearon {reservas_creadas} reservaciones periódicas correctamente."

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return False, f"Error al crear reservaciones periódicas: {err}"

    finally:
        if cursor:
            cursor.close()

def cancelar_reservacion(id_reservacion: int) -> tuple[bool, str]:
    """
    c.1) Cancelar una reservación específica.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        delete_sql = "DELETE FROM reservacion WHERE id_reservacion = %s;"
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

def cancelar_reservaciones_por_intervalo(
    id_usuario: str,
    fecha_inicio: date,
    fecha_fin: date
) -> tuple[bool, str]:
    """
    c.2) Cancelar reservaciones en un intervalo de fechas para un usuario.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        delete_sql = """
            DELETE FROM reservacion
            WHERE id_usuario = %s
              AND fecha BETWEEN %s AND %s;
        """
        cursor.execute(delete_sql, (id_usuario, fecha_inicio, fecha_fin))
        deleted_count = cursor.rowcount

        if deleted_count == 0:
            conn.rollback() # O commit, pero avisando que no hubo nada
            return False, "No se encontraron reservaciones en ese rango para cancelar."

        conn.commit()
        return True, f"Se cancelaron {deleted_count} reservaciones correctamente."

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return False, f"Error al cancelar reservaciones: {err}"

    finally:
        if cursor:
            cursor.close()
