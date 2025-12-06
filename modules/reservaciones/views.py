# Form: st.form("new_reservation")
import streamlit as st

def reservation_form():
    with st.form("new_reservation"):
        st.header("Nueva Reservación")
        # Add form fields
        submitted = st.form_submit_button("Reservar")

