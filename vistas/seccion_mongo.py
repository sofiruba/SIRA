import io
import contextlib
import streamlit as st
import mongodb_app.consultas_mongo as mongo
import mongodb_app.mongo_crud_app as mongo_crud


def _capturar_salida(funcion, *args):
    salida = io.StringIO()
    try:
        with contextlib.redirect_stdout(salida):
            funcion(*args)
        texto = salida.getvalue()
        if texto.strip():
            st.code(texto, language="text")
        else:
            st.warning("La consulta no devolvió resultados.")
    except Exception as e:
        st.error(f"Error: {e}")


def render(coleccion_puntos, coleccion_residuos):
    st.title("🍃 MongoDB")
    st.write("""
    MongoDB almacena información flexible y descriptiva,
    como puntos verdes, residuos aceptados, horarios, barrios y comunas.
    """)

    tab1, tab2, tab3, tab4 = st.tabs(["Consultas", "Crear", "Actualizar", "Eliminar"])

    # ====================================================
    # CONSULTAS
    # ====================================================
    with tab1:
        st.subheader("Consultas MongoDB")

        opcion = st.selectbox(
            "Seleccioná una consulta",
            [
                "Consulta 1 - Puntos verdes que aceptan RAEEs",
                "Consulta 2 - Puntos verdes abiertos los sábados",
                "Consulta 3 - Botellas de Amor y Cápsulas de Café",
                "Consulta 4 - Puntos verdes en Villa Lugano",
                "Consulta 5 - Puntos verdes en comunas 7 y 8",
                "Consulta 6 - Residuos reciclables",
                "Consulta 7 - Residuos de tratamiento especial",
                "Consulta 8 - Residuos del contenedor amarillo",
                "Consulta 9 - Residuos reutilizables u orgánicos",
                "Buscar punto verde por ID",
                "Buscar puntos verdes por barrio",
                "Buscar residuo por nombre",
            ],
            key="mongo_select_consulta"
        )

        if opcion == "Buscar punto verde por ID":
            id_punto_buscar = st.number_input("ID del punto verde", min_value=1, step=1, key="mongo_buscar_id")
        elif opcion == "Buscar puntos verdes por barrio":
            barrio_buscar = st.text_input("Barrio", key="mongo_buscar_barrio")
        elif opcion == "Buscar residuo por nombre":
            nombre_buscar = st.text_input("Nombre del residuo", key="mongo_buscar_residuo_nombre")

        if st.button("Ejecutar consulta MongoDB", key="mongo_btn_consulta"):
            if opcion.startswith("Consulta 1"):
                _capturar_salida(mongo.consulta1, coleccion_puntos)
            elif opcion.startswith("Consulta 2"):
                _capturar_salida(mongo.consulta2, coleccion_puntos)
            elif opcion.startswith("Consulta 3"):
                _capturar_salida(mongo.consulta3, coleccion_puntos)
            elif opcion.startswith("Consulta 4"):
                _capturar_salida(mongo.consulta4, coleccion_puntos)
            elif opcion.startswith("Consulta 5"):
                _capturar_salida(mongo.consulta5, coleccion_puntos)
            elif opcion.startswith("Consulta 6"):
                _capturar_salida(mongo.consulta6, coleccion_residuos)
            elif opcion.startswith("Consulta 7"):
                _capturar_salida(mongo.consulta7, coleccion_residuos)
            elif opcion.startswith("Consulta 8"):
                _capturar_salida(mongo.consulta8, coleccion_residuos)
            elif opcion.startswith("Consulta 9"):
                _capturar_salida(mongo.consulta9, coleccion_residuos)
            elif opcion == "Buscar punto verde por ID":
                punto = mongo_crud.buscar_punto_verde_por_id(int(id_punto_buscar))
                if punto:
                    st.json(punto)
                else:
                    st.warning("No se encontró un punto verde con ese ID.")
            elif opcion == "Buscar puntos verdes por barrio":
                if barrio_buscar:
                    resultados = mongo_crud.buscar_punto_verde_por_barrio(coleccion_puntos, barrio_buscar)
                    if resultados:
                        for r in resultados:
                            st.json(r)
                    else:
                        st.warning("No se encontraron puntos verdes en ese barrio.")
                else:
                    st.error("Ingresá un barrio.")
            elif opcion == "Buscar residuo por nombre":
                if nombre_buscar:
                    resultados = mongo_crud.buscar_residuo_por_nombre(coleccion_residuos, nombre_buscar)
                    if resultados:
                        for r in resultados:
                            st.json(r)
                    else:
                        st.warning("No se encontraron residuos con ese nombre.")
                else:
                    st.error("Ingresá un nombre de residuo.")

    # ====================================================
    # CREAR
    # ====================================================
    with tab2:
        st.subheader("Crear datos en MongoDB")

        tipo = st.selectbox(
            "Qué querés crear",
            ["Residuo", "Punto verde", "Muchos puntos verdes (JSON)", "Muchos residuos (JSON)"],
            key="mongo_select_crear"
        )

        if tipo == "Residuo":
            nombre = st.text_input("Nombre del residuo", key="mongo_crear_res_nombre")
            color = st.text_input("Color del contenedor", key="mongo_crear_res_color")
            categoria = st.text_input("Categoría", key="mongo_crear_res_categoria")

            if st.button("Crear residuo", key="mongo_btn_crear_residuo"):
                if nombre and color and categoria:
                    st.success(mongo_crud.crear_residuo(nombre, color, categoria))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Punto verde":
            nombre = st.text_input("Nombre", key="mongo_crear_pv_nombre")
            direccion = st.text_input("Dirección", key="mongo_crear_pv_dir")
            barrio = st.text_input("Barrio", key="mongo_crear_pv_barrio")
            comuna = st.text_input("Comuna", placeholder="Comuna 6", key="mongo_crear_pv_comuna")
            residuos = st.text_input("Residuos aceptados", placeholder="R1,R2,R3", key="mongo_crear_pv_residuos")
            dias = st.text_input("Días de atención", placeholder="Lunes,Martes,Sabado", key="mongo_crear_pv_dias")
            apertura = st.text_input("Hora apertura", placeholder="09:00", key="mongo_crear_pv_apertura")
            cierre = st.text_input("Hora cierre", placeholder="18:00", key="mongo_crear_pv_cierre")

            if st.button("Crear punto verde", key="mongo_btn_crear_pv"):
                if all([nombre, direccion, barrio, comuna, residuos, dias, apertura, cierre]):
                    lista_residuos = [r.strip().upper() for r in residuos.split(",")]
                    lista_dias = [d.strip() for d in dias.split(",")]
                    st.success(mongo_crud.crear_punto_verde(
                        nombre, direccion, barrio, comuna,
                        lista_residuos, lista_dias, apertura, cierre
                    ))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Muchos puntos verdes (JSON)":
            st.info("Pegá una lista JSON con los puntos verdes a insertar.")
            json_pv = st.text_area(
                "Lista de puntos verdes (JSON)",
                placeholder='[{"nombre": "...", "direccion": "...", ...}, ...]',
                key="mongo_crear_muchos_pv_json"
            )
            if st.button("Crear puntos verdes", key="mongo_btn_crear_muchos_pv"):
                if json_pv:
                    import json
                    try:
                        lista = json.loads(json_pv)
                        if isinstance(lista, list) and len(lista) > 0:
                            st.success(mongo_crud.crear_muchos_puntos_verdes(coleccion_puntos, lista))
                        else:
                            st.error("El JSON debe ser una lista con al menos un elemento.")
                    except json.JSONDecodeError:
                        st.error("El JSON ingresado no es válido.")
                else:
                    st.error("Ingresá el JSON.")

        elif tipo == "Muchos residuos (JSON)":
            st.info("Pegá una lista JSON con los residuos a insertar.")
            json_res = st.text_area(
                "Lista de residuos (JSON)",
                placeholder='[{"id_residuo": "R99", "nombre": "...", "color_contenedor": "...", "categoria": "..."}, ...]',
                key="mongo_crear_muchos_res_json"
            )
            if st.button("Crear residuos", key="mongo_btn_crear_muchos_res"):
                if json_res:
                    import json
                    try:
                        lista = json.loads(json_res)
                        if isinstance(lista, list) and len(lista) > 0:
                            st.success(mongo_crud.crear_muchos_residuos(coleccion_residuos, lista))
                        else:
                            st.error("El JSON debe ser una lista con al menos un elemento.")
                    except json.JSONDecodeError:
                        st.error("El JSON ingresado no es válido.")
                else:
                    st.error("Ingresá el JSON.")

    # ====================================================
    # ACTUALIZAR
    # ====================================================
    with tab3:
        st.subheader("Actualizar datos en MongoDB")

        tipo_update = st.selectbox(
            "Qué querés actualizar",
            ["Horario de punto verde", "Tipo de residuo", "Agregar campo activo", "Eliminar campo activo"],
            key="mongo_select_update"
        )

        if tipo_update == "Horario de punto verde":
            id_punto = st.number_input("ID del punto verde", min_value=1, step=1, key="mongo_update_pv_id")
            apertura = st.text_input("Nueva hora apertura", placeholder="09:00", key="mongo_update_apertura")
            cierre = st.text_input("Nueva hora cierre", placeholder="18:00", key="mongo_update_cierre")

            if st.button("Actualizar horario", key="mongo_btn_update_horario"):
                if apertura and cierre:
                    st.info(mongo_crud.actualizar_horario_punto(int(id_punto), apertura, cierre))
                else:
                    st.error("Completá apertura y cierre.")

        elif tipo_update == "Tipo de residuo":
            id_res = st.text_input("ID del residuo", placeholder="R1", key="mongo_update_res_id")
            nombre = st.text_input("Nuevo nombre", key="mongo_update_res_nombre")
            color = st.text_input("Nuevo color", key="mongo_update_res_color")
            categoria = st.text_input("Nueva categoría", key="mongo_update_res_cat")

            if st.button("Actualizar residuo", key="mongo_btn_update_res"):
                if all([id_res, nombre, color, categoria]):
                    st.info(mongo_crud.actualizar_residuo(id_res.upper(), nombre, color, categoria))
                else:
                    st.error("Completá todos los campos.")

        elif tipo_update == "Agregar campo activo":
            st.write("Agrega el campo `activo: True` a todos los puntos verdes que no lo tengan.")
            if st.button("Agregar campo activo", key="mongo_btn_agregar_activo"):
                st.info(mongo_crud.agregar_campo_activo(coleccion_puntos))

        elif tipo_update == "Eliminar campo activo":
            st.write("Elimina el campo `activo` de todos los puntos verdes.")
            if st.button("Eliminar campo activo", key="mongo_btn_eliminar_activo"):
                st.warning(mongo_crud.eliminar_campo_activo(coleccion_puntos))

    # ====================================================
    # ELIMINAR
    # ====================================================
    with tab4:
        st.subheader("Eliminar datos en MongoDB")

        tipo_delete = st.selectbox(
            "Qué querés eliminar",
            ["Punto verde", "Tipo de residuo", "Muchos puntos verdes", "Muchos residuos"],
            key="mongo_select_delete"
        )

        if tipo_delete == "Punto verde":
            id_punto = st.number_input("ID del punto verde a eliminar", min_value=1, step=1, key="mongo_delete_pv_id")
            if st.button("Eliminar punto verde", key="mongo_btn_delete_pv"):
                st.warning(mongo_crud.eliminar_punto_verde(int(id_punto)))

        elif tipo_delete == "Tipo de residuo":
            id_res = st.text_input("ID del residuo a eliminar", placeholder="R17", key="mongo_delete_res_id")
            if st.button("Eliminar residuo", key="mongo_btn_delete_res"):
                if id_res:
                    st.warning(mongo_crud.eliminar_residuo(id_res.upper()))
                else:
                    st.error("Ingresá un ID de residuo.")

        elif tipo_delete == "Muchos puntos verdes":
            st.info("Ingresá los IDs separados por coma.")
            ids_input = st.text_input("IDs a eliminar", placeholder="1,2,3", key="mongo_delete_muchos_pv_ids")
            if st.button("Eliminar puntos verdes", key="mongo_btn_delete_muchos_pv"):
                if ids_input:
                    try:
                        ids = [int(i.strip()) for i in ids_input.split(",")]
                        st.warning(mongo_crud.eliminar_muchos_puntos_verdes(coleccion_puntos, ids))
                    except ValueError:
                        st.error("Los IDs deben ser números enteros separados por coma.")
                else:
                    st.error("Ingresá al menos un ID.")

        elif tipo_delete == "Muchos residuos":
            st.info("Ingresá los códigos de residuo separados por coma.")
            codigos_input = st.text_input("Códigos a eliminar", placeholder="R1,R2,R3", key="mongo_delete_muchos_res_codigos")
            if st.button("Eliminar residuos", key="mongo_btn_delete_muchos_res"):
                if codigos_input:
                    codigos = [c.strip().upper() for c in codigos_input.split(",")]
                    st.warning(mongo_crud.eliminar_muchos_residuos(coleccion_residuos, coleccion_puntos, codigos))
                else:
                    st.error("Ingresá al menos un código de residuo.")