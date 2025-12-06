import streamlit as st
from modules.auth.ui import renderizar_login, renderizar_sidebar
from modules.salones.views import view_salones
from utils.ui import aplicar_tema_personalizado

def main():
    aplicar_tema_personalizado()
    usuario = renderizar_login()
    
    st.title("Scheduleee For Dummies")
    st.write("Bienvenido al sistema de gestión de salones y espacios.")
    
    if usuario:
        st.balloons()
        renderizar_sidebar(usuario)
        
        st.divider()
        view_salones()

if __name__ == "__main__":
    main()
