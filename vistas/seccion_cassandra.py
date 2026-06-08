import streamlit as st
import pandas as pd
import cassandra_app.consultas_cassandra as cassandra_consultas
import cassandra_app.cassandra_crud_app as cassandra_crud


def render(session):
    st.title("📦 Cassandra - Registros históricos")
    st.write("""
    Cassandra almacena grandes volúmenes de recolecciones y retiros históricos.
    Consultas rápidas por usuario, punto verde, reciclador y zona.
    """)

    tab1, tab2, tab3 = st.tabs(["Consultas", "CRUD", "Análisis"])

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
                "Actividad por zona"
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
            zona = st.text_input("Zona", key="cass_consulta_zona")

        if st.button("Ejecutar consulta Cassandra", key="cass_btn_consulta"):
            try:
                if consulta == "Recolecciones por usuario":
                    datos = cassandra_consultas.consultar_usuario(session, usuario_id)
                elif consulta == "Recolecciones por punto verde":
                    datos = cassandra_consultas.consultar_punto_verde(session, punto_verde_id)
                elif consulta == "Retiros por reciclador":
                    datos = cassandra_consultas.consultar_reciclador(session, reciclador_id)
                else:
                    datos = cassandra_consultas.consultar_zona(session, zona)

                if datos:
                    st.dataframe(pd.DataFrame(datos))
                else:
                    st.warning("No se encontraron registros.")
            except Exception as e:
                st.error(e)

    # ====================================================
    # CRUD
    # ====================================================
    with tab2:
        st.subheader("CRUD Cassandra")

        crud = st.selectbox(
            "Operación",
            ["Crear", "Buscar por ID", "Actualizar peso", "Actualizar tipo", "Eliminar"],
            key="cass_select_crud"
        )

        if crud == "Crear":
            recoleccion_id = st.text_input("ID Recolección", key="cass_crear_id")
            usuario_id = st.text_input("Usuario", key="cass_crear_usuario")
            punto_verde_id = st.text_input("Punto Verde", key="cass_crear_pv")
            fecha = st.text_input("Fecha (YYYY-MM-DD)", key="cass_crear_fecha")
            tipo = st.text_input("Tipo Residuo", key="cass_crear_tipo")
            peso = st.number_input("Peso KG", key="cass_crear_peso")

            if st.button("Crear recolección", key="cass_btn_crear"):
                st.success(cassandra_crud.crear_recoleccion(
                    recoleccion_id, usuario_id, punto_verde_id, fecha, tipo, peso
                ))

        elif crud == "Buscar por ID":
            recoleccion_id = st.text_input("ID", key="cass_buscar_id")
            if st.button("Buscar", key="cass_btn_buscar"):
                dato = cassandra_crud.obtener_recoleccion_por_id(recoleccion_id)
                if dato:
                    st.json(dict(dato._asdict()))
                else:
                    st.warning("No encontrado.")

        elif crud == "Actualizar peso":
            recoleccion_id = st.text_input("ID Recolección", key="cass_update_peso_id")
            peso = st.number_input("Nuevo peso", key="cass_update_peso_val")
            if st.button("Actualizar peso", key="cass_btn_update_peso"):
                st.success(cassandra_crud.actualizar_peso_recoleccion(recoleccion_id, peso))

        elif crud == "Actualizar tipo":
            recoleccion_id = st.text_input("ID Recolección", key="cass_update_tipo_id")
            tipo = st.text_input("Nuevo tipo", key="cass_update_tipo_val")
            if st.button("Actualizar tipo", key="cass_btn_update_tipo"):
                st.success(cassandra_crud.actualizar_tipo_residuo(recoleccion_id, tipo))

        elif crud == "Eliminar":
            recoleccion_id = st.text_input("ID Recolección", key="cass_delete_id")
            if st.button("Eliminar", key="cass_btn_delete"):
                st.warning(cassandra_crud.eliminar_recoleccion(recoleccion_id))

    # ====================================================
    # ANÁLISIS
    # ====================================================
    with tab3:
        st.subheader("Análisis por usuario")

        usuario_id = st.text_input("ID Usuario para análisis", value="1", key="cass_analisis_usuario")

        if st.button("Generar análisis", key="cass_btn_analisis"):
            try:
                total = cassandra_consultas.total_kg_usuario(session, usuario_id)
                resumen = cassandra_consultas.recolecciones_por_tipo(session, usuario_id)

                st.metric("Total reciclado (kg)", round(total, 2))

                if resumen:
                    df = pd.DataFrame(resumen.items(), columns=["Tipo", "Kg"])
                    st.dataframe(df)
                    st.bar_chart(df.set_index("Tipo"))
            except Exception as e:
                st.error(e)