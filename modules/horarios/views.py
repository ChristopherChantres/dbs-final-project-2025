import streamlit as st
from datetime import time as dt_time
from modules.models import Rol, DiaSemana
import time

from .queries import (
    obtener_horario_completo,
    filtrar_horario,
)
from modules.salones.queries import obtener_catalogo_salones
from .transactions import (
    crear_horario,
    actualizar_horario,
    eliminar_horario,
)
from modules.cursos.queries import obtener_cursos_existentes

def view_horarios():
    usuario = st.session_state.get("usuario_activo", {})
    rol_usuario = usuario.get("rol")

    es_admin = rol_usuario == Rol.ADMINISTRADOR.value
    es_profesor = rol_usuario == Rol.PROFESOR.value
    
    titulos_tabs = ["📋 Horario completo", "🔍 Filtro por periodo/día"]
    if es_profesor:
        titulos_tabs.append("👨‍🏫 Vista profesor (filtro)")
    if es_admin:
        titulos_tabs.append("🛠 Administrar horarios")

    tabs = st.tabs(titulos_tabs)

    tab_completo = tabs[0]
    tab_filtro = tabs[1]
    tab_profesor = tabs[2] if es_profesor else None
    tab_admin = tabs[-1] if es_admin else None

    
   
    with tab_completo:
        st.subheader("Listado general de horarios")

        df = obtener_horario_completo()

        if df.empty:
            st.info("No se encontraron horarios registrados.")
        else:
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de horarios", len(df))

            if "id_salon" in df.columns:
                col2.metric("Salones distintos", df["id_salon"].nunique())

            if "materia" in df.columns:
                col3.metric("Materias distintas", df["materia"].nunique())

           
            c1, c2, c3 = st.columns(3)
            with c1:
                salones = ["Todos"] + sorted(df["id_salon"].unique().tolist())
                filtro_salon = st.selectbox("Filtrar por salón", salones)
            with c2:
                materias = ["Todas"] + sorted(df["materia"].unique().tolist())
                filtro_materia = st.selectbox("Filtrar por materia", materias)
            with c3:
                profesores = ["Todos"] + sorted(df["profesor"].dropna().unique().tolist())
                filtro_profesor = st.selectbox("Filtrar por profesor", profesores)

            df_filtrado = df.copy()
            if filtro_salon != "Todos":
                df_filtrado = df_filtrado[df_filtrado["id_salon"] == filtro_salon]
            if filtro_materia != "Todas":
                df_filtrado = df_filtrado[df_filtrado["materia"] == filtro_materia]
            if filtro_profesor != "Todos":
                df_filtrado = df_filtrado[df_filtrado["profesor"] == filtro_profesor]

            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    
    with tab_filtro:
        st.subheader("Filtrar horario por periodo y día")
       
        df = obtener_horario_completo()

        if df.empty:
            st.info("No hay datos de horarios para filtrar.")
        else:
            periodos_unicos = df["id_periodo"].unique().tolist()
            c1, c2 = st.columns(2)
            with c1:
                id_periodo = st.selectbox("Periodo", periodos_unicos)
            with c2:
                dia_semana = st.selectbox(
                    "Día de la semana (opcional)",
                    ["Todos", "Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
                )

            dia_param = None if dia_semana == "Todos" else dia_semana
            df_filtro = filtrar_horario(id_periodo=id_periodo, dia_semana=dia_param)

            if df_filtro.empty:
                st.warning("No se encontraron horarios para ese filtro.")
            else:
                st.dataframe(df_filtro, use_container_width=True, hide_index=True)

   
    if es_profesor and tab_profesor:
        with tab_profesor:
            st.subheader("👨‍🏫 Vista para profesor")

            df = obtener_horario_completo()

            if df.empty:
                st.info("No se encontraron horarios.")
            else:
                
                nombre_prof = st.text_input(
                    "Filtrar por nombre de profesor (coincidencia en columna 'profesor')",
                    value=""
                )

                df_filtrado = df.copy()
                if nombre_prof.strip():
                    df_filtrado = df_filtrado[
                        df_filtrado["profesor"].str.contains(nombre_prof.strip(), case=False, na=False)
                    ]

                st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    
    if es_admin and tab_admin:
        with tab_admin:
            st.subheader("🛠 Administración de horarios")

            # --------- SUBSECCION: EDITAR / ELIMINAR -------------
            st.markdown("### 🧾 Editar / eliminar horarios existentes")

            df = obtener_horario_completo()

            if df.empty:
                st.info("No hay horarios cargados.")
            else:
                # Agregar columna de selección para eliminar
                if "Eliminar" not in df.columns:
                    df["Eliminar"] = False

                # Reordenar para que 'Eliminar' salga primero
                columnas = ["Eliminar"] + [c for c in df.columns if c != "Eliminar"]
                df = df[columnas]

                edited_df = st.data_editor(
                    df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "Eliminar": st.column_config.CheckboxColumn(
                            "Eliminar",
                            help="Selecciona para borrar este horario",
                            default=False
                        ),
                        "id_horario": st.column_config.TextColumn("ID Horario", disabled=True),
                        "hora_inicio": st.column_config.TextColumn("Hora", disabled=True),
                        "duracion_minutos": st.column_config.NumberColumn("Duración", disabled=True),
                        "dia_semana": st.column_config.TextColumn("Días", disabled=True),
                        "id_salon": st.column_config.TextColumn("Salón", disabled=True),
                        "materia": st.column_config.TextColumn("Materia", disabled=True),
                        "profesor": st.column_config.TextColumn("Profesor", disabled=True),
                    },
                    key="editor_horarios"
                )

                # Procesar eliminaciones
                to_delete = edited_df[edited_df["Eliminar"] == True]
                if not to_delete.empty:
                    st.warning(f"Has marcado {len(to_delete)} horarios para eliminar.")
                    if st.button("🗑️ Confirmar eliminación", type="primary"):
                        for _, row in to_delete.iterrows():
                            ok, msg = eliminar_horario(int(row["id_horario"]))
                            if ok:
                                st.toast(f"Horario {row['id_horario']} eliminado.")
                            else:
                                st.error(f"Error al eliminar {row['id_horario']}: {msg}")
                        time.sleep(1)
                        st.rerun()

            st.markdown("---")

            # --------- SUBSECCION: CREAR NUEVO HORARIO -------------
            st.markdown("### ➕ Crear nuevo horario")

            df_salones = obtener_catalogo_salones()
            # Fetch valid courses instead of just periods
            df_cursos = obtener_cursos_existentes() 

            if df_cursos.empty:
                st.warning("⚠️ No hay cursos registrados. Ve a la sección 'Cursos' primero.")
            elif df_salones.empty:
                st.warning("No hay salones registrados. Primero crea salones.")
            else:
                with st.form("form_nuevo_horario"):
                    # Filter logic: Select Period first, then show courses for that period
                    periodos_disponibles = df_cursos["id_periodo"].unique()
                    
                    c_top1, c_top2 = st.columns(2)
                    with c_top1:
                        periodo_sel = st.selectbox("1. Selecciona Periodo", periodos_disponibles)
                    
                    # Filter courses by selected period
                    cursos_periodo = df_cursos[df_cursos["id_periodo"] == periodo_sel]
                    
                    # Create a label for the dropdown: "LIS-2082 (Sec 1) - Bases de Datos"
                    cursos_periodo["label"] = (
                        cursos_periodo["clave_materia"] + " (Sec " + 
                        cursos_periodo["seccion"].astype(str) + ") - " + 
                        cursos_periodo["materia_titulo"]
                    )
                    
                    with c_top2:
                        curso_seleccionado_label = st.selectbox(
                            "2. Selecciona Curso", 
                            cursos_periodo["label"]
                        )

                    st.markdown("---")
                    
                    # Get the IDs from the selection
                    row_curso = cursos_periodo[cursos_periodo["label"] == curso_seleccionado_label].iloc[0]
                    
                    # Schedule Details
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        id_salon = st.selectbox("Salón", df_salones["id_salon"])
                    with c2:
                        dias = st.multiselect("Días", [d.value for d in DiaSemana])
                    with c3:
                        hora = st.time_input("Hora Inicio", value=dt_time(9,0))
                        duracion = st.number_input("Duración (min)", value=90, step=30)

                    submitted = st.form_submit_button("Guardar Horario")
                    
                    if submitted:
                        if not dias:
                            st.error("Selecciona al menos un día.")
                        else:
                            # Pass the IDs from the selected course row
                            ok, msg = crear_horario(
                                id_salon=id_salon,
                                hora_inicio=hora,
                                duracion_min=duracion,
                                dias_semana=dias,
                                curso_clave=row_curso["clave_materia"],
                                curso_seccion=int(row_curso["seccion"]),
                                id_periodo=row_curso["id_periodo"]
                            )
                            if ok:
                                st.success(msg)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(msg)
