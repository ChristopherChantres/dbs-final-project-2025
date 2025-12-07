import streamlit as st
from datetime import datetime, time, date
import pandas as pd
from .queries import (
    obtener_disponibilidad_salones, 
    obtener_mis_reservaciones, 
    obtener_periodos, 
    obtener_periodo_activo
)
from .transactions import (
    crear_reservacion, 
    crear_reservacion_periodica, 
    cancelar_reservacion, 
    cancelar_reservaciones_por_intervalo
)

def view_reservaciones():
    """
    Vista para consultar disponibilidad de salones y gestionar reservaciones.
    """
    st.header("🗒️ Gestión de Reservaciones")
    
    # Crear pestañas para separar la búsqueda de "Mis Reservaciones"
    tab_nueva, tab_mis = st.tabs(["📅 Nueva Reservación", "📋 Mis Reservaciones"])
    
    # --- TAB 1: NUEVA RESERVACIÓN ---
    with tab_nueva:
        st.markdown("### 🔍 Generar Nueva Reservación")
        
        tipo_reserva = st.radio(
            "Tipo de Reservación", 
            ["Individual (Fecha específica)", "Periódica (Día de la semana por todo el periodo)"],
            horizontal=True
        )

        usuario = st.session_state.get('usuario_activo')
        if not usuario:
            st.warning("🔒 Debes iniciar sesión para realizar reservaciones.")
            st.stop()
        
        id_usuario = usuario.get('id_usuario')

        if tipo_reserva.startswith("Individual"):
            # --- MODO INDIVIDUAL ---
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    fecha_reserva = st.date_input(
                        "Fecha", 
                        min_value=datetime.today(),
                        value=datetime.today(),
                        help="Selecciona el día para la reservación",
                        key="res_fecha"
                    )
                with col2:
                    hora_inicio = st.time_input(
                        "Hora de Inicio", 
                        value=time(9, 0),
                        step=1800, 
                        key="res_hora"
                    )
                with col3:
                    duracion = st.number_input(
                        "Duración (min)", 
                        min_value=30, max_value=300, step=30, value=60,
                        key="res_duracion"
                    )
                
                # Botón de búsqueda de disponibilidad
                if st.button("Consultar Disponibilidad", type="primary", use_container_width=True):
                    with st.spinner("Buscando salones disponibles..."):
                        df = obtener_disponibilidad_salones(fecha_reserva, hora_inicio, duracion)
                        st.session_state['res_disponibles'] = df
                        st.session_state['res_params'] = {
                            'fecha': fecha_reserva,
                            'hora': hora_inicio,
                            'duracion': duracion
                        }

            # Mostrar resultados si existen en session_state
            if 'res_disponibles' in st.session_state:
                df_disponibles = st.session_state['res_disponibles']
                
                # Verificar si los parámetros de búsqueda cambiaron (opcional, por ahora confiamos en el usuario)
                
                if not df_disponibles.empty:
                    st.success(f"✅ Se encontraron {len(df_disponibles)} espacios disponibles.")
                    st.dataframe(
                        df_disponibles, 
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "id_salon": "Salón",
                            "tipo": "Tipo",
                            "capacidad": "Capacidad"
                        }
                    )
                    
                    st.divider()
                    st.subheader("Confirmar Reservación")
                    
                    with st.form("form_confirmar_reserva"):
                        # Selección del salón de la lista de disponibles
                        opciones_salones = df_disponibles['id_salon'].tolist()
                        seleccion_salon = st.selectbox("Selecciona el Salón", opciones_salones)
                        motivo = st.text_input("Motivo de la reservación", placeholder="Ej. Asesoría de proyecto final")
                        
                        submitted = st.form_submit_button("Confirmar Reservación")
                        
                        if submitted:
                            if not motivo:
                                st.error("⚠️ Debes ingresar un motivo.")
                            else:
                                params = st.session_state.get('res_params', {})
                                # Usar params guardados para consistencia
                                f_res = params.get('fecha', fecha_reserva)
                                h_ini = params.get('hora', hora_inicio)
                                dur = params.get('duracion', duracion)
                                
                                id_periodo = obtener_periodo_activo(f_res)
                                if not id_periodo:
                                    st.error("❌ No hay un periodo académico activo para esta fecha.")
                                else:
                                    success, msg = crear_reservacion(
                                        id_usuario, seleccion_salon, f_res, 
                                        h_ini, dur, id_periodo, motivo
                                    )
                                    if success:
                                        st.success(f"🎉 {msg}")
                                        st.balloons()
                                        # Limpiar resultados para reiniciar flujo
                                        del st.session_state['res_disponibles']
                                        # st.rerun() # Opcional
                                    else:
                                        st.error(f"❌ {msg}")
                else:
                    st.error("❌ No hay salones disponibles en ese horario.")
                    if st.button("Limpiar búsqueda"):
                        del st.session_state['res_disponibles']
                        st.rerun()

        else:
            # --- MODO PERIÓDICO ---
            st.info("ℹ️ Esta opción reservará el salón seleccionado para **todos** los días de la semana elegidos dentro del periodo seleccionado.")
            
            with st.container(border=True):
                # Cargar periodos
                lista_periodos = obtener_periodos()
                if not lista_periodos:
                    st.error("No se encontraron periodos registrados.")
                else:
                    col_p, col_d = st.columns(2)
                    with col_p:
                        periodo_sel = st.selectbox("Periodo Académico", lista_periodos)
                    with col_d:
                        dia_semana_sel = st.selectbox("Día de la Semana", ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado'])

                    col_h, col_dur = st.columns(2)
                    with col_h:
                        hora_inicio_p = st.time_input("Hora de Inicio", value=time(9, 0), step=1800, key="p_hora")
                    with col_dur:
                        duracion_p = st.number_input("Duración (min)", min_value=30, max_value=300, step=30, value=60, key="p_dur")
                    
                    salon_input = st.text_input("ID del Salón (Ej. IA104)", help="Ingresa el código del salón a reservar.")
                    motivo_p = st.text_input("Motivo", placeholder="Ej. Taller semanal de Python", key="p_motivo")

                    if st.button("Crear Reservaciones Periódicas", type="primary"):
                        if not salon_input or not motivo_p:
                            st.warning("⚠️ Debes ingresar el salón y el motivo.")
                        else:
                            with st.spinner("Procesando reservaciones masivas..."):
                                success, msg = crear_reservacion_periodica(
                                    id_usuario, salon_input, dia_semana_sel, 
                                    hora_inicio_p, duracion_p, periodo_sel, motivo_p
                                )
                            
                            if success:
                                st.success(f"🎉 {msg}")
                            else:
                                st.error(f"❌ {msg}")

    # --- TAB 2: MIS RESERVACIONES ---
    with tab_mis:
        st.markdown("### 🗒️ Gestión de mis Reservaciones")
        
        usuario = st.session_state.get('usuario_activo')
        if not usuario:
            st.warning("Debes iniciar sesión para ver tus reservaciones.")
        else:
            id_usuario = usuario.get('id_usuario')
            
            # Cargar reservaciones
            df_reservas = obtener_mis_reservaciones(id_usuario)
            
            if not df_reservas.empty:
                st.dataframe(
                    df_reservas,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "id_reservacion": st.column_config.NumberColumn("# ID", format="%d", width="small"),
                        "id_salon": "Salón",
                        "fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
                        "hora_inicio": st.column_config.TimeColumn("Hora", format="HH:mm"),
                        "duracion_minutos": st.column_config.NumberColumn("Duración", format="%d min"),
                        "motivo": "Motivo"
                    }
                )
                
                st.divider()
                col_c1, col_c2 = st.columns(2)
                
                # Cancelación Individual
                with col_c1:
                    st.subheader("Cancelar una Reservación")
                    ids_reservas = df_reservas['id_reservacion'].tolist()
                    
                    with st.form("form_cancel_single"):
                        id_cancelar = st.selectbox("Selecciona ID a cancelar", ids_reservas)
                        confirm = st.checkbox(f"Estoy seguro de cancelar", key="chk_single")
                        
                        if st.form_submit_button("❌ Cancelar Seleccionada"):
                            if confirm:
                                success, msg = cancelar_reservacion(id_cancelar)
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                            else:
                                st.warning("Debes marcar la casilla de confirmación.")

                # Cancelación por Intervalo
                with col_c2:
                    st.subheader("Cancelar por Rango")
                    
                    with st.form("form_cancel_range"):
                        st.markdown("Borra todas tus reservaciones en un periodo.")
                        d_inicio = st.date_input("Fecha Inicio", value=date.today())
                        d_fin = st.date_input("Fecha Fin", value=date.today())
                        confirm_range = st.checkbox("Confirmar eliminación masiva", key="chk_range")
                        
                        if st.form_submit_button("🗑️ Cancelar en Rango"):
                            if d_inicio > d_fin:
                                st.error("La fecha de inicio no puede ser mayor a la fin.")
                            elif confirm_range:
                                success, msg = cancelar_reservaciones_por_intervalo(id_usuario, d_inicio, d_fin)
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                            else:
                                st.warning("Debes marcar la casilla de confirmación.")
            else:
                st.info("📭 No tienes reservaciones registradas.")
