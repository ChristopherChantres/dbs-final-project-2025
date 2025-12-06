import mysql.connector
import os
import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# El decorador hace la magia del Singleton por ti
@st.cache_resource
def _get_connection_object():
    """
    Crea la conexión UNA sola vez y la mantiene en caché de RAM.
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", "scheduleee"),
        port=int(os.getenv("DB_PORT", 3306))
    )

def get_connection():
    """
    Recupera la conexión activa. Si se cayó, intenta reconectar.
    """
    try:
        conn = _get_connection_object()
        # Verificar si sigue viva (ping)
        if not conn.is_connected():
            st.cache_resource.clear() # Borramos caché
            conn = _get_connection_object() # Reconectamos
        return conn
    except mysql.connector.Error as e:
        st.error(f"Error de conexión: {e}")
        return None