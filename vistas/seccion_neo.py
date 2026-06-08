import streamlit as st

import neo4j_app.consultas_neo as neo_consultas
import neo4j_app.neo_crud_app as neo_crud


def _neo_exec(driver, database, funcion, capturar_salida):
    try:
        with driver.session(database=database) as session:
            capturar_salida(funcion, session)
    except Exception as e:
        st.error(f"Error Neo4j: {e}")


def render_ciudadano(driver_neo4j, neo4j_database, capturar_salida):
    st.header("Neo4j - Comunidad y relaciones")
    st.caption("Neo4j representa conexiones entre usuarios, puntos verdes, residuos y recicladores.")

    tab_red, tab_comunidad = st.tabs([
        "Relaciones de puntos verdes",
        "Comunidad y gamificación"
    ])

    with tab_red:
        opcion = st.selectbox(
            "Consulta",
            [
                "Puntos verdes cercanos",
                "Puntos verdes por comuna",
                "Puntos verdes y residuos que aceptan",
                "Recicladores y puntos verdes",
            ],
            key="neo_ciu_red_opcion"
        )

        mapa = {
            "Puntos verdes cercanos": "puntos_verdes_cercanos",
            "Puntos verdes por comuna": "puntos_verdes_por_comuna",
            "Puntos verdes y residuos que aceptan": "puntos_verdes_y_residuos",
            "Recicladores y puntos verdes": "recicladores_y_puntos_verdes",
        }

        if st.button("Consultar relación", key="neo_ciu_btn_red"):
            funcion = getattr(neo_consultas, mapa[opcion], None)
            if funcion:
                _neo_exec(driver_neo4j, neo4j_database, funcion, capturar_salida)
            else:
                st.error("Función no encontrada.")

    with tab_comunidad:
        opcion = st.selectbox(
            "Consulta",
            [
                "Top 10 usuarios",
                "Usuarios por nivel",
                "Usuarios y residuos reciclados",
                "Residuos más reciclados",
            ],
            key="neo_ciu_comunidad_opcion"
        )

        mapa = {
            "Top 10 usuarios": "top_usuarios",
            "Usuarios por nivel": "usuarios_por_nivel",
            "Usuarios y residuos reciclados": "usuarios_y_residuos",
            "Residuos más reciclados": "residuos_mas_reciclados",
        }

        if st.button("Consultar comunidad", key="neo_ciu_btn_comunidad"):
            funcion = getattr(neo_consultas, mapa[opcion], None)
            if funcion:
                _neo_exec(driver_neo4j, neo4j_database, funcion, capturar_salida)
            else:
                st.error("Función no encontrada.")


def render_admin():
    st.header("Neo4j - Gestión de nodos y relaciones")
    st.caption("ABM de nodos y relaciones del grafo.")

    operacion = st.selectbox(
        "Operación",
        ["Crear", "Actualizar", "Eliminar"],
        key="neo_admin_operacion"
    )

    if operacion == "Crear":
        tipo = st.selectbox(
            "¿Qué querés crear?",
            [
                "Usuario",
                "Tipo de Residuo",
                "Punto Verde",
                "Reciclador",
                "Relación RECICLA",
                "Relación ENTREGA_EN",
                "Relación ACEPTA",
                "Relación RECOLECTA",
                "Relación RETIRA_DE",
                "Relación TIENE_PUNTO_CERCANO",
            ],
            key="neo_admin_crear_tipo"
        )

        if tipo == "Usuario":
            nombre = st.text_input("Nombre", key="neo_admin_crear_u_nombre")
            email = st.text_input("Email", key="neo_admin_crear_u_email")
            barrio = st.text_input("Barrio", key="neo_admin_crear_u_barrio")
            comuna = st.text_input("Comuna", placeholder="Comuna 6", key="neo_admin_crear_u_comuna")

            if st.button("Crear usuario", key="neo_admin_btn_crear_u"):
                if all([nombre, email, barrio, comuna]):
                    st.success(neo_crud.crear_usuario(nombre, email, barrio, comuna))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Tipo de Residuo":
            nombre = st.text_input("Nombre", key="neo_admin_crear_res_nombre")
            categoria = st.text_input("Categoría", key="neo_admin_crear_res_categoria")
            color = st.text_input("Color contenedor", key="neo_admin_crear_res_color")

            if st.button("Crear tipo de residuo", key="neo_admin_btn_crear_res"):
                if all([nombre, categoria, color]):
                    st.success(neo_crud.crear_tipo_residuo(nombre, categoria, color))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Punto Verde":
            nombre = st.text_input("Nombre", key="neo_admin_crear_pv_nombre")
            direccion = st.text_input("Dirección", key="neo_admin_crear_pv_direccion")
            barrio = st.text_input("Barrio", key="neo_admin_crear_pv_barrio")
            comuna = st.text_input("Comuna", placeholder="Comuna 6", key="neo_admin_crear_pv_comuna")

            if st.button("Crear punto verde", key="neo_admin_btn_crear_pv"):
                if all([nombre, direccion, barrio, comuna]):
                    st.success(neo_crud.crear_punto_verde(nombre, direccion, barrio, comuna))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Reciclador":
            nombre = st.text_input("Nombre", key="neo_admin_crear_rec_nombre")
            tipo_rec = st.selectbox(
                "Tipo",
                ["Empresa", "Cooperativa", "Independiente"],
                key="neo_admin_crear_rec_tipo"
            )
            direccion = st.text_input("Dirección", key="neo_admin_crear_rec_direccion")
            barrio = st.text_input("Barrio", key="neo_admin_crear_rec_barrio")
            comuna = st.text_input("Comuna", placeholder="Comuna 6", key="neo_admin_crear_rec_comuna")

            if st.button("Crear reciclador", key="neo_admin_btn_crear_rec"):
                if all([nombre, direccion, barrio, comuna]):
                    st.success(neo_crud.crear_reciclador(nombre, tipo_rec, direccion, barrio, comuna))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Relación RECICLA":
            id_u = st.number_input("ID Usuario", min_value=1, step=1, key="neo_admin_recicla_u")
            id_r = st.number_input("ID Residuo", min_value=1, step=1, key="neo_admin_recicla_r")

            if st.button("Crear RECICLA", key="neo_admin_btn_recicla"):
                st.success(neo_crud.crear_relacion_recicla(int(id_u), int(id_r)))

        elif tipo == "Relación ENTREGA_EN":
            id_u = st.number_input("ID Usuario", min_value=1, step=1, key="neo_admin_entrega_u")
            id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_admin_entrega_p")

            if st.button("Crear ENTREGA_EN", key="neo_admin_btn_entrega"):
                st.success(neo_crud.crear_relacion_entrega_en(int(id_u), int(id_p)))

        elif tipo == "Relación ACEPTA":
            id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_admin_acepta_p")
            id_r = st.number_input("ID Residuo", min_value=1, step=1, key="neo_admin_acepta_r")

            if st.button("Crear ACEPTA", key="neo_admin_btn_acepta"):
                st.success(neo_crud.crear_relacion_acepta(int(id_p), int(id_r)))

        elif tipo == "Relación RECOLECTA":
            id_rec = st.number_input("ID Reciclador", min_value=1, step=1, key="neo_admin_recolecta_rec")
            id_r = st.number_input("ID Residuo", min_value=1, step=1, key="neo_admin_recolecta_r")

            if st.button("Crear RECOLECTA", key="neo_admin_btn_recolecta"):
                st.success(neo_crud.crear_relacion_recolecta(int(id_rec), int(id_r)))

        elif tipo == "Relación RETIRA_DE":
            id_rec = st.number_input("ID Reciclador", min_value=1, step=1, key="neo_admin_retira_rec")
            id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_admin_retira_p")

            if st.button("Crear RETIRA_DE", key="neo_admin_btn_retira"):
                st.success(neo_crud.crear_relacion_retira_de(int(id_rec), int(id_p)))

        elif tipo == "Relación TIENE_PUNTO_CERCANO":
            id_u = st.number_input("ID Usuario", min_value=1, step=1, key="neo_admin_cercano_u")
            id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_admin_cercano_p")

            if st.button("Crear TIENE_PUNTO_CERCANO", key="neo_admin_btn_cercano"):
                st.success(neo_crud.crear_relacion_punto_cercano(int(id_u), int(id_p)))

    elif operacion == "Actualizar":
        tipo = st.selectbox(
            "¿Qué querés actualizar?",
            ["Puntos ecológicos de usuario", "Tipo de Residuo", "Punto Verde", "Reciclador"],
            key="neo_admin_update_tipo"
        )

        if tipo == "Puntos ecológicos de usuario":
            id_u = st.number_input("ID Usuario", min_value=1, step=1, key="neo_admin_update_u_id")
            puntos = st.number_input(
                "Nuevos puntos ecológicos",
                min_value=0,
                step=10,
                key="neo_admin_update_u_puntos"
            )

            if st.button("Actualizar puntos", key="neo_admin_btn_update_u"):
                st.info(neo_crud.actualizar_puntos_usuario(int(id_u), int(puntos)))

        elif tipo == "Tipo de Residuo":
            id_r = st.number_input("ID Residuo", min_value=1, step=1, key="neo_admin_update_res_id")
            nombre = st.text_input("Nuevo nombre", key="neo_admin_update_res_nombre")
            categoria = st.text_input("Nueva categoría", key="neo_admin_update_res_categoria")
            color = st.text_input("Nuevo color", key="neo_admin_update_res_color")

            if st.button("Actualizar residuo", key="neo_admin_btn_update_res"):
                if all([nombre, categoria, color]):
                    st.info(neo_crud.modificar_tipo_residuo(int(id_r), nombre, categoria, color))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Punto Verde":
            id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_admin_update_pv_id")
            nombre = st.text_input("Nuevo nombre", key="neo_admin_update_pv_nombre")
            direccion = st.text_input("Nueva dirección", key="neo_admin_update_pv_direccion")

            if st.button("Actualizar punto verde", key="neo_admin_btn_update_pv"):
                if all([nombre, direccion]):
                    st.info(neo_crud.modificar_punto_verde(int(id_p), nombre, direccion))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Reciclador":
            id_rec = st.number_input("ID Reciclador", min_value=1, step=1, key="neo_admin_update_rec_id")
            nombre = st.text_input("Nuevo nombre", key="neo_admin_update_rec_nombre")
            tipo_rec = st.selectbox(
                "Nuevo tipo",
                ["Empresa", "Cooperativa", "Independiente"],
                key="neo_admin_update_rec_tipo"
            )

            if st.button("Actualizar reciclador", key="neo_admin_btn_update_rec"):
                if nombre:
                    st.info(neo_crud.modificar_reciclador(int(id_rec), nombre, tipo_rec))
                else:
                    st.error("Ingresá el nuevo nombre.")

    elif operacion == "Eliminar":
        tipo = st.selectbox(
            "¿Qué querés eliminar?",
            [
                "Usuario",
                "Tipo de Residuo",
                "Punto Verde",
                "Reciclador",
                "Relación RECICLA",
                "Relación ENTREGA_EN",
                "Relación ACEPTA",
                "Relación RECOLECTA",
                "Relación RETIRA_DE",
                "Relación TIENE_PUNTO_CERCANO",
            ],
            key="neo_admin_delete_tipo"
        )

        if tipo == "Usuario":
            id_u = st.number_input("ID Usuario", min_value=1, step=1, key="neo_admin_delete_u")
            if st.button("Eliminar usuario", key="neo_admin_btn_delete_u"):
                st.warning(neo_crud.eliminar_usuario(int(id_u)))

        elif tipo == "Tipo de Residuo":
            id_r = st.number_input("ID Residuo", min_value=1, step=1, key="neo_admin_delete_res")
            if st.button("Eliminar tipo de residuo", key="neo_admin_btn_delete_res"):
                st.warning(neo_crud.eliminar_tipo_residuo(int(id_r)))

        elif tipo == "Punto Verde":
            id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_admin_delete_pv")
            if st.button("Eliminar punto verde", key="neo_admin_btn_delete_pv"):
                st.warning(neo_crud.eliminar_punto_verde(int(id_p)))

        elif tipo == "Reciclador":
            id_rec = st.number_input("ID Reciclador", min_value=1, step=1, key="neo_admin_delete_rec")
            if st.button("Eliminar reciclador", key="neo_admin_btn_delete_rec"):
                st.warning(neo_crud.eliminar_reciclador(int(id_rec)))

        elif tipo == "Relación RECICLA":
            id_u = st.number_input("ID Usuario", min_value=1, step=1, key="neo_admin_delete_recicla_u")
            id_r = st.number_input("ID Residuo", min_value=1, step=1, key="neo_admin_delete_recicla_r")
            if st.button("Eliminar RECICLA", key="neo_admin_btn_delete_recicla"):
                st.warning(neo_crud.eliminar_relacion_recicla(int(id_u), int(id_r)))

        elif tipo == "Relación ENTREGA_EN":
            id_u = st.number_input("ID Usuario", min_value=1, step=1, key="neo_admin_delete_entrega_u")
            id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_admin_delete_entrega_p")
            if st.button("Eliminar ENTREGA_EN", key="neo_admin_btn_delete_entrega"):
                st.warning(neo_crud.eliminar_relacion_entrega_en(int(id_u), int(id_p)))

        elif tipo == "Relación ACEPTA":
            id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_admin_delete_acepta_p")
            id_r = st.number_input("ID Residuo", min_value=1, step=1, key="neo_admin_delete_acepta_r")
            if st.button("Eliminar ACEPTA", key="neo_admin_btn_delete_acepta"):
                st.warning(neo_crud.eliminar_relacion_acepta(int(id_p), int(id_r)))

        elif tipo == "Relación RECOLECTA":
            id_rec = st.number_input("ID Reciclador", min_value=1, step=1, key="neo_admin_delete_recolecta_rec")
            id_r = st.number_input("ID Residuo", min_value=1, step=1, key="neo_admin_delete_recolecta_r")
            if st.button("Eliminar RECOLECTA", key="neo_admin_btn_delete_recolecta"):
                st.warning(neo_crud.eliminar_relacion_recolecta(int(id_rec), int(id_r)))

        elif tipo == "Relación RETIRA_DE":
            id_rec = st.number_input("ID Reciclador", min_value=1, step=1, key="neo_admin_delete_retira_rec")
            id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_admin_delete_retira_p")
            if st.button("Eliminar RETIRA_DE", key="neo_admin_btn_delete_retira"):
                st.warning(neo_crud.eliminar_relacion_retira_de(int(id_rec), int(id_p)))

        elif tipo == "Relación TIENE_PUNTO_CERCANO":
            id_u = st.number_input("ID Usuario", min_value=1, step=1, key="neo_admin_delete_cercano_u")
            id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_admin_delete_cercano_p")
            if st.button("Eliminar TIENE_PUNTO_CERCANO", key="neo_admin_btn_delete_cercano"):
                st.warning(neo_crud.eliminar_relacion_punto_cercano(int(id_u), int(id_p)))


def render_dashboard(driver_neo4j, neo4j_database, capturar_salida):
    st.header("Neo4j - Métricas de red")
    st.caption("Consultas analíticas sobre nodos, relaciones y comunidad.")

    consultas = {
        "Usuarios por barrio": "usuarios_por_barrio",
        "Residuos más reciclados": "residuos_mas_reciclados",
        "Top 10 usuarios": "top_usuarios",
        "Usuarios por nivel": "usuarios_por_nivel",
        "Tipos de residuos por punto verde": "tipos_residuos_por_punto_verde",
        "Recicladores y residuos": "recicladores_y_residuos",
        "Total de nodos": "total_nodos",
        "Total de relaciones": "total_relaciones",
    }

    opcion = st.selectbox("Métrica", list(consultas.keys()), key="neo_dashboard_opcion")

    if st.button("Ver métrica Neo4j", key="neo_dashboard_btn"):
        funcion = getattr(neo_consultas, consultas[opcion], None)
        if funcion:
            _neo_exec(driver_neo4j, neo4j_database, funcion, capturar_salida)
        else:
            st.error("Función no encontrada.")