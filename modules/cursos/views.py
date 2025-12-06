import streamlit as st
import time
import datetime
from modules.cursos.queries import obtener_cursos_existentes, obtener_catalogos_para_curso
from modules.cursos.transactions import crear_nuevo_curso
from modules.models import Rol, TipoPeriodo

def view_cursos():
    # Permission check
    usuario = st.session_state.get("usuario_activo", {})
    if usuario.get("rol") != Rol.ADMINISTRADOR.value:
        return

    st.header("📚 Gestión de Cursos (Oferta Académica)")
    st.info("Primero define qué cursos se ofertan este periodo. Después podrás asignarles horarios.")

    # --- SECTION 1: LIST COURSES ---
    df_cursos = obtener_cursos_existentes()
    if not df_cursos.empty:
        st.dataframe(df_cursos, use_container_width=True, hide_index=True)
    else:
        st.warning("No hay cursos registrados.")

    st.divider()

    # --- SECTION 2: CREATE COURSE ---
    st.subheader("➕ Abrir nuevo curso")
    
    df_materias, _ = obtener_catalogos_para_curso()
    
    if df_materias.empty:
        st.error("No hay materias registradas. Primero crea materias en la BD.")
        return

    with st.form("form_crear_curso"):
        c1, c2 = st.columns(2)
        with c1:
            # Materia Selection
            lista_materias = df_materias["clave"] + " - " + df_materias["titulo"]
            materia_sel = st.selectbox("Materia", options=lista_materias)
            
            seccion = st.number_input("Sección", min_value=1, value=1, step=1)
            
            profesor = st.text_input("Profesor asignado", placeholder="Ej. Dr. Zechinelli")

        with c2:
            st.markdown("#### Definir Periodo")
            # Dynamic Period Construction
            tipo_periodo = st.selectbox("Tipo Periodo", [p.value for p in TipoPeriodo])
            current_year = datetime.date.today().year
            anio_periodo = st.number_input("Año", min_value=current_year, value=current_year, step=1)
            
            # Preview
            periodo_generado = f"{tipo_periodo}-{anio_periodo}"
            st.caption(f"📌 Periodo a asignar: **{periodo_generado}**")
            
        submitted = st.form_submit_button("Guardar Curso", type="primary")
        
        if submitted:
            if not materia_sel:
                st.error("Debes seleccionar una materia.")
            elif not profesor:
                st.warning("Debes asignar un profesor.")
            else:
                # Extract just the code 'LIS-2082'
                clave_materia = materia_sel.split(" - ")[0]
                
                # Call transaction with constructed period string
                ok, msg = crear_nuevo_curso(clave_materia, seccion, periodo_generado, profesor)
                if ok:
                    st.success(msg)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)
