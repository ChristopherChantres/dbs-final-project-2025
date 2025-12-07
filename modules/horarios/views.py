import streamlit as st
from datetime import time as dt_time, datetime
import time
from modules.models import Rol, DiaSemana

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
    
    titulos_tabs = ["📋 Horario completo", "🔍 Busqueda Parcial"]
    if es_profesor:
        titulos_tabs.append("👨‍🏫 Mis Horarios")
    if es_admin:
        titulos_tabs.append("🛠 Administrar horarios")

    tabs = st.tabs(titulos_tabs)

    tab_completo = tabs[0]
    tab_filtro = tabs[1]
    # Adjust index for optional tabs
    idx = 2
    tab_profesor = None
    if es_profesor:
        tab_profesor = tabs[idx]
        idx += 1
    
    tab_admin = None
    if es_admin:
        tab_admin = tabs[idx]


    # TAB 1: HORARIO COMPLETO
    with tab_completo:
        st.subheader("Listado general de horarios")

        df = obtener_horario_completo()

        if df.empty:
            st.info("No se encontraron horarios registrados.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de horarios", len(df))
            if "id_salon" in df.columns:
                col2.metric("Salones ocupados", df["id_salon"].nunique())
            if "materia" in df.columns:
                col3.metric("Materias programadas", df["materia"].nunique())

            st.dataframe(df, use_container_width=True, hide_index=True)

    # TAB 2: BUSQUEDA PARCIAL (FILTROS)
    with tab_filtro:
        st.subheader("Búsqueda Parcial de Horarios")
        
        # Load auxiliary data for filters
        df_completo = obtener_horario_completo()
        if df_completo.empty:
             st.warning("No hay datos para filtrar.")
        else:
            periodos_unicos = sorted(df_completo["id_periodo"].unique().tolist())
            salones_unicos = sorted(df_completo["id_salon"].unique().tolist())
            # Unique courses can be many, maybe filter by code
            cursos_unicos = sorted(df_completo["curso_clave"].unique().tolist())
            
            c1, c2 = st.columns(2)
            with c1:
                f_periodo = st.selectbox("Periodo (Requerido)", periodos_unicos)
                f_dia = st.selectbox("Día de la Semana", ["Todos"] + [d.value for d in DiaSemana])
            with c2:
                f_curso = st.selectbox("Clave de Materia (Opcional)", ["Todos"] + cursos_unicos)
                f_salon = st.selectbox("Salón (Opcional)", ["Todos"] + salones_unicos)
            
            # Button to apply filter
            if st.button("Buscar"):
                dia_param = None if f_dia == "Todos" else f_dia
                curso_param = None if f_curso == "Todos" else f_curso
                salon_param = None if f_salon == "Todos" else f_salon
                
                df_res = filtrar_horario(
                    id_periodo=f_periodo,
                    dia_semana=dia_param,
                    clave_materia=curso_param,
                    id_salon=salon_param
                )
                
                if df_res.empty:
                    st.warning("No se encontraron resultados con los filtros seleccionados.")
                else:
                    st.success(f"Se encontraron {len(df_res)} horarios.")
                    st.dataframe(df_res, use_container_width=True, hide_index=True)

    # TAB PROFESOR (SI APLICA)
    if es_profesor and tab_profesor:
        with tab_profesor:
            st.subheader("👨‍🏫 Mis Horarios")
            df = obtener_horario_completo()
            if df.empty:
                st.info("No hay horarios.")
            else:
                # Filter by user name vaguely or exact if we had the link
                # Current schema links course to 'profesor' string name, not ID.
                # We'll ask the user to type their name or filter by it if we knew it exactly.
                nombre_prof = usuario.get("nombre", "")
                if nombre_prof:
                     df_profe = df[df["profesor"].str.contains(nombre_prof, case=False, na=False)]
                     st.dataframe(df_profe, use_container_width=True, hide_index=True)
                else:
                     st.write("No se pudo identificar el nombre del profesor en la sesión.")

    # TAB ADMIN: CREAR / MODIFICAR / ELIMINAR
    if es_admin and tab_admin:
        with tab_admin:
            st.subheader("🛠 Administración de Horarios")
            
            opcion_admin = st.radio("Acción", ["➕ Crear Nuevo", "✏️ Modificar Existente", "🗑️ Eliminar"], horizontal=True)
            st.divider()

            if opcion_admin == "➕ Crear Nuevo":
                st.markdown("### Registrar nuevo horario")
                df_salones = obtener_catalogo_salones()
                df_cursos = obtener_cursos_existentes()

                if df_cursos.empty:
                    st.warning("No hay cursos registrados.")
                elif df_salones.empty:
                    st.warning("No hay salones registrados.")
                else:
                    with st.form("form_crear_horario"):
                        periodos_disponibles = sorted(df_cursos["id_periodo"].unique())
                        periodo_sel = st.selectbox("Periodo", periodos_disponibles)
                        
                        # Filter courses by period
                        cursos_periodo = df_cursos[df_cursos["id_periodo"] == periodo_sel].copy()
                        cursos_periodo["label"] = (
                            cursos_periodo["clave_materia"] + " (Sec " + 
                            cursos_periodo["seccion"].astype(str) + ") - " + 
                            cursos_periodo["materia_titulo"]
                        )
                        
                        curso_seleccionado_label = st.selectbox("Curso", cursos_periodo["label"])
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            id_salon = st.selectbox("Salón", df_salones["id_salon"])
                            dias = st.multiselect("Días", [d.value for d in DiaSemana])
                        with col_b:
                            hora = st.time_input("Hora Inicio", value=dt_time(7,0))
                            duracion = st.number_input("Duración (min)", value=90, step=15)
                        
                        submitted = st.form_submit_button("Guardar")
                        
                        if submitted:
                            row_curso = cursos_periodo[cursos_periodo["label"] == curso_seleccionado_label].iloc[0]
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

            elif opcion_admin == "✏️ Modificar Existente":
                st.markdown("### Modificar horario")
                
                # Select a schedule to edit
                df_all = obtener_horario_completo()
                if df_all.empty:
                    st.info("No hay horarios para modificar.")
                else:
                    # Helper column for display
                    df_all["display"] = (
                        df_all["id_periodo"] + " | " + 
                        df_all["dia_semana"] + " " + df_all["hora_inicio"].astype(str) + " | " +
                        df_all["materia"] + " (" + df_all["id_salon"] + ")"
                    )
                    
                    horario_sel_label = st.selectbox("Selecciona el horario a editar", df_all["display"])
                    
                    # Get selected row
                    row_sel = df_all[df_all["display"] == horario_sel_label].iloc[0]
                    
                    st.info(f"Editando horario ID: {row_sel['id_horario']}")
                    
                    with st.form("form_editar_horario"):
                        
                        df_salones = obtener_catalogo_salones()
                        list_salones = df_salones["id_salon"].tolist() if not df_salones.empty else []
                        
                        t_start = row_sel["hora_inicio"]
                        val_hora = (datetime.min + t_start).time() if hasattr(t_start, 'seconds') else t_start
                        try:
                            val_hora_str = str(row_sel["hora_inicio"]).split(" days ")[-1] # handle timedelta string
                            h, m, s = map(int, val_hora_str.split(":"))
                            val_hora = dt_time(h, m)
                        except:
                            val_hora = dt_time(9,0)

                        c1, c2 = st.columns(2)
                        with c1:
                            new_salon = st.selectbox("Salón", list_salones, index=list_salones.index(row_sel["id_salon"]) if row_sel["id_salon"] in list_salones else 0)
                            new_dia = st.selectbox("Día", [d.value for d in DiaSemana], index=[d.value for d in DiaSemana].index(row_sel["dia_semana"]) if row_sel["dia_semana"] in [d.value for d in DiaSemana] else 0)
                        with c2:
                            new_hora = st.time_input("Hora Inicio", value=val_hora)
                            new_duracion = st.number_input("Duración (min)", value=int(row_sel["duracion_minutos"]))
                            
                        submit_edit = st.form_submit_button("Actualizar Horario")
                        
                        if submit_edit:
                            ok, msg = actualizar_horario(
                                id_horario=int(row_sel["id_horario"]),
                                id_salon=new_salon,
                                hora_inicio=new_hora,
                                duracion_min=new_duracion,
                                dia_semana=new_dia
                            )
                            if ok:
                                st.success(msg)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(msg)

            elif opcion_admin == "🗑️ Eliminar":
                st.markdown("### Eliminar horarios")
                st.warning("Esta acción eliminará el horario seleccionado.")
                
                df_all = obtener_horario_completo()
                if df_all.empty:
                    st.info("No hay horarios.")
                else:
                    df_all["Eliminar"] = False
                    
                    edited_df = st.data_editor(
                        df_all[["Eliminar", "id_horario", "dia_semana", "hora_inicio", "materia", "id_salon"]],
                        column_config={
                            "Eliminar": st.column_config.CheckboxColumn("¿Eliminar?", default=False)
                        },
                        hide_index=True,
                        use_container_width=True,
                        key="delete_editor"
                    )
                    
                    to_delete = edited_df[edited_df["Eliminar"] == True]
                    
                    if not to_delete.empty:
                        if st.button(f"Confirmar eliminación de {len(to_delete)} registros", type="primary"):
                            errores = []
                            for _, row in to_delete.iterrows():
                                ok, msg = eliminar_horario(row["id_horario"])
                                if not ok:
                                    errores.append(f"ID {row['id_horario']}: {msg}")
                            
                            if errores:
                                st.error("Errores al eliminar:\n" + "\n".join(errores))
                            else:
                                st.success("Horarios eliminados correctamente.")
                                time.sleep(1)
                                st.rerun()
