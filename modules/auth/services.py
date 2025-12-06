import streamlit as st
from config.db import get_connection
from typing import Optional

def autenticar_usuario(id_usuario: str) -> Optional[dict]:
    """
    Busca al usuario por ID. 
    Retorna un diccionario con sus datos si existe, o None si no.
    """
    conn = get_connection()
    if not conn:
        return None
    
    cursor = None
    try:
        # dictionary=True es vital para acceder como usuario['nombre']
        cursor = conn.cursor(dictionary=True) 
        
        # Limpiamos cualquier resultado pendiente de lecturas anteriores (buena práctica en Singleton)
        conn.consume_results() 
        
        query = "SELECT id_usuario, nombre, rol FROM usuario WHERE id_usuario = %s"
        cursor.execute(query, (id_usuario,))
        usuario = cursor.fetchone()
        
        return usuario 
    except Exception as e:
        print(f"Error al autenticar usuario: {e}")
        return None
        
    finally:
        # Cerramos el cursor para liberar memoria, 
        # Pero mantenemos la conexión (conn) abierta.
        if cursor:
            cursor.close()

def registrar_nuevo_usuario(id_usuario: str, nombre: str, rol: str) -> tuple[bool, str]:
    """
    Crea un nuevo usuario en la BD.
    """
    conn = get_connection()
    if not conn:
        return False, "Error de conexión con la base de datos"
        
    cursor = None
    try:
        cursor = conn.cursor()
        
        query = "INSERT INTO usuario (id_usuario, nombre, rol) VALUES (%s, %s, %s)"
        cursor.execute(query, (id_usuario, nombre, rol))
        
        # Confirmamos el cambio en la BD
        conn.commit()
        return True, "Usuario registrado exitosamente"
        
    except Exception as e:
        if conn:
            conn.rollback()
            
        # Detectar error de duplicado (Código 1062 en MySQL)
        if "Duplicate entry" in str(e) or "1062" in str(e):
            return False, "Ese ID de usuario ya existe."
            
        return False, f"Error al registrar: {e}"
        
    finally:
        # Cerramos el cursor para liberar memoria, 
        # Pero mantenemos la conexión (conn) abierta.
        if cursor:
            cursor.close()