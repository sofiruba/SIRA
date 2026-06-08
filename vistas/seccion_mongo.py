import json
import streamlit as st
import pandas as pd

import mongodb_app.consultas_mongo as mongo
import mongodb_app.mongo_crud_app as mongo_crud


def render_ciudadano(coleccion_puntos, coleccion_residuos, capturar_salida):
    st.header("MongoDB - Puntos verdes y residuos")
    st.caption("MongoDB almacena datos descriptivos: puntos verdes, residuos, horarios, barrios y comunas.")

    tab_barrio, tab_residuo, tab_horario = st.tabs([
        "Buscar por barrio / ID",
        "Buscar por residuo",
        "Buscar por horario / zona"
    ])

    with tab_barrio:
        st.subheader("Buscar punto verde por barrio")
        barrio = st.text_input("Barrio", key="mongo_ciu_barrio")

        if st.button("Buscar por barrio", key="mongo_ciu_btn_barrio"):
            if barrio:
                resultados = mongo_crud.buscar_punto_verde_por_barrio(coleccion_puntos, barrio)
                if resultados:
                    for r in resultados:
                        st.json(r)
                else:
                    st.warning("No se encontraron puntos verdes.")
            else:
                st.error("Ingresá un barrio.")

        st.divider()

        st.subheader("Buscar punto verde por ID")
        id_pv = st.number_input("ID del punto verde", min_value=1, step=1, key="mongo_ciu_id_pv")

        if st.button("Buscar por ID", key="mongo_ciu_btn_id"):
            punto = mongo_crud.buscar_punto_verde_por_id(int(id_pv))
            if punto:
                st.json(punto)
            else:
                st.warning("No se encontró un punto verde con ese ID.")

    with tab_residuo:
        st.subheader("Buscar por tipo de residuo")

        opcion = st.selectbox(
            "Consulta",
            [
                "Buscar residuo por nombre",
                "Puntos verdes que aceptan RAEEs",
                "Botellas de Amor y Cápsulas de Café",
                "Residuos reciclables",
                "Residuos de tratamiento especial",
                "Residuos del contenedor amarillo",
                "Residuos reutilizables u orgánicos",
            ],
            key="mongo_ciu_residuo_opcion"
        )

        if opcion == "Buscar residuo por nombre":
            nombre = st.text_input("Nombre del residuo", key="mongo_ciu_res_nombre")

        if st.button("Buscar residuo", key="mongo_ciu_btn_residuo"):
            if opcion == "Buscar residuo por nombre":
                if nombre:
                    resultados = mongo_crud.buscar_residuo_por_nombre(coleccion_residuos, nombre)
                    if resultados:
                        for r in resultados:
                            st.json(r)
                    else:
                        st.warning("No se encontraron residuos.")
                else:
                    st.error("Ingresá un nombre.")

            elif opcion == "Puntos verdes que aceptan RAEEs":
                capturar_salida(mongo.consulta1, coleccion_puntos)

            elif opcion == "Botellas de Amor y Cápsulas de Café":
                capturar_salida(mongo.consulta3, coleccion_puntos)

            elif opcion == "Residuos reciclables":
                capturar_salida(mongo.consulta6, coleccion_residuos)

            elif opcion == "Residuos de tratamiento especial":
                capturar_salida(mongo.consulta7, coleccion_residuos)

            elif opcion == "Residuos del contenedor amarillo":
                capturar_salida(mongo.consulta8, coleccion_residuos)

            elif opcion == "Residuos reutilizables u orgánicos":
                capturar_salida(mongo.consulta9, coleccion_residuos)

    with tab_horario:
        st.subheader("Buscar por horario o zona")

        opcion = st.selectbox(
            "Filtro",
            [
                "Abiertos los sábados",
                "En Villa Lugano",
                "En comunas 7 y 8",
            ],
            key="mongo_ciu_horario_opcion"
        )

        if st.button("Buscar horario / zona", key="mongo_ciu_btn_horario"):
            if opcion == "Abiertos los sábados":
                capturar_salida(mongo.consulta2, coleccion_puntos)

            elif opcion == "En Villa Lugano":
                capturar_salida(mongo.consulta4, coleccion_puntos)

            elif opcion == "En comunas 7 y 8":
                capturar_salida(mongo.consulta5, coleccion_puntos)


def render_admin(coleccion_puntos, coleccion_residuos):
    st.header("MongoDB - Gestión de puntos verdes y residuos")
    st.caption("ABM de documentos flexibles: puntos verdes y tipos de residuos.")

    operacion = st.selectbox(
        "Operación",
        ["Crear", "Actualizar", "Eliminar"],
        key="mongo_admin_operacion"
    )

    if operacion == "Crear":
        tipo = st.selectbox(
            "¿Qué querés crear?",
            ["Residuo", "Punto verde", "Muchos puntos verdes JSON", "Muchos residuos JSON"],
            key="mongo_admin_crear_tipo"
        )

        if tipo == "Residuo":
            nombre = st.text_input("Nombre del residuo", key="mongo_admin_crear_res_nombre")
            color = st.text_input("Color del contenedor", key="mongo_admin_crear_res_color")
            categoria = st.text_input("Categoría", key="mongo_admin_crear_res_categoria")

            if st.button("Crear residuo", key="mongo_admin_btn_crear_res"):
                if all([nombre, color, categoria]):
                    st.success(mongo_crud.crear_residuo(nombre, color, categoria))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Punto verde":
            nombre = st.text_input("Nombre", key="mongo_admin_crear_pv_nombre")
            direccion = st.text_input("Dirección", key="mongo_admin_crear_pv_direccion")
            barrio = st.text_input("Barrio", key="mongo_admin_crear_pv_barrio")
            comuna = st.text_input("Comuna", placeholder="Comuna 6", key="mongo_admin_crear_pv_comuna")
            residuos = st.text_input("Residuos aceptados", placeholder="R1,R2,R3", key="mongo_admin_crear_pv_residuos")
            dias = st.text_input("Días de atención", placeholder="Lunes,Sabado", key="mongo_admin_crear_pv_dias")
            apertura = st.text_input("Hora apertura", placeholder="09:00", key="mongo_admin_crear_pv_apertura")
            cierre = st.text_input("Hora cierre", placeholder="18:00", key="mongo_admin_crear_pv_cierre")

            if st.button("Crear punto verde", key="mongo_admin_btn_crear_pv"):
                if all([nombre, direccion, barrio, comuna, residuos, dias, apertura, cierre]):
                    lista_residuos = [r.strip().upper() for r in residuos.split(",")]
                    lista_dias = [d.strip() for d in dias.split(",")]

                    st.success(mongo_crud.crear_punto_verde(
                        nombre,
                        direccion,
                        barrio,
                        comuna,
                        lista_residuos,
                        lista_dias,
                        apertura,
                        cierre
                    ))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Muchos puntos verdes JSON":
            json_pv = st.text_area("Lista JSON de puntos verdes", key="mongo_admin_json_pv")

            if st.button("Crear puntos verdes", key="mongo_admin_btn_crear_muchos_pv"):
                try:
                    lista = json.loads(json_pv)
                    if isinstance(lista, list) and lista:
                        st.success(mongo_crud.crear_muchos_puntos_verdes(coleccion_puntos, lista))
                    else:
                        st.error("El JSON debe ser una lista con al menos un elemento.")
                except Exception as e:
                    st.error(f"Error: {e}")

        elif tipo == "Muchos residuos JSON":
            json_res = st.text_area("Lista JSON de residuos", key="mongo_admin_json_res")

            if st.button("Crear residuos", key="mongo_admin_btn_crear_muchos_res"):
                try:
                    lista = json.loads(json_res)
                    if isinstance(lista, list) and lista:
                        st.success(mongo_crud.crear_muchos_residuos(coleccion_residuos, lista))
                    else:
                        st.error("El JSON debe ser una lista con al menos un elemento.")
                except Exception as e:
                    st.error(f"Error: {e}")

    elif operacion == "Actualizar":
        tipo = st.selectbox(
            "¿Qué querés actualizar?",
            ["Horario de punto verde", "Tipo de residuo", "Agregar campo activo", "Eliminar campo activo"],
            key="mongo_admin_update_tipo"
        )

        if tipo == "Horario de punto verde":
            id_pv = st.number_input("ID punto verde", min_value=1, step=1, key="mongo_admin_update_id_pv")
            apertura = st.text_input("Nueva apertura", placeholder="09:00", key="mongo_admin_update_apertura")
            cierre = st.text_input("Nuevo cierre", placeholder="18:00", key="mongo_admin_update_cierre")

            if st.button("Actualizar horario", key="mongo_admin_btn_update_horario"):
                if apertura and cierre:
                    st.info(mongo_crud.actualizar_horario_punto(int(id_pv), apertura, cierre))
                else:
                    st.error("Completá apertura y cierre.")

        elif tipo == "Tipo de residuo":
            id_res = st.text_input("ID residuo", placeholder="R1", key="mongo_admin_update_res_id")
            nombre = st.text_input("Nuevo nombre", key="mongo_admin_update_res_nombre")
            color = st.text_input("Nuevo color", key="mongo_admin_update_res_color")
            categoria = st.text_input("Nueva categoría", key="mongo_admin_update_res_categoria")

            if st.button("Actualizar residuo", key="mongo_admin_btn_update_res"):
                if all([id_res, nombre, color, categoria]):
                    st.info(mongo_crud.actualizar_residuo(id_res.upper(), nombre, color, categoria))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Agregar campo activo":
            if st.button("Agregar activo=True", key="mongo_admin_btn_agregar_activo"):
                st.info(mongo_crud.agregar_campo_activo(coleccion_puntos))

        elif tipo == "Eliminar campo activo":
            if st.button("Eliminar campo activo", key="mongo_admin_btn_eliminar_activo"):
                st.warning(mongo_crud.eliminar_campo_activo(coleccion_puntos))

    elif operacion == "Eliminar":
        tipo = st.selectbox(
            "¿Qué querés eliminar?",
            ["Punto verde", "Tipo de residuo", "Muchos puntos verdes", "Muchos residuos"],
            key="mongo_admin_delete_tipo"
        )

        if tipo == "Punto verde":
            id_pv = st.number_input("ID punto verde", min_value=1, step=1, key="mongo_admin_delete_id_pv")

            if st.button("Eliminar punto verde", key="mongo_admin_btn_delete_pv"):
                st.warning(mongo_crud.eliminar_punto_verde(int(id_pv)))

        elif tipo == "Tipo de residuo":
            id_res = st.text_input("ID residuo", placeholder="R17", key="mongo_admin_delete_id_res")

            if st.button("Eliminar residuo", key="mongo_admin_btn_delete_res"):
                if id_res:
                    st.warning(mongo_crud.eliminar_residuo(id_res.upper()))
                else:
                    st.error("Ingresá un ID.")

        elif tipo == "Muchos puntos verdes":
            ids_input = st.text_input("IDs separados por coma", placeholder="1,2,3", key="mongo_admin_delete_muchos_pv")

            if st.button("Eliminar puntos verdes", key="mongo_admin_btn_delete_muchos_pv"):
                try:
                    ids = [int(i.strip()) for i in ids_input.split(",")]
                    st.warning(mongo_crud.eliminar_muchos_puntos_verdes(coleccion_puntos, ids))
                except Exception as e:
                    st.error(f"Error: {e}")

        elif tipo == "Muchos residuos":
            codigos_input = st.text_input("Códigos separados por coma", placeholder="R1,R2,R3", key="mongo_admin_delete_muchos_res")

            if st.button("Eliminar residuos", key="mongo_admin_btn_delete_muchos_res"):
                try:
                    codigos = [c.strip().upper() for c in codigos_input.split(",")]
                    st.warning(mongo_crud.eliminar_muchos_residuos(coleccion_residuos, coleccion_puntos, codigos))
                except Exception as e:
                    st.error(f"Error: {e}")


def render_dashboard(coleccion_puntos, coleccion_residuos):
    st.header("MongoDB - Métricas")
    st.caption("Cantidad de documentos almacenados en colecciones principales.")

    total_puntos = coleccion_puntos.count_documents({})
    total_residuos = coleccion_residuos.count_documents({})

    c1, c2 = st.columns(2)
    c1.metric("Puntos verdes", total_puntos)
    c2.metric("Tipos de residuos", total_residuos)