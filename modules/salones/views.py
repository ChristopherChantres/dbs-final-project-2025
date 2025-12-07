import streamlit as st
import pandas as pd
import altair as alt
import time
from modules.models import Rol, TipoSalon
from .queries import (
    obtener_catalogo_salones,
    obtener_salones_avanzado,
    obtener_top_salones_ocupados,
    obtener_periodos
)
from .transactions import crear_salon, borrar_salon

def view_salones():
    """
    Renderiza la vista principal de gestión de salones.
    Incluye catálogo, búsqueda avanzada y métricas de ocupación.
    Solo administradores pueden ver la opción de crear nuevos salones.
    """
    st.header("🏢 Gestión de Salones y Espacios")

    # Verificar rol del usuario
    usuario = st.session_state.get('usuario_activo', {})
    es_admin = usuario.get('rol') == Rol.ADMINISTRADOR.value

    # Definir las pestañas disponibles
    titulos_tabs = ["📋 Catálogo", "🔍 Búsqueda Avanzada", "📊 Ocupación"]
    if es_admin:
        titulos_tabs.append("➕ Nuevo Salón")

    # Crear las pestañas
    tabs = st.tabs(titulos_tabs)
    
    # Asignar variables a las pestañas para usarlas después
    tab_catalogo = tabs[0]
    tab_busqueda = tabs[1]
    tab_stats = tabs[2]
    tab_nuevo = tabs[3] if es_admin else None

    # --- TAB 1: CATÁLOGO ---
    with tab_catalogo:
        st.subheader("Listado de Salones")
        
        # Cargamos datos
        df_salones = obtener_catalogo_salones()
        
        if not df_salones.empty:
            # Mostramos métricas rápidas
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Salones", len(df_salones))
            
            # Verificamos columnas para evitar errores si la query cambia
            if 'capacidad' in df_salones.columns:
                col2.metric("Capacidad Promedio", f"{df_salones['capacidad'].mean():.0f} personas")
            
            if 'tipo' in df_salones.columns:
                top_tipo = df_salones['tipo'].mode()[0]
                col3.metric("Tipo más común", top_tipo)

            # Lógica de visualización/edición
            if es_admin:
                st.write("📝 **Modo Administrador**: Selecciona los salones que deseas eliminar.")
                
                # Añadimos columna para selección si no existe
                if "Eliminar" not in df_salones.columns:
                    df_salones["Eliminar"] = False
                
                # Reordenamos columnas para que Eliminar salga primero
                cols = ["Eliminar"] + [c for c in df_salones.columns if c != "Eliminar"]
                df_salones = df_salones[cols]

                # Editor de datos
                edited_df = st.data_editor(
                    df_salones,
                    column_config={
                        "Eliminar": st.column_config.CheckboxColumn(
                            "Eliminar",
                            help="Selecciona para borrar este salón",
                            default=False,
                        ),
                        "id_salon": st.column_config.TextColumn(
                            "ID Salón",
                            disabled=True
                        ),
                        "capacidad": st.column_config.NumberColumn(
                            "Capacidad",
                            disabled=True
                        ),
                        "tipo": st.column_config.TextColumn(
                            "Tipo",
                            disabled=True
                        )
                    },
                    disabled=["id_salon", "capacidad", "tipo"], # Refuerzo de seguridad
                    hide_index=True,
                    use_container_width=True,
                    key="editor_salones"
                )

                # Detectar filas marcadas para eliminar
                to_delete = edited_df[edited_df["Eliminar"] == True]
                
                if not to_delete.empty:
                    st.warning(f"Has seleccionado {len(to_delete)} salones para eliminar.")
                    if st.button("🗑️ Confirmar Eliminación", type="primary"):
                        for index, row in to_delete.iterrows():
                            success, msg = borrar_salon(row['id_salon'])
                            if success:
                                st.toast(f"Salón {row['id_salon']} eliminado.")
                            else:
                                st.error(f"Error al eliminar {row['id_salon']}: {msg}")
                        
                        time.sleep(1)
                        st.rerun()

            else:
                # Vista solo lectura para no admins
                st.dataframe(
                    df_salones, 
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("No se encontraron salones registrados.")

    # --- TAB 2: BÚSQUEDA ---
    with tab_busqueda:
        st.subheader("Encontrar salón")
        
        # Controles de filtro en columnas
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            capacidad_min = st.slider("Capacidad mínima requerida", 0, 200, 20, step=5)
        with c2:
            # Opciones hardcodeadas basadas en el ENUM de la BD
            tipo_opcion = st.selectbox("Tipo de espacio", ["Cualquiera", "Aula", "Laboratorio", "Auditorio"])
        with c3:
            st.write("") # Espaciado vertical
            st.write("") 
            btn_buscar = st.button("Buscar", type="primary", use_container_width=True)

        if btn_buscar:
            # Convertimos "Cualquiera" a None para la función de query
            tipo_filtro = None if tipo_opcion == "Cualquiera" else tipo_opcion
            
            df_resultados = obtener_salones_avanzado(capacidad_min, tipo_filtro)
            
            if not df_resultados.empty:
                st.success(f"✅ Se encontraron {len(df_resultados)} salones que cumplen los criterios.")
                st.dataframe(df_resultados, use_container_width=True, hide_index=True)
            else:
                st.warning("⚠️ No hay salones con esas características.")

    # --- TAB 3: ESTADÍSTICAS ---
    with tab_stats:
        st.subheader("Top Salones Ocupados")
        
        # Selector de Periodo
        df_periodos = obtener_periodos()
        if not df_periodos.empty:
            periodo_selec = st.selectbox("Seleccionar Periodo", df_periodos['id_periodo'])
            
            limit = st.slider("Cantidad a mostrar", 1, 5, 4)
            df_top = obtener_top_salones_ocupados(periodo_selec, limit)
            
            if not df_top.empty and 'horas_ocupadas' in df_top.columns:
                # Gráfico de barras con Altair para mejor visualización
                chart = alt.Chart(df_top).mark_bar().encode(
                    x=alt.X('id_salon', sort='-y', title='Salón'),
                    y=alt.Y('horas_ocupadas', title='Horas Ocupadas (Semanal)'),
                    color=alt.Color('tipo', legend=alt.Legend(title="Tipo")),
                    tooltip=['id_salon', 'tipo', 'capacidad', 'horas_ocupadas']
                ).properties(
                    height=400
                ).interactive()
                
                st.altair_chart(chart, use_container_width=True)
                
                # Tabla de datos debajo
                st.dataframe(df_top, use_container_width=True, hide_index=True)
            else:
                st.info("No hay datos de ocupación suficientes para este periodo.")
        else:
            st.warning("No hay periodos registrados en el sistema.")

    # --- TAB 4: NUEVO SALÓN (Solo Admin) ---
    if es_admin and tab_nuevo:
        with tab_nuevo:
            st.subheader("Registrar Nuevo Salón")
            st.markdown("Utiliza este formulario para dar de alta nuevos espacios en el sistema.")
            
            with st.form("form_nuevo_salon"):
                col_a, col_b = st.columns(2)
                with col_a:
                    new_id = st.text_input("ID del Salón (ej. IA104, CN105)", max_chars=10)
                    new_tipo = st.selectbox("Tipo de Espacio", [t.value for t in TipoSalon])
                with col_b:
                    new_capacidad = st.number_input("Capacidad (personas)", min_value=1, value=30, step=1)
                
                submitted = st.form_submit_button("💾 Crear Salón", type="primary")
                
                if submitted:
                    if new_id and new_capacidad:
                        exito, msg = crear_salon(new_id, new_capacidad, new_tipo)
                        if exito:
                            st.success(msg)
                            time.sleep(1) 
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("El ID y la capacidad son obligatorios.")
