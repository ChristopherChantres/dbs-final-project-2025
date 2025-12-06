# Timetable grid

import streamlit as st
import pandas as pd
import altair as alt
import time

from datetime import time as dt_time

from modules.models import Rol
from .queries import (
    obtener_horario_completo,
    filtrar_horario,
    obtener_catalogo_salones,  # si está en otro módulo, ajusta el import
)
from .transactions import (
    crear_horario,
    actualizar_horario,
    eliminar_horario,
)


def view_horarios():
    

   
    usuario = st.session_state.get("usuario_activo", {})
    rol_usuario = usuario.get("rol")

    es_admin = rol_usuario == Rol.ADMINISTRADOR.value
    es_profesor = rol_usuario == Rol.PROFESOR.value
    es_alumno = rol_usuario == Rol.ALUMNO.value

    
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

            if "idSalon" in df.columns:
                col2.metric("Salones distintos", df["idSalon"].nunique())

            if "materia" in df.columns:
                col3.metric("Materias distintas", df["materia"].nunique())

           
            c1, c2, c3 = st.columns(3)
            with c1:
                salones = ["Todos"] + sorted(df["idSalon"].unique().tolist())
                filtro_salon = st.selectbox("Filtrar por salón", salones)
            with c2:
                materias = ["Todas"] + sorted(df["materia"].unique().tolist())
                filtro_materia = st.selectbox("Filtrar por materia", materias)
            with c3:
                profesores = ["Todos"] + sorted(df["profesor"].dropna().unique().tolist())
                filtro_profesor = st.selectbox("Filtrar por profesor", profesores)

            df_filtrado = df.copy()
            if filtro_salon != "Todos":
                df_filtrado = df_filtrado[df_filtrado["idSalon"] == filtro_salon]
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
            periodos_unicos = df["idPeriodo"].unique().tolist()
            c1, c2 = st.columns(2)
            with c1:
                id_periodo = st.selectbox("Periodo", periodos_unicos)
            with c2:
                dia_semana = st.selectbox(
                    "Día de la semana (opcional)",
                    ["Todos", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
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
                        "idHorario": st.column_config.TextColumn("ID Horario", disabled=True),
                        "hora": st.column_config.TextColumn("Hora", disabled=True),
                        "duracion": st.column_config.NumberColumn("Duración", disabled=True),
                        "diasSemana": st.column_config.TextColumn("Días", disabled=True),
                        "idSalon": st.column_config.TextColumn("Salón", disabled=True),
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
                            ok, msg = eliminar_horario(int(row["idHorario"]))
                            if ok:
                                st.toast(f"Horario {row['idHorario']} eliminado.")
                            else:
                                st.error(f"Error al eliminar {row['idHorario']}: {msg}")
                        time.sleep(1)
                        st.rerun()

            st.markdown("---")

            # --------- SUBSECCION: CREAR NUEVO HORARIO -------------
            st.markdown("### ➕ Crear nuevo horario")

            df_salones = obtener_catalogo_salones()
            if df_salones.empty:
                st.warning("No hay salones registrados. Primero crea salones.")
            else:
                with st.form("form_nuevo_horario"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        id_salon = st.selectbox(
                            "Salón",
                            options=df_salones["id_salon"].tolist()
                        )
                        dias_semana = st.text_input(
                            "Días de la semana (ej. MON-WED-FRI)"
                        )
                    with c2:
                        hora_inicio = st.time_input(
                            "Hora de inicio",
                            value=dt_time(7, 0)
                        )
                        duracion_min = st.number_input(
                            "Duración (minutos)",
                            min_value=10,
                            max_value=300,
                            value=60,
                            step=10
                        )
                    with c3:
                        curso_clave = st.text_input("Clave del curso")
                        curso_seccion = st.number_input(
                            "Sección del curso",
                            min_value=1,
                            step=1,
                            value=1
                        )

                    submitted = st.form_submit_button("💾 Crear horario", type="primary")

                    if submitted:
                        if not (id_salon and dias_semana and curso_clave):
                            st.warning("ID salón, días y clave del curso son obligatorios.")
                        else:
                            ok, msg = crear_horario(
                                id_salon=id_salon,
                                hora_inicio=hora_inicio,
                                duracion_min=int(duracion_min),
                                dias_semana=dias_semana,
                                curso_clave=curso_clave,
                                curso_seccion=int(curso_seccion),
                            )
                            if ok:
                                st.success(msg)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(msg)
