import streamlit as st
import pandas as pd
import cassandra_app.consultas_cassandra as cassandra_consultas
import cassandra_app.cassandra_crud_app as cassandra_crud


def render(session):
    st.title("📦 Cassandra")
    st.write("""
    Cassandra almacena grandes volúmenes de recolecciones y retiros históricos.
    Consultas rápidas por usuario, punto verde, reciclador y zona.
    """)

    tab1, tab2, tab3, tab4 = st.tabs(["Consultas", "Crear", "Actualizar", "Eliminar"])

    # ====================================================
    # CONSULTAS
    # ====================================================
    with tab1:
        st.subheader("Consultas Cassandra")

        consulta = st.selectbox(
            "Seleccioná una consulta",
            [
                "Recolecciones por usuario",
                "Recolecciones por punto verde",
                "Retiros por reciclador",
                "Actividad por zona",
                "Buscar recolección por ID",
                "Últimas recolecciones de usuario",
                "Recolecciones con peso mayor a 20 kg (por punto verde)",
            ],
            key="cass_select_consulta"
        )

        if consulta == "Recolecciones por usuario":
            usuario_id = st.text_input("ID Usuario", key="cass_consulta_usuario")
        elif consulta == "Recolecciones por punto verde":
            punto_verde_id = st.text_input("ID Punto Verde", key="cass_consulta_pv")
        elif consulta == "Retiros por reciclador":
            reciclador_id = st.text_input("ID Reciclador", key="cass_consulta_rec")
        elif consulta == "Actividad por zona":
            zona = st.text_input("Zona (barrio)", key="cass_consulta_zona")
        elif consulta == "Buscar recolección por ID":
            recoleccion_id = st.number_input("ID Recolección", min_value=1, step=1, key="cass_consulta_id")
        elif consulta == "Últimas recolecciones de usuario":
            usuario_id = st.text_input("ID Usuario", key="cass_consulta_ultimas_u")
            limite = st.number_input("Cantidad", min_value=1, max_value=50, value=5, step=1, key="cass_consulta_limite")
        elif consulta == "Recolecciones con peso mayor a 20 kg (por punto verde)":
            punto_verde_id = st.text_input("ID Punto Verde", key="cass_consulta_pv_peso")

        if st.button("Ejecutar consulta Cassandra", key="cass_btn_consulta"):
            try:
                datos = None

                if consulta == "Recolecciones por usuario":
                    datos = cassandra_consultas.consultar_usuario(session, usuario_id)
                elif consulta == "Recolecciones por punto verde":
                    datos = cassandra_consultas.consultar_punto_verde(session, punto_verde_id)
                elif consulta == "Retiros por reciclador":
                    datos = cassandra_consultas.consultar_reciclador(session, reciclador_id)
                elif consulta == "Actividad por zona":
                    datos = cassandra_consultas.consultar_zona(session, zona)
                elif consulta == "Buscar recolección por ID":
                    row = cassandra_crud.obtener_recoleccion_por_id(int(recoleccion_id))
                    if row:
                        st.dataframe(pd.DataFrame([dict(row._asdict())]))
                    else:
                        st.warning("No se encontró la recolección.")
                    datos = None
                elif consulta == "Últimas recolecciones de usuario":
                    datos = cassandra_consultas.ultimas_recolecciones_usuario(session, usuario_id, int(limite))
                elif consulta == "Recolecciones con peso mayor a 20 kg (por punto verde)":
                    datos = cassandra_consultas.rango_fechas_punto_verde(session, punto_verde_id)

                if datos is not None:
                    if datos:
                        st.dataframe(pd.DataFrame([dict(r._asdict()) for r in datos]))
                    else:
                        st.warning("No se encontraron registros.")

            except Exception as e:
                st.error(f"Error: {e}")

        # Análisis rápido
        st.divider()
        st.subheader("Análisis por usuario")
        usuario_analisis = st.text_input("ID Usuario para análisis", value="1", key="cass_analisis_usuario")

        if st.button("Generar análisis", key="cass_btn_analisis"):
            try:
                total = cassandra_consultas.total_kg_usuario(session, usuario_analisis)
                resumen = cassandra_consultas.recolecciones_por_tipo(session, usuario_analisis)

                st.metric("Total reciclado (kg)", round(total, 2))

                if resumen:
                    df = pd.DataFrame(resumen.items(), columns=["Tipo", "Kg"])
                    st.dataframe(df)
                    st.bar_chart(df.set_index("Tipo"))
            except Exception as e:
                st.error(f"Error: {e}")

    # ====================================================
    # CREAR
    # ====================================================
    with tab2:
        st.subheader("Crear recolección")

        recoleccion_id = st.number_input("ID Recolección", min_value=1, step=1, key="cass_crear_id")
        usuario_id     = st.number_input("ID Usuario",     min_value=1, step=1, key="cass_crear_usuario")
        punto_verde_id = st.number_input("ID Punto Verde", min_value=1, step=1, key="cass_crear_pv")
        fecha          = st.text_input("Fecha (YYYY-MM-DD)", key="cass_crear_fecha")
        tipo           = st.text_input("Tipo de Residuo",    key="cass_crear_tipo")
        peso           = st.number_input("Peso (kg)", min_value=0.0, step=0.1, key="cass_crear_peso")

        if st.button("Crear recolección", key="cass_btn_crear"):
            if all([fecha, tipo]):
                try:
                    st.success(cassandra_crud.crear_recoleccion(
                        int(recoleccion_id), int(usuario_id), int(punto_verde_id),
                        fecha, tipo, peso
                    ))
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Completá todos los campos.")

    # ====================================================
    # ACTUALIZAR
    # ====================================================
    with tab3:
        st.subheader("Actualizar recolección")

        tipo_update = st.selectbox(
            "Qué querés actualizar",
            ["Peso", "Tipo de residuo"],
            key="cass_select_update"
        )

        recoleccion_id = st.number_input("ID Recolección", min_value=1, step=1, key="cass_update_id")

        if tipo_update == "Peso":
            nuevo_peso = st.number_input("Nuevo peso (kg)", min_value=0.0, step=0.1, key="cass_update_peso")
            if st.button("Actualizar peso", key="cass_btn_update_peso"):
                try:
                    st.info(cassandra_crud.actualizar_peso_recoleccion(int(recoleccion_id), nuevo_peso))
                except Exception as e:
                    st.error(f"Error: {e}")

        elif tipo_update == "Tipo de residuo":
            nuevo_tipo = st.text_input("Nuevo tipo de residuo", key="cass_update_tipo")
            if st.button("Actualizar tipo", key="cass_btn_update_tipo"):
                if nuevo_tipo:
                    try:
                        st.info(cassandra_crud.actualizar_tipo_residuo(int(recoleccion_id), nuevo_tipo))
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Ingresá el nuevo tipo.")

    # ====================================================
    # ELIMINAR
    # ====================================================
    with tab4:
        st.subheader("Eliminar recolección")

        recoleccion_id = st.number_input("ID Recolección a eliminar", min_value=1, step=1, key="cass_delete_id")

        if st.button("Eliminar recolección", key="cass_btn_delete"):
            try:
                st.warning(cassandra_crud.eliminar_recoleccion(int(recoleccion_id)))
            except Exception as e:
                st.error(f"Error: {e}")