import streamlit as st
from .services import autenticar_usuario, registrar_nuevo_usuario
import time
from utils.helpers import LOGO

def renderizar_login():
    """
    Renderiza el Login.
    Si el usuario ya está logueado, retorna el diccionario del usuario.
    Si no, muestra el form, detiene la ejecución y retorna None.
    """
    
    if 'usuario_activo' in st.session_state:
        return st.session_state['usuario_activo']

    st.header("🔐 Scheduleee For Dummies")
    st.image(LOGO, width=100)
    
    tab_login, tab_registro = st.tabs(["Login", "Registro"])

    # --- TAB 1: LOGIN ---
    with tab_login:
        with st.form("login_form"):
            id_input = st.text_input("Ingresa tu ID / Matrícula", max_chars=6, help="Debe ser un número de 6 dígitos")
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
                    usuario = autenticar_usuario(id_input)
                    if usuario:
                        st.session_state['usuario_activo'] = usuario
                        st.success(f"Bienvenido {usuario['nombre']} ({usuario['rol']})")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("ID no encontrado. Por favor regístrate.")

    # --- TAB 2: REGISTRO ---
    with tab_registro:
        with st.form("register_form"):
            st.write("Crea tu cuenta nueva")
            new_id = st.text_input("Crea un ID / Matrícula", max_chars=6, help="Debe ser un número de 6 dígitos")
            new_nombre = st.text_input("Nombre Completo")
            # El selectbox asegura que no inventen roles raros
            new_rol = st.selectbox("Rol", ["Estudiante", "Profesor", "Administrador"])
            
            submitted_reg = st.form_submit_button("Crear Cuenta")
            
            if submitted_reg:
                if not new_id.isdigit():
                    st.error("El ID debe contener solo números.")
                elif len(new_id) != 6:
                    st.error("El ID debe tener exactamente 6 dígitos.")
                elif new_id and new_nombre:
                    exito, msg = registrar_nuevo_usuario(new_id, new_nombre, new_rol)
                    if exito:
                        # Después de registrar, autenticar al usuario para iniciar sesión automáticamente
                        usuario = autenticar_usuario(new_id)
                        if usuario:
                            st.session_state['usuario_activo'] = usuario
                            st.success(f"¡Cuenta creada! Bienvenido {usuario['nombre']} ({usuario['rol']})")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Cuenta creada, pero error al iniciar sesión. Por favor, inicia sesión manualmente.")
                    else:
                        st.error(msg)
                else:
                    st.warning("Todos los campos son obligatorios")

    # DETENER LA EJECUCIÓN DEL RESTO DE LA APP
    # Esto es clave: si llegamos aquí, es que no se ha logueado.
    # No queremos que se renderice el menú ni nada más.
    st.stop()

def renderizar_sidebar(usuario: dict):
    """
    Renderiza la barra lateral con información del usuario y botón de logout.
    
    Args:
        usuario: Diccionario con los datos del usuario activo (nombre, rol, etc.)
    """
    with st.sidebar:
        st.image(LOGO, width=100)
        st.markdown(
            f"""
            ### 👤 {usuario['nombre']}
            **Rol:** `{usuario['rol']}`
            """,
            unsafe_allow_html=True
        )
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
            # Clear the session state
            del st.session_state['usuario_activo']
            # Rerun to show login screen
            st.rerun()