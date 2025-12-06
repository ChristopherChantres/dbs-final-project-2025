from typing import Optional

def login_simulado(id_usuario: str) -> Optional[dict]:
    """
    Busca al usuario en la BD.
    Retorna un diccionario: {'id': '...', 'nombre': '...', 'rol': 'Administrador'}
    Retorna None si no existe.
    """
    pass

def tiene_permiso(rol_usuario: str, accion: str) -> bool:
    """
    Lógica simple de permisos:
    - Si rol == 'Administrador' -> True siempre.
    - Si rol == 'Estudiante' y accion == 'borrar' -> False.
    """
    pass