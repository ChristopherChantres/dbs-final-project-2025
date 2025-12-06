import mysql.connector
import pandas as pd
from config.db import get_connection

def obtener_cursos_existentes() -> pd.DataFrame:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        # Join to show readable names
        query = """
            SELECT 
                c.clave_materia,
                m.titulo as materia_titulo,
                c.seccion,
                c.id_periodo,
                c.profesor
            FROM curso c
            JOIN materia m ON c.clave_materia = m.clave
            ORDER BY c.id_periodo DESC, m.titulo ASC, c.seccion ASC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return pd.DataFrame(rows)
    except mysql.connector.Error as e:
        print(f"Error fetching courses: {e}")
        return pd.DataFrame()
    finally:
        # Cerramos el cursor para liberar memoria
        # Pero mantenemos la conexión (conn) abierta.
        if cursor:
            cursor.close()

def obtener_catalogos_para_curso() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (df_materias, df_periodos)"""
    try:
        # Obtener materias
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT clave, titulo FROM materia ORDER BY titulo")
        materias = pd.DataFrame(cursor.fetchall())
        
        # Obtener periodos
        cursor.execute("SELECT id_periodo FROM periodo ORDER BY fecha_inicio DESC")
        periodos = pd.DataFrame(cursor.fetchall())
        
        return materias, periodos
    except mysql.connector.Error as err:
        print(" Error SQL:", err)
        return pd.DataFrame(), pd.DataFrame()
    finally:
        # Cerramos el cursor para liberar memoria
        # Pero mantenemos la conexión (conn) abierta.
        if cursor:
            cursor.close()
