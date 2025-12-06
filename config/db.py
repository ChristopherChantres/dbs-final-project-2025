import mysql.connector
from mysql.connector import Error
import os
import streamlit as st

# Intentar cargar .env si no estamos en un entorno de contenedor donde ya están establecidas las variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connection = None
        return cls._instance

    def _create_connection(self):
        """Establece una conexión con la base de datos."""
        try:
            self._connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASS", ""),
                database=os.getenv("DB_NAME", "scheduleee"),
                port=int(os.getenv("DB_PORT", 3306))
            )
            if self._connection.is_connected():
                # print("Conexión a MySQL exitosa") # Evitar imprimir en producción
                pass
        except Error as e:
            st.error(f"Error al conectar a MySQL: {e}")
            self._connection = None

    def get_connection(self):
        """Retorna la conexión activa a la base de datos. Reconecta si es necesario."""
        if self._connection is None or not self._connection.is_connected():
            self._create_connection()
        return self._connection

    def close_connection(self):
        """Cierra la conexión con la base de datos."""
        if self._connection is not None and self._connection.is_connected():
            self._connection.close()
            # print("La conexión a MySQL fue cerrada")

# Importación sencilla: función para obtener la conexión singleton a la base de datos
def get_connection():
    """
    Retorna una conexión singleton a MySQL, reconectando si es necesario.
    Uso: from config.db import get_connection
    """
    db_singleton = DatabaseConnection()
    return db_singleton.get_connection()
