
import streamlit as st
import neo4j_app.consultas_neo as neo_consultas
import neo4j_app.neo_crud_app as neo_crud


def _capturar_salida(funcion, *args):
    import io, contextlib
    salida = io.StringIO()
    try:
        with contextlib.redirect_stdout(salida):
            funcion(*args)
        texto = salida.getvalue()
        if texto.strip():
            st.code(texto, language="text")
        else:
            st.warning("La operación no devolvió resultados.")
    except Exception as e:
        st.error(f"Error: {e}")


def _ejecutar_consulta(driver, database, funcion):
    try:
        with driver.session(database=database) as session:
            _capturar_salida(funcion, session)
    except Exception as e:
        st.error(f"Error de conexión Neo4j: {e}")


def _buscar_funcion(posibles_nombres):
    for nombre in posibles_nombres:
        if hasattr(neo_consultas, nombre):
            return getattr(neo_consultas, nombre)
    return None


def render(driver, database):
    st.title("🔗 Neo4j")
    st.write("Neo4j modela relaciones entre usuarios, residuos, puntos verdes y recicladores.")

    tab1, tab2, tab3, tab4 = st.tabs(["Consultas", "Crear", "Actualizar", "Eliminar"])

    # ====================================================
    # CONSULTAS
    # ====================================================
    with tab1:
        st.subheader("Consultas Neo4j")

        opcion = st.selectbox(
            "Seleccioná una consulta",
            [
                "Puntos verdes cercanos",
                "Usuarios por barrio",
                "Puntos verdes por comuna",
                "Top 10 usuarios",
                "Usuarios y residuos",
                "Puntos verdes y residuos aceptados",
                "Recicladores y residuos",
                "Recicladores y puntos verdes",
                "Residuos más reciclados",
                "Tipos de residuos por punto verde",
                "Usuarios por nivel",
                "Total de nodos",
                "Total de relaciones"
            ],
            key="neo_select_consulta"
        )

        MAPA = {
            "Puntos verdes cercanos":             ["puntos_verdes_cercanos"],
            "Usuarios por barrio":                ["usuarios_por_barrio"],
            "Puntos verdes por comuna":           ["puntos_verdes_por_comuna"],
            "Top 10 usuarios":                    ["top_usuarios"],
            "Usuarios y residuos":                ["usuarios_y_residuos"],
            "Puntos verdes y residuos aceptados": ["puntos_verdes_y_residuos"],
            "Recicladores y residuos":            ["recicladores_y_residuos"],
            "Recicladores y puntos verdes":       ["recicladores_y_puntos_verdes"],
            "Residuos más reciclados":            ["residuos_mas_reciclados"],
            "Tipos de residuos por punto verde":  ["tipos_residuos_por_punto_verde"],
            "Usuarios por nivel":                 ["usuarios_por_nivel"],
            "Total de nodos":                     ["total_nodos"],
            "Total de relaciones":                ["total_relaciones"],
        }

        if st.button("Ejecutar consulta Neo4j", key="neo_btn_consulta"):
            funcion = _buscar_funcion(MAPA.get(opcion, []))
            if funcion:
                _ejecutar_consulta(driver, database, funcion)
            else:
                st.error(f"No se encontró la función para: {opcion}")

    # ====================================================
    # CREAR
    # ====================================================
    with tab2:
        st.subheader("Crear datos en Neo4j")

        tipo = st.selectbox(
            "Qué querés crear",
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
            key="neo_select_crear"
        )

        if tipo == "Usuario":
            nombre = st.text_input("Nombre", key="neo_crear_nombre")
            email  = st.text_input("Email",  key="neo_crear_email")
            barrio = st.text_input("Barrio", key="neo_crear_barrio")
            comuna = st.text_input("Comuna", placeholder="Comuna 6", key="neo_crear_comuna")
            if st.button("Crear usuario", key="neo_btn_crear_usuario"):
                if all([nombre, email, barrio, comuna]):
                    st.success(neo_crud.crear_usuario(nombre, email, barrio, comuna))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Tipo de Residuo":
            nombre    = st.text_input("Nombre",            key="neo_crear_res_nombre")
            categoria = st.text_input("Categoría",         key="neo_crear_res_cat")
            color     = st.text_input("Color contenedor",  key="neo_crear_res_color")
            if st.button("Crear tipo de residuo", key="neo_btn_crear_residuo"):
                if all([nombre, categoria, color]):
                    st.success(neo_crud.crear_tipo_residuo(nombre, categoria, color))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Punto Verde":
            nombre    = st.text_input("Nombre",    key="neo_crear_pv_nombre")
            direccion = st.text_input("Dirección", key="neo_crear_pv_dir")
            barrio    = st.text_input("Barrio",    key="neo_crear_pv_barrio")
            comuna    = st.text_input("Comuna",    placeholder="Comuna 6", key="neo_crear_pv_comuna")
            if st.button("Crear punto verde", key="neo_btn_crear_pv"):
                if all([nombre, direccion, barrio, comuna]):
                    st.success(neo_crud.crear_punto_verde(nombre, direccion, barrio, comuna))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Reciclador":
            nombre    = st.text_input("Nombre",    key="neo_crear_rec_nombre")
            tipo_rec  = st.selectbox("Tipo", ["Empresa", "Cooperativa", "Independiente"], key="neo_crear_rec_tipo")
            direccion = st.text_input("Dirección", key="neo_crear_rec_dir")
            barrio    = st.text_input("Barrio",    key="neo_crear_rec_barrio")
            comuna    = st.text_input("Comuna",    placeholder="Comuna 6", key="neo_crear_rec_comuna")
            if st.button("Crear reciclador", key="neo_btn_crear_rec"):
                if all([nombre, direccion, barrio, comuna]):
                    st.success(neo_crud.crear_reciclador(nombre, tipo_rec, direccion, barrio, comuna))
                else:
                    st.error("Completá todos los campos.")

        elif tipo == "Relación RECICLA":
            id_u = st.number_input("ID Usuario", min_value=1, step=1, key="neo_recicla_u")
            id_r = st.number_input("ID Residuo", min_value=1, step=1, key="neo_recicla_r")
            if st.button("Crear RECICLA", key="neo_btn_recicla"):
                st.success(neo_crud.crear_relacion_recicla(int(id_u), int(id_r)))

        elif tipo == "Relación ENTREGA_EN":
            id_u = st.number_input("ID Usuario",      min_value=1, step=1, key="neo_entrega_u")
            id_p = st.number_input("ID Punto Verde",  min_value=1, step=1, key="neo_entrega_p")
            if st.button("Crear ENTREGA_EN", key="neo_btn_entrega"):
                st.success(neo_crud.crear_relacion_entrega_en(int(id_u), int(id_p)))

        elif tipo == "Relación ACEPTA":
            id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_acepta_p")
            id_r = st.number_input("ID Residuo",     min_value=1, step=1, key="neo_acepta_r")
            if st.button("Crear ACEPTA", key="neo_btn_acepta"):
                st.success(neo_crud.crear_relacion_acepta(int(id_p), int(id_r)))

        elif tipo == "Relación RECOLECTA":
            id_rc = st.number_input("ID Reciclador", min_value=1, step=1, key="neo_recolecta_rc")
            id_r  = st.number_input("ID Residuo",    min_value=1, step=1, key="neo_recolecta_r")
            if st.button("Crear RECOLECTA", key="neo_btn_recolecta"):
                st.success(neo_crud.crear_relacion_recolecta(int(id_rc), int(id_r)))

        elif tipo == "Relación RETIRA_DE":
            id_rc = st.number_input("ID Reciclador",  min_value=1, step=1, key="neo_retira_rc")
            id_p  = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_retira_p")
            if st.button("Crear RETIRA_DE", key="neo_btn_retira"):
                st.success(neo_crud.crear_relacion_retira_de(int(id_rc), int(id_p)))

        elif tipo == "Relación TIENE_PUNTO_CERCANO":
            id_u = st.number_input("ID Usuario",      min_value=1, step=1, key="neo_cercano_u")
            id_p = st.number_input("ID Punto Verde",  min_value=1, step=1, key="neo_cercano_p")
            if st.button("Crear TIENE_PUNTO_CERCANO", key="neo_btn_cercano"):
                st.success(neo_crud.crear_relacion_punto_cercano(int(id_u), int(id_p)))

    # ====================================================
    # ACTUALIZAR
    # ====================================================
    with tab3:
        st.subheader("Actualizar datos en Neo4j")

        tipo_update = st.selectbox(
            "Qué querés actualizar",
            [
                "Puntos ecológicos de usuario",
                "Tipo de Residuo",
                "Punto Verde",
                "Reciclador",
            ],
            key="neo_select_update"
        )

        if tipo_update == "Puntos ecológicos de usuario":
            id_u   = st.number_input("ID del usuario", min_value=1, step=1, key="neo_update_id")
            puntos = st.number_input("Nuevos puntos ecológicos", min_value=0, step=10, key="neo_update_puntos")
            if st.button("Actualizar puntos", key="neo_btn_update"):
                st.info(neo_crud.actualizar_puntos_usuario(int(id_u), int(puntos)))

        elif tipo_update == "Tipo de Residuo":
            id_r      = st.number_input("ID Residuo",        min_value=1, step=1, key="neo_update_res_id")
            nombre    = st.text_input("Nuevo nombre",         key="neo_update_res_nombre")
            categoria = st.text_input("Nueva categoría",      key="neo_update_res_cat")
            color     = st.text_input("Nuevo color",          key="neo_update_res_color")
            if st.button("Actualizar residuo", key="neo_btn_update_res"):
                if all([nombre, categoria, color]):
                    st.info(neo_crud.modificar_tipo_residuo(int(id_r), nombre, categoria, color))
                else:
                    st.error("Completá todos los campos.")

        elif tipo_update == "Punto Verde":
            id_p      = st.number_input("ID Punto Verde",    min_value=1, step=1, key="neo_update_pv_id")
            nombre    = st.text_input("Nuevo nombre",         key="neo_update_pv_nombre")
            direccion = st.text_input("Nueva dirección",      key="neo_update_pv_dir")
            if st.button("Actualizar punto verde", key="neo_btn_update_pv"):
                if all([nombre, direccion]):
                    st.info(neo_crud.modificar_punto_verde(int(id_p), nombre, direccion))
                else:
                    st.error("Completá todos los campos.")

        elif tipo_update == "Reciclador":
            id_rc    = st.number_input("ID Reciclador",      min_value=1, step=1, key="neo_update_rec_id")
            nombre   = st.text_input("Nuevo nombre",          key="neo_update_rec_nombre")
            tipo_rec = st.selectbox("Nuevo tipo", ["Empresa", "Cooperativa", "Independiente"], key="neo_update_rec_tipo")
            if st.button("Actualizar reciclador", key="neo_btn_update_rec"):
                if nombre:
                    st.info(neo_crud.modificar_reciclador(int(id_rc), nombre, tipo_rec))
                else:
                    st.error("Ingresá el nuevo nombre.")

    # ====================================================
    # ELIMINAR
    # ====================================================
    with tab4:
        st.subheader("Eliminar datos en Neo4j")

        tipo_delete = st.selectbox(
            "Qué querés eliminar",
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
            key="neo_select_delete"
        )

        if tipo_delete == "Usuario":
            id_u = st.number_input("ID Usuario a eliminar", min_value=1, step=1, key="neo_delete_u")
            if st.button("Eliminar usuario", key="neo_btn_delete_u"):
                st.warning(neo_crud.eliminar_usuario(int(id_u)))

        elif tipo_delete == "Tipo de Residuo":
            id_r = st.number_input("ID Residuo a eliminar", min_value=1, step=1, key="neo_delete_res")
            if st.button("Eliminar tipo de residuo", key="neo_btn_delete_res"):
                st.warning(neo_crud.eliminar_tipo_residuo(int(id_r)))

        elif tipo_delete == "Punto Verde":
            id_p = st.number_input("ID Punto Verde a eliminar", min_value=1, step=1, key="neo_delete_pv")
            if st.button("Eliminar punto verde", key="neo_btn_delete_pv"):
                st.warning(neo_crud.eliminar_punto_verde(int(id_p)))

        elif tipo_delete == "Reciclador":
            id_rc = st.number_input("ID Reciclador a eliminar", min_value=1, step=1, key="neo_delete_rec")
            if st.button("Eliminar reciclador", key="neo_btn_delete_rec"):
                st.warning(neo_crud.eliminar_reciclador(int(id_rc)))

        elif tipo_delete == "Relación RECICLA":
            id_u = st.number_input("ID Usuario", min_value=1, step=1, key="neo_delete_rel_u")
            id_r = st.number_input("ID Residuo", min_value=1, step=1, key="neo_delete_rel_r")
            if st.button("Eliminar relación RECICLA", key="neo_btn_delete_recicla"):
                st.warning(neo_crud.eliminar_relacion_recicla(int(id_u), int(id_r)))

        elif tipo_delete == "Relación ENTREGA_EN":
            id_u = st.number_input("ID Usuario",      min_value=1, step=1, key="neo_delete_entrega_u")
            id_p = st.number_input("ID Punto Verde",  min_value=1, step=1, key="neo_delete_entrega_p")
            if st.button("Eliminar relación ENTREGA_EN", key="neo_btn_delete_entrega"):
                st.warning(neo_crud.eliminar_relacion_entrega_en(int(id_u), int(id_p)))

        elif tipo_delete == "Relación ACEPTA":
            id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_delete_acepta_p")
            id_r = st.number_input("ID Residuo",     min_value=1, step=1, key="neo_delete_acepta_r")
            if st.button("Eliminar relación ACEPTA", key="neo_btn_delete_acepta"):
                st.warning(neo_crud.eliminar_relacion_acepta(int(id_p), int(id_r)))

        elif tipo_delete == "Relación RECOLECTA":
            id_rc = st.number_input("ID Reciclador", min_value=1, step=1, key="neo_delete_recolecta_rc")
            id_r  = st.number_input("ID Residuo",    min_value=1, step=1, key="neo_delete_recolecta_r")
            if st.button("Eliminar relación RECOLECTA", key="neo_btn_delete_recolecta"):
                st.warning(neo_crud.eliminar_relacion_recolecta(int(id_rc), int(id_r)))

        elif tipo_delete == "Relación RETIRA_DE":
            id_rc = st.number_input("ID Reciclador",  min_value=1, step=1, key="neo_delete_retira_rc")
            id_p  = st.number_input("ID Punto Verde", min_value=1, step=1, key="neo_delete_retira_p")
            if st.button("Eliminar relación RETIRA_DE", key="neo_btn_delete_retira"):
                st.warning(neo_crud.eliminar_relacion_retira_de(int(id_rc), int(id_p)))

        elif tipo_delete == "Relación TIENE_PUNTO_CERCANO":
            id_u = st.number_input("ID Usuario",      min_value=1, step=1, key="neo_delete_cercano_u")
            id_p = st.number_input("ID Punto Verde",  min_value=1, step=1, key="neo_delete_cercano_p")
            if st.button("Eliminar relación TIENE_PUNTO_CERCANO", key="neo_btn_delete_cercano"):
                st.warning(neo_crud.eliminar_relacion_punto_cercano(int(id_u), int(id_p)))