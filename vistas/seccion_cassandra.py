import streamlit as st
import pandas as pd

import cassandra_app.consultas_cassandra as cassandra_consultas
import cassandra_app.cassandra_crud_app as cassandra_crud


def _rows_to_df(rows):
    return pd.DataFrame([dict(r._asdict()) for r in rows])


def render_admin(session):
    st.header("Cassandra - Registro histórico")
    st.caption("Cassandra almacena datos históricos de recolecciones y retiros, modelados por consulta.")

    tab_consultas, tab_crear, tab_actualizar, tab_eliminar = st.tabs([
        "Consultas",
        "Crear",
        "Actualizar",
        "Eliminar"
    ])

    with tab_consultas:
        st.subheader("Historial de recolecciones")

        consulta = st.selectbox(
            "Tipo de búsqueda",
            [
                "Por usuario",
                "Por punto verde",
                "Por reciclador",
                "Por zona",
                "Por ID de recolección",
                "Últimas recolecciones de un usuario",
                "Recolecciones con peso > 20 kg por punto verde",
            ],
            key="cass_admin_consulta"
        )

        if consulta == "Por usuario":
            usuario_id = st.text_input("ID Usuario", key="cass_admin_usuario")
        elif consulta == "Por punto verde":
            punto_verde_id = st.text_input("ID Punto Verde", key="cass_admin_pv")
        elif consulta == "Por reciclador":
            reciclador_id = st.text_input("ID Reciclador", key="cass_admin_rec")
        elif consulta == "Por zona":
            zona = st.text_input("Zona / barrio", key="cass_admin_zona")
        elif consulta == "Por ID de recolección":
            recoleccion_id = st.number_input("ID Recolección", min_value=1, step=1, key="cass_admin_id")
        elif consulta == "Últimas recolecciones de un usuario":
            usuario_id = st.text_input("ID Usuario", key="cass_admin_ult_usuario")
            limite = st.number_input("Cantidad", min_value=1, max_value=50, value=5, step=1, key="cass_admin_ult_limite")
        elif consulta == "Recolecciones con peso > 20 kg por punto verde":
            punto_verde_id = st.text_input("ID Punto Verde", key="cass_admin_peso_pv")

        if st.button("Buscar en Cassandra", key="cass_admin_btn_buscar"):
            try:
                datos = None

                if consulta == "Por usuario":
                    datos = cassandra_consultas.consultar_usuario(session, usuario_id)

                elif consulta == "Por punto verde":
                    datos = cassandra_consultas.consultar_punto_verde(session, punto_verde_id)

                elif consulta == "Por reciclador":
                    datos = cassandra_consultas.consultar_reciclador(session, reciclador_id)

                elif consulta == "Por zona":
                    datos = cassandra_consultas.consultar_zona(session, zona)

                elif consulta == "Por ID de recolección":
                    row = cassandra_crud.obtener_recoleccion_por_id(
                        int(recoleccion_id),
                        session=session
                    )

                    if row:
                        st.dataframe(
                            pd.DataFrame([dict(row._asdict())]),
                            use_container_width=True
                        )
                    else:
                        st.warning("No se encontró la recolección.")

                elif consulta == "Últimas recolecciones de un usuario":
                    datos = cassandra_consultas.ultimas_recolecciones_usuario(
                        session,
                        usuario_id,
                        int(limite)
                    )

                elif consulta == "Recolecciones con peso > 20 kg por punto verde":
                    datos = cassandra_consultas.rango_fechas_punto_verde(
                        session,
                        punto_verde_id
                    )

                if datos is not None:
                    if datos:
                        st.dataframe(_rows_to_df(datos), use_container_width=True)
                    else:
                        st.warning("No se encontraron registros.")

            except Exception as e:
                st.error(f"Error: {e}")

    with tab_crear:
        st.subheader("Registrar nueva recolección")

        recoleccion_id = st.number_input("ID Recolección", min_value=1, step=1, key="cass_crear_id")
        usuario_id = st.number_input("ID Usuario", min_value=1, step=1, key="cass_crear_usuario")
        punto_verde_id = st.number_input("ID Punto Verde", min_value=1, step=1, key="cass_crear_pv")
        fecha = st.text_input("Fecha (YYYY-MM-DD)", key="cass_crear_fecha")
        tipo = st.text_input("Tipo de residuo", key="cass_crear_tipo")
        peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1, key="cass_crear_peso")

        if st.button("Registrar recolección", key="cass_btn_crear"):
            if all([fecha, tipo]):
                try:
                    mensaje = cassandra_crud.crear_recoleccion(
                        int(recoleccion_id),
                        int(usuario_id),
                        int(punto_verde_id),
                        fecha,
                        tipo,
                        peso,
                        session=session
                    )
                    st.success(mensaje)
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Completá todos los campos.")

    with tab_actualizar:
        st.subheader("Actualizar recolección")

        campo = st.selectbox(
            "Campo a actualizar",
            ["Peso", "Tipo de residuo"],
            key="cass_update_campo"
        )

        recoleccion_id = st.number_input("ID Recolección", min_value=1, step=1, key="cass_update_id")

        if campo == "Peso":
            nuevo_peso = st.number_input("Nuevo peso (kg)", min_value=0.0, step=0.1, key="cass_update_peso")

            if st.button("Actualizar peso", key="cass_btn_update_peso"):
                try:
                    st.info(cassandra_crud.actualizar_peso_recoleccion(
                        int(recoleccion_id),
                        nuevo_peso,
                        session=session
                    ))
                except Exception as e:
                    st.error(f"Error: {e}")

        elif campo == "Tipo de residuo":
            nuevo_tipo = st.text_input("Nuevo tipo de residuo", key="cass_update_tipo")

            if st.button("Actualizar tipo", key="cass_btn_update_tipo"):
                if nuevo_tipo:
                    try:
                        st.info(cassandra_crud.actualizar_tipo_residuo(
                            int(recoleccion_id),
                            nuevo_tipo,
                            session=session
                        ))
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Ingresá el nuevo tipo.")

    with tab_eliminar:
        st.subheader("Eliminar recolección")

        recoleccion_id = st.number_input(
            "ID Recolección a eliminar",
            min_value=1,
            step=1,
            key="cass_delete_id"
        )

        if st.button("Eliminar recolección", key="cass_btn_delete"):
            try:
                st.warning(cassandra_crud.eliminar_recoleccion(
                    int(recoleccion_id),
                    session=session
                ))
            except Exception as e:
                st.error(f"Error: {e}")


def render_dashboard(session):
    st.header("Cassandra - Métricas históricas")
    st.caption("Análisis histórico de recolecciones por usuario y tipo de residuo.")

    usuario_id = st.text_input("ID Usuario", value="1", key="cass_dashboard_usuario")

    if st.button("Analizar usuario", key="cass_dashboard_btn"):
        try:
            total = cassandra_consultas.total_kg_usuario(session, usuario_id)
            resumen = cassandra_consultas.recolecciones_por_tipo(session, usuario_id)

            st.metric("Total reciclado (kg)", round(total, 2))

            if resumen:
                df = pd.DataFrame(
                    resumen.items(),
                    columns=["Tipo de residuo", "Kg"]
                )
                st.dataframe(df, use_container_width=True)
                st.bar_chart(df.set_index("Tipo de residuo"))
            else:
                st.warning("No hay datos para ese usuario.")

        except Exception as e:
            st.error(f"Error Cassandra: {e}")