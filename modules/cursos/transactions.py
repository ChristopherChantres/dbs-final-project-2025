import mysql.connector
from config.db import get_connection
from utils.period_helpers import obtener_fechas_periodo

def crear_nuevo_curso(clave: str, seccion: int, periodo_str: str, profesor: str) -> tuple[bool, str]:
    """
    Crea un curso. Si el periodo no existe (ej. OTOÑO-2025), intenta crearlo primero.
    periodo_str debe ser 'TIPO-ANIO' (ej. 'OTOÑO-2024').
    """
    try:
        conn = get_connection()
        conn.autocommit = False # Transaction mode
        cursor = conn.cursor()
        
        # 1. Verificar si el periodo existe
        check_periodo_sql = "SELECT id_periodo FROM periodo WHERE id_periodo = %s"
        cursor.execute(check_periodo_sql, (periodo_str,))
        
        if not cursor.fetchone():
            # Crear el periodo si no existe
            try:
                parts = periodo_str.split('-')
                if len(parts) != 2:
                     raise ValueError("Formato de periodo inválido")
                
                tipo = parts[0]
                anio = int(parts[1])
                
                f_inicio, f_fin = obtener_fechas_periodo(tipo, anio)
                
                insert_periodo_sql = """
                    INSERT INTO periodo (id_periodo, fecha_inicio, fecha_fin)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_periodo_sql, (periodo_str, f_inicio, f_fin))
            except Exception as e:
                conn.rollback()
                return False, f"Error al crear el nuevo periodo {periodo_str}: {e}"

        # 2. Crear el curso
        sql = """
            INSERT INTO curso (clave_materia, seccion, id_periodo, profesor)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (clave, seccion, periodo_str, profesor))
        
        conn.commit()
        return True, "Curso creado exitosamente"
        
    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return False, f"Error SQL: {err}"
        
    finally:
        # Cerramos el cursor para liberar memoria
        # Pero mantenemos la conexión (conn) abierta.
        if cursor:
            cursor.close()
