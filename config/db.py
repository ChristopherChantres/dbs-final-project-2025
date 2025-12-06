import mysql.connector
from mysql.connector import Error
import os
import streamlit as st

# Attempt to load .env if not in a container environment where variables are already set
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
        """Establishes a connection to the database."""
        try:
            self._connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASS", ""),
                database=os.getenv("DB_NAME", "scheduleee"),
                port=int(os.getenv("DB_PORT", 3306))
            )
            if self._connection.is_connected():
                # print("Connection to MySQL DB successful") # Avoid printing in production
                pass
        except Error as e:
            st.error(f"Error while connecting to MySQL: {e}")
            self._connection = None

    def get_connection(self):
        """Returns the active database connection. Reconnects if necessary."""
        if self._connection is None or not self._connection.is_connected():
            self._create_connection()
        return self._connection

    def close_connection(self):
        """Closes the database connection."""
        if self._connection is not None and self._connection.is_connected():
            self._connection.close()
            # print("MySQL connection is closed")
