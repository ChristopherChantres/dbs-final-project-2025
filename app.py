import streamlit as st
from modules.auth.ui import renderizar_login, renderizar_sidebar
from utils.ui import aplicar_tema_personalizado

def main():
    aplicar_tema_personalizado()
    usuario = renderizar_login()
    
    st.title("Scheduleee for Dummies")
    st.write("Welcome to the classroom management system.")
    
    if usuario:
        renderizar_sidebar(usuario)

if __name__ == "__main__":
    main()

