import streamlit as st
from datetime import datetime, time
import pandas as pd
from .queries import obtener_disponibilidad_salones, obtener_mis_reservaciones

def view_reservaciones():
    """
    Vista para consultar disponibilidad de salones y gestionar reservaciones.
    """
    st.header("Gestión de Reservaciones")
    
    # Crear pestañas para separar la búsqueda de "Mis Reservaciones"
    tab_nueva, tab_mis = st.tabs(["📅 Nueva Reservación", "📋 Mis Reservaciones"])
    
    # --- TAB 1: NUEVA RESERVACIÓN ---
    with tab_nueva:
        st.markdown("### 🔍 Consultar Disponibilidad")
        st.markdown("Consulta los espacios disponibles por fecha y hora.")

        # Contenedor para el formulario de búsqueda
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fecha_reserva = st.date_input(
                    "Fecha", 
                    min_value=datetime.today(),
                    help="Selecciona el día para la reservación",
                    key="res_fecha"
                )
                
            with col2:
                hora_inicio = st.time_input(
                    "Hora de Inicio", 
                    value=time(7, 0),
                    step=1800, 
                    help="Horario de inicio de la reservación",
                    key="res_hora"
                )
                
            with col3:
                duracion = st.number_input(
                    "Duración (minutos)", 
                    min_value=30, 
                    max_value=300, 
                    step=30, 
                    value=60,
                    help="Duración del evento en minutos",
                    key="res_duracion"
                )

            # Botón de búsqueda
            buscar = st.button("Consultar Disponibilidad", type="primary", use_container_width=True)

        # Sección de resultados
        if buscar:
            with st.spinner("Verificando disponibilidad en tiempo real..."):
                df_disponibles = obtener_disponibilidad_salones(fecha_reserva, hora_inicio, duracion)
            
            if not df_disponibles.empty:
                st.success(f"✅ Se encontraron {len(df_disponibles)} espacios disponibles.")
                
                st.dataframe(
                    df_disponibles,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "id_salon": st.column_config.TextColumn(
                            "Salón",
                            help="Código del salón",
                            width="small"
                        ),
                        "tipo": st.column_config.TextColumn(
                            "Tipo de Espacio",
                            width="medium"
                        ),
                        "capacidad": st.column_config.NumberColumn(
                            "Capacidad",
                            format="%d personas"
                        )
                    }
                )
                st.info("💡 Para reservar, toma nota del ID del salón.")
            else:
                st.error("❌ No hay salones disponibles para los criterios seleccionados.")
                st.markdown("""
                    **Sugerencias:**
                    - Intenta con una duración menor.
                    - Busca en otro horario.
                    - Verifica si es fin de semana o día festivo.
                """)

    # --- TAB 2: MIS RESERVACIONES ---
    with tab_mis:
        st.markdown("### 🗒️ Mis Reservaciones Activas")
        
        # Obtener usuario activo de la sesión
        usuario = st.session_state.get('usuario_activo')
        
        if not usuario:
            st.warning("Debes iniciar sesión para ver tus reservaciones.")
        else:
            id_usuario = usuario.get('id_usuario')
            
            # Cargar reservaciones
            with st.spinner("Cargando tus reservaciones..."):
                df_reservas = obtener_mis_reservaciones(id_usuario)
            
            if not df_reservas.empty:
                # Métricas resumen
                total = len(df_reservas)
                # Filtrar futuras (asumiendo que 'fecha' y 'hora_inicio' permiten comparar)
                # Para simplificar, solo mostramos el total por ahora.
                st.metric("Total de Reservaciones", total)
                
                st.dataframe(
                    df_reservas,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "id_reservacion": st.column_config.NumberColumn(
                            "# ID",
                            format="%d",
                            width="small"
                        ),
                        "id_salon": st.column_config.TextColumn(
                            "Salón",
                            width="small"
                        ),
                        "fecha": st.column_config.DateColumn(
                            "Fecha",
                            format="DD/MM/YYYY"
                        ),
                        "hora_inicio": st.column_config.TimeColumn(
                            "Hora Inicio",
                            format="HH:mm"
                        ),
                        "duracion_minutos": st.column_config.NumberColumn(
                            "Duración",
                            format="%d min",
                            help="Duración en minutos"
                        ),
                        "motivo": st.column_config.TextColumn(
                            "Motivo",
                            width="large"
                        ),
                        "usuario": None, # Ocultamos la columna usuario pues ya sabemos que es el usuario actual
                        "id_periodo": None # Ocultamos ID técnico
                    }
                )
            else:
                st.info("📭 No tienes reservaciones registradas.")
                st.markdown("Ve a la pestaña **Nueva Reservación** para agendar un espacio.")
