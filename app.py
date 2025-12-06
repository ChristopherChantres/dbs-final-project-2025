import streamlit as st
from modules.auth.ui import renderizar_login, renderizar_sidebar
from modules.salones.views import view_salones
from modules.reservaciones.views import view_reservaciones
from modules.horarios.views import view_horarios
from modules.cursos.views import view_cursos
from utils.ui import aplicar_tema_personalizado
from utils.helpers import LOGO

def main():
    st.set_page_config(
        page_title="Scheduleee For Dummies",
        page_icon=LOGO,
        layout="wide"
    )
    aplicar_tema_personalizado()
    usuario = renderizar_login()
    
    st.title("Scheduleee For Dummies")
    st.write("Bienvenido al sistema de gestión de salones y espacios.")
    
    if usuario:
        renderizar_sidebar(usuario)
        st.divider()
        view_salones()
        view_cursos()
        view_horarios()
        view_reservaciones()

if __name__ == "__main__":
    main()
