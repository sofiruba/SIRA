import streamlit as st
import pandas as pd

import redis_app.consultas_redis as redis_consultas
import redis_app.redis_crud_app as redis_crud
import redis_app.carga_redis as redis_carga


def render_ciudadano():
    st.header("Redis - Estado en tiempo real")
    st.caption("Redis almacena estados temporales: disponibilidad, saturación, capacidad, ranking y alertas.")

    tab_estado, tab_listas, tab_ranking = st.tabs([
        "Estado por ID",
        "Disponibles / Saturados",
        "Ranking"
    ])

    with tab_estado:
        id_punto = st.text_input("ID del punto verde", placeholder="Ej: 1", key="redis_ciu_estado_id")

        if st.button("Ver estado", key="redis_ciu_btn_estado"):
            if id_punto:
                estado = redis_consultas.obtener_estado_punto_verde(id_punto)
                if estado:
                    st.json(estado)
                else:
                    st.warning("No se encontró estado para ese punto.")
            else:
                st.error("Ingresá un ID.")

    with tab_listas:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Disponibles")
            if st.button("Ver disponibles", key="redis_ciu_btn_disponibles"):
                datos = redis_consultas.obtener_puntos_disponibles()
                if datos:
                    st.dataframe(pd.DataFrame({"Punto Verde": datos}), use_container_width=True)
                else:
                    st.info("No hay puntos disponibles.")

        with col2:
            st.subheader("Saturados")
            if st.button("Ver saturados", key="redis_ciu_btn_saturados"):
                datos = redis_consultas.obtener_puntos_saturados()
                if datos:
                    st.dataframe(pd.DataFrame({"Punto Verde": datos}), use_container_width=True)
                else:
                    st.info("No hay puntos saturados.")

    with tab_ranking:
        if st.button("Ver ranking", key="redis_ciu_btn_ranking"):
            ranking = redis_consultas.obtener_ranking()
            datos = [{"id_punto_verde": item[0], "puntaje": item[1]} for item in ranking]

            if datos:
                df = pd.DataFrame(datos)
                st.dataframe(df, use_container_width=True)
                st.bar_chart(df.set_index("id_punto_verde"))
            else:
                st.info("No hay ranking cargado.")


def render_admin():
    st.header("Redis - Monitoreo en tiempo real")
    st.caption("Administración de datos temporales: estados, alertas y ranking.")

    try:
        disponibles = redis_consultas.obtener_puntos_disponibles()
        saturados = redis_consultas.obtener_puntos_saturados()
        alertas = redis_consultas.obtener_alertas()
    except Exception as e:
        st.error(f"Error cargando Redis: {e}")
        disponibles, saturados, alertas = [], [], []

    c1, c2, c3 = st.columns(3)
    c1.metric("Disponibles", len(disponibles))
    c2.metric("Saturados", len(saturados))
    c3.metric("Alertas recientes", len(alertas))

    tab_consultas, tab_update, tab_delete, tab_carga = st.tabs([
        "Consultas",
        "Actualizar",
        "Eliminar",
        "Cargar datos"
    ])

    with tab_consultas:
        opcion = st.selectbox(
            "Consulta",
            ["Disponibles", "Saturados", "Alertas", "Estado por ID", "Ranking"],
            key="redis_admin_consulta"
        )

        if opcion == "Estado por ID":
            id_punto = st.text_input("ID punto verde", placeholder="Ej: 1", key="redis_admin_estado_id")

        if st.button("Ejecutar consulta Redis", key="redis_admin_btn_consulta"):
            if opcion == "Disponibles":
                if disponibles:
                    st.dataframe(pd.DataFrame({"Punto Verde": disponibles}), use_container_width=True)
                else:
                    st.info("No hay puntos disponibles.")

            elif opcion == "Saturados":
                if saturados:
                    st.dataframe(pd.DataFrame({"Punto Verde": saturados}), use_container_width=True)
                else:
                    st.info("No hay puntos saturados.")

            elif opcion == "Alertas":
                if alertas:
                    st.dataframe(pd.DataFrame(alertas), use_container_width=True)
                else:
                    st.info("No hay alertas.")

            elif opcion == "Estado por ID":
                if id_punto:
                    estado = redis_consultas.obtener_estado_punto_verde(id_punto)
                    if estado:
                        st.json(estado)
                    else:
                        st.warning("No se encontró estado para ese punto.")
                else:
                    st.error("Ingresá un ID.")

            elif opcion == "Ranking":
                ranking = redis_consultas.obtener_ranking()
                datos = [{"id_punto_verde": item[0], "puntaje": item[1]} for item in ranking]

                if datos:
                    df = pd.DataFrame(datos)
                    st.dataframe(df, use_container_width=True)
                    st.bar_chart(df.set_index("id_punto_verde"))
                else:
                    st.info("No hay ranking cargado.")

    with tab_update:
        st.subheader("Actualizar estado de punto verde")

        id_punto = st.text_input("ID punto verde", placeholder="Ej: 1", key="redis_admin_update_id")
        estado = st.selectbox("Nuevo estado", ["disponible", "saturado"], key="redis_admin_update_estado")
        capacidad = st.number_input("Capacidad actual (%)", min_value=0, max_value=100, step=1, key="redis_admin_update_capacidad")

        if st.button("Actualizar estado", key="redis_admin_btn_update"):
            if id_punto:
                st.success(redis_crud.actualizar_estado_punto(id_punto, estado, capacidad))
            else:
                st.error("Ingresá un ID.")

    with tab_delete:
        st.subheader("Eliminar datos temporales")

        opcion = st.selectbox(
            "Qué querés eliminar",
            ["Estado de un punto verde", "Todas las alertas recientes"],
            key="redis_admin_delete_opcion"
        )

        if opcion == "Estado de un punto verde":
            id_punto = st.text_input("ID punto verde", placeholder="Ej: 1", key="redis_admin_delete_id")

            if st.button("Eliminar estado", key="redis_admin_btn_delete_estado"):
                if id_punto:
                    st.warning(redis_crud.eliminar_estado_punto(id_punto))
                else:
                    st.error("Ingresá un ID.")

        elif opcion == "Todas las alertas recientes":
            if st.button("Eliminar alertas", key="redis_admin_btn_delete_alertas"):
                st.warning(redis_crud.eliminar_alertas())

    with tab_carga:
        st.subheader("Cargar datos de prueba")

        if st.button("Cargar redis_data.json", key="redis_admin_btn_cargar"):
            try:
                redis_carga.cargar_datos()
                st.success("Datos cargados correctamente en Redis.")
            except Exception as e:
                st.error(f"Error: {e}")


def render_dashboard():
    st.header("Redis - Métricas")
    st.caption("Resumen de datos temporales en memoria.")

    try:
        disponibles = redis_consultas.obtener_puntos_disponibles()
        saturados = redis_consultas.obtener_puntos_saturados()
        alertas = redis_consultas.obtener_alertas()
        ranking = redis_consultas.obtener_ranking()
    except Exception as e:
        st.error(f"Error cargando Redis: {e}")
        disponibles, saturados, alertas, ranking = [], [], [], []

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Disponibles", len(disponibles))
    c2.metric("Saturados", len(saturados))
    c3.metric("Alertas recientes", len(alertas))
    c4.metric("Ranking", len(ranking))