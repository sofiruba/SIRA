import streamlit as st
import pandas as pd
import redis_app.carga_redis as redis_carga
import redis_app.consultas_redis as redis_consultas
import redis_app.redis_crud_app as redis_crud
 
 
def render():
    st.title("⚡ Redis - Estado en tiempo real")
    st.write("""
    Redis administra estados temporales y de acceso rápido:
    disponibilidad, saturación, ranking y alertas de puntos verdes.
    """)
 
    tab1, tab2, tab3 = st.tabs(["Consultas", "Actualizar", "Eliminar"])
 
    # ====================================================
    # CONSULTAS
    # ====================================================
    with tab1:
        st.subheader("Consultas Redis")
 
        consulta = st.selectbox(
            "Seleccioná una consulta",
            [
                "Estado de punto verde por ID",
                "Puntos verdes disponibles",
                "Puntos verdes saturados",
                "Ranking de puntos verdes por uso",
                "Alertas recientes"
            ],
            key="redis_select_consulta"
        )
 
        if consulta == "Estado de punto verde por ID":
            id_punto = st.text_input("ID del punto verde", placeholder="Ej: 1", key="redis_consulta_id")
 
        if st.button("Ejecutar consulta Redis", key="redis_btn_consulta"):
            if consulta == "Estado de punto verde por ID":
                if id_punto:
                    estado = redis_consultas.obtener_estado_punto_verde(id_punto)
                    if estado:
                        st.json(estado)
                    else:
                        st.warning("No se encontró estado para ese punto verde.")
                else:
                    st.error("Ingresá un ID.")
 
            elif consulta == "Puntos verdes disponibles":
                datos = redis_consultas.obtener_puntos_disponibles()
                if datos:
                    st.dataframe(pd.DataFrame({"punto_verde_disponible": datos}), use_container_width=True)
                else:
                    st.warning("No se encontraron resultados.")
 
            elif consulta == "Puntos verdes saturados":
                datos = redis_consultas.obtener_puntos_saturados()
                if datos:
                    st.dataframe(pd.DataFrame({"punto_verde_saturado": datos}), use_container_width=True)
                else:
                    st.warning("No se encontraron resultados.")
 
            elif consulta == "Ranking de puntos verdes por uso":
                ranking = redis_consultas.obtener_ranking()
                datos = [{"id_punto_verde": item[0], "puntaje": item[1]} for item in ranking]
                if datos:
                    df = pd.DataFrame(datos)
                    st.dataframe(df, use_container_width=True)
                    st.bar_chart(df.set_index("id_punto_verde"))
                else:
                    st.warning("No hay ranking cargado.")
 
            elif consulta == "Alertas recientes":
                alertas = redis_consultas.obtener_alertas()
                if alertas:
                    st.dataframe(pd.DataFrame(alertas), use_container_width=True)
                else:
                    st.warning("No hay alertas cargadas.")
 
    # ====================================================
    # ACTUALIZAR
    # ====================================================
    with tab2:
        st.subheader("Actualizar estado de un punto verde")
 
        id_punto = st.text_input("ID punto verde", placeholder="Ej: 1", key="redis_update_id")
        estado_nuevo = st.selectbox("Nuevo estado", ["disponible", "saturado"], key="redis_update_estado")
        capacidad = st.number_input("Nueva capacidad actual", min_value=0, max_value=100, step=1, key="redis_update_cap")
 
        if st.button("Actualizar estado", key="redis_btn_update"):
            if id_punto:
                st.success(redis_crud.actualizar_estado_punto(id_punto, estado_nuevo, capacidad))
            else:
                st.error("Ingresá un ID de punto verde.")
 
    # ====================================================
    # ELIMINAR
    # ====================================================
    with tab3:
        st.subheader("Eliminar datos temporales de Redis")
 
        opcion = st.selectbox(
            "Qué querés eliminar",
            ["Estado de un punto verde", "Todas las alertas recientes"],
            key="redis_select_delete"
        )
 
        if opcion == "Estado de un punto verde":
            id_punto = st.text_input("ID del punto verde", placeholder="Ej: 1", key="redis_delete_id")
            if st.button("Eliminar estado", key="redis_btn_delete_estado"):
                if id_punto:
                    st.warning(redis_crud.eliminar_estado_punto(id_punto))
                else:
                    st.error("Ingresá un ID.")
 
        elif opcion == "Todas las alertas recientes":
            if st.button("Eliminar alertas", key="redis_btn_delete_alertas"):
                st.warning(redis_crud.eliminar_alertas())
 
   