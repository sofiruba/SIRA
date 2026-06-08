"""
vista_administrador.py
======================
Sección del ROL ADMINISTRADOR en SIRA.

Subsecciones:
  1. 📋 Registro Operativo        → Cassandra (CRUD recolecciones)
  2. 🔔 Monitoreo y Alertas       → Redis
  3. 📊 Dashboard Estadístico     → Neo4j + Cassandra
  4. ⚙️  Gestión de Plataforma    → MongoDB CRUD + Neo4j CRUD
"""

import json
import streamlit as st
import pandas as pd

import cassandra_app.consultas_cassandra as cassandra_consultas
import cassandra_app.cassandra_crud_app as cassandra_crud

import redis_app.consultas_redis as redis_consultas
import redis_app.redis_crud_app as redis_crud

import neo4j_app.consultas_neo as neo_consultas
import neo4j_app.neo_crud_app as neo_crud

import mongodb_app.consultas_mongo as mongo
import mongodb_app.mongo_crud_app as mongo_crud


# ─────────────────────────────────────────────
# Helper Neo4j
# ─────────────────────────────────────────────

def _neo_exec(driver, database, funcion, capturar_salida):
    try:
        with driver.session(database=database) as session:
            capturar_salida(funcion, session)
    except Exception as e:
        st.error(f"Error Neo4j: {e}")


# ─────────────────────────────────────────────
# RENDER PRINCIPAL
# ─────────────────────────────────────────────

def render(
    coleccion_puntos,
    coleccion_residuos,
    driver_neo4j,
    neo4j_database,
    session_cassandra,
    capturar_salida,
):
    st.title("🏭 Panel del Administrador")
    st.caption("Gestioná operaciones, monitoreá alertas, analizá métricas y administrá la plataforma.")

    seccion = st.sidebar.radio(
        "Sección",
        [
            "📋 Registro Operativo",
            "🔔 Monitoreo y Alertas",
            "📊 Dashboard Estadístico",
            "⚙️ Gestión de Plataforma",
        ],
        key="admin_menu"
    )

    if seccion == "📋 Registro Operativo":
        _seccion_registro(session_cassandra)

    elif seccion == "🔔 Monitoreo y Alertas":
        _seccion_monitoreo()

    elif seccion == "📊 Dashboard Estadístico":
        _seccion_dashboard(driver_neo4j, neo4j_database, session_cassandra, capturar_salida)

    elif seccion == "⚙️ Gestión de Plataforma":
        _seccion_abm(coleccion_puntos, coleccion_residuos, driver_neo4j, neo4j_database)


# ─────────────────────────────────────────────
# 1. REGISTRO OPERATIVO — Cassandra
# ─────────────────────────────────────────────

def _seccion_registro(session):
    st.header("📋 Registro Operativo")
    st.write("Registrá recolecciones, actualizá datos y consultá historiales.")

    tab_consultas, tab_crear, tab_actualizar, tab_eliminar = st.tabs([
        "Historial y consultas", "Nueva recolección", "Actualizar", "Eliminar"
    ])

    # ── Consultas / Historial ──
    with tab_consultas:
        st.subheader("Historial de recolecciones")

        consulta = st.selectbox(
            "Tipo de búsqueda",
            [
                "Por usuario",
                "Por punto verde",
                "Por reciclador",
                "Por zona (barrio)",
                "Por ID de recolección",
                "Últimas recolecciones de un usuario",
                "Recolecciones con peso > 20 kg (por punto verde)",
            ],
            key="adm_cass_consulta"
        )

        if consulta == "Por usuario":
            usuario_id = st.text_input("ID Usuario", key="adm_cass_c_usuario")
        elif consulta == "Por punto verde":
            punto_verde_id = st.text_input("ID Punto Verde", key="adm_cass_c_pv")
        elif consulta == "Por reciclador":
            reciclador_id = st.text_input("ID Reciclador", key="adm_cass_c_rec")
        elif consulta == "Por zona (barrio)":
            zona = st.text_input("Zona (barrio)", key="adm_cass_c_zona")
        elif consulta == "Por ID de recolección":
            recoleccion_id = st.number_input("ID Recolección", min_value=1, step=1, key="adm_cass_c_id")
        elif consulta == "Últimas recolecciones de un usuario":
            usuario_id = st.text_input("ID Usuario", key="adm_cass_c_ult_u")
            limite = st.number_input("Cantidad", min_value=1, max_value=50, value=5, step=1, key="adm_cass_c_limite")
        elif consulta == "Recolecciones con peso > 20 kg (por punto verde)":
            punto_verde_id = st.text_input("ID Punto Verde", key="adm_cass_c_pv_peso")

        if st.button("Buscar", key="adm_cass_btn_consulta"):
            try:
                datos = None
                if consulta == "Por usuario":
                    datos = cassandra_consultas.consultar_usuario(session, usuario_id)
                elif consulta == "Por punto verde":
                    datos = cassandra_consultas.consultar_punto_verde(session, punto_verde_id)
                elif consulta == "Por reciclador":
                    datos = cassandra_consultas.consultar_reciclador(session, reciclador_id)
                elif consulta == "Por zona (barrio)":
                    datos = cassandra_consultas.consultar_zona(session, zona)
                elif consulta == "Por ID de recolección":
                    row = cassandra_crud.obtener_recoleccion_por_id(int(recoleccion_id))
                    if row:
                        st.dataframe(pd.DataFrame([dict(row._asdict())]))
                    else:
                        st.warning("No se encontró la recolección.")
                    datos = None
                elif consulta == "Últimas recolecciones de un usuario":
                    datos = cassandra_consultas.ultimas_recolecciones_usuario(session, usuario_id, int(limite))
                elif consulta == "Recolecciones con peso > 20 kg (por punto verde)":
                    datos = cassandra_consultas.rango_fechas_punto_verde(session, punto_verde_id)

                if datos is not None:
                    if datos:
                        st.dataframe(pd.DataFrame([dict(r._asdict()) for r in datos]))
                    else:
                        st.warning("No se encontraron registros.")
            except Exception as e:
                st.error(f"Error: {e}")

        st.divider()
        st.subheader("Análisis rápido por usuario")
        usuario_analisis = st.text_input("ID Usuario", value="1", key="adm_cass_analisis_u")
        if st.button("Generar análisis", key="adm_cass_btn_analisis"):
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

    # ── Crear ──
    with tab_crear:
        st.subheader("Registrar nueva recolección")
        recoleccion_id = st.number_input("ID Recolección", min_value=1, step=1, key="adm_cass_crear_id")
        usuario_id     = st.number_input("ID Usuario", min_value=1, step=1, key="adm_cass_crear_u")
        punto_verde_id = st.number_input("ID Punto Verde", min_value=1, step=1, key="adm_cass_crear_pv")
        fecha          = st.text_input("Fecha (YYYY-MM-DD)", key="adm_cass_crear_fecha")
        tipo           = st.text_input("Tipo de Residuo", key="adm_cass_crear_tipo")
        peso           = st.number_input("Peso (kg)", min_value=0.0, step=0.1, key="adm_cass_crear_peso")

        if st.button("Registrar recolección", key="adm_cass_btn_crear"):
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

    # ── Actualizar ──
    with tab_actualizar:
        st.subheader("Actualizar recolección")
        tipo_update    = st.selectbox("Campo a actualizar", ["Peso", "Tipo de residuo"], key="adm_cass_upd_tipo")
        recoleccion_id = st.number_input("ID Recolección", min_value=1, step=1, key="adm_cass_upd_id")

        if tipo_update == "Peso":
            nuevo_peso = st.number_input("Nuevo peso (kg)", min_value=0.0, step=0.1, key="adm_cass_upd_peso")
            if st.button("Actualizar peso", key="adm_cass_btn_upd_peso"):
                try:
                    st.info(cassandra_crud.actualizar_peso_recoleccion(int(recoleccion_id), nuevo_peso))
                except Exception as e:
                    st.error(f"Error: {e}")

        elif tipo_update == "Tipo de residuo":
            nuevo_tipo = st.text_input("Nuevo tipo de residuo", key="adm_cass_upd_tipo_res")
            if st.button("Actualizar tipo", key="adm_cass_btn_upd_tipo"):
                if nuevo_tipo:
                    try:
                        st.info(cassandra_crud.actualizar_tipo_residuo(int(recoleccion_id), nuevo_tipo))
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Ingresá el nuevo tipo.")

    # ── Eliminar ──
    with tab_eliminar:
        st.subheader("Eliminar recolección")
        recoleccion_id = st.number_input("ID Recolección a eliminar", min_value=1, step=1, key="adm_cass_del_id")
        if st.button("Eliminar", key="adm_cass_btn_del"):
            try:
                st.warning(cassandra_crud.eliminar_recoleccion(int(recoleccion_id)))
            except Exception as e:
                st.error(f"Error: {e}")


# ─────────────────────────────────────────────
# 2. MONITOREO Y ALERTAS — Redis
# ─────────────────────────────────────────────

def _seccion_monitoreo():
    st.header("🔔 Monitoreo y Alertas")
    st.write("Panel de control en tiempo real: disponibilidad, saturación y alertas activas.")

    # ── KPIs rápidos ──
    try:
        disponibles = redis_consultas.obtener_puntos_disponibles()
        saturados   = redis_consultas.obtener_puntos_saturados()
        alertas_raw = redis_consultas.obtener_alertas()
    except Exception as e:
        st.error(f"Error cargando datos de Redis: {e}")
        disponibles, saturados, alertas_raw = [], [], []

    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Puntos disponibles", len(disponibles))
    c2.metric("🔴 Puntos saturados", len(saturados))
    c3.metric("🔔 Alertas activas", len(alertas_raw) if alertas_raw else 0)

    st.divider()

    tab_disp, tab_sat, tab_alertas, tab_actualizar, tab_eliminar = st.tabs([
        "Disponibles", "Saturados", "Alertas", "Actualizar estado", "Eliminar"
    ])

    with tab_disp:
        st.subheader("Puntos verdes disponibles")
        if disponibles:
            st.dataframe(pd.DataFrame({"ID Punto Verde": disponibles}), use_container_width=True)
        else:
            st.info("No hay puntos disponibles registrados.")

    with tab_sat:
        st.subheader("Puntos verdes saturados")
        if saturados:
            st.dataframe(pd.DataFrame({"ID Punto Verde": saturados}), use_container_width=True)
        else:
            st.info("No hay puntos saturados registrados.")

    with tab_alertas:
        st.subheader("Alertas recientes")
        if alertas_raw:
            st.dataframe(pd.DataFrame(alertas_raw), use_container_width=True)
        else:
            st.info("No hay alertas activas.")

        st.divider()
        st.subheader("Buscar estado de un punto específico")
        id_punto = st.text_input("ID del punto verde", placeholder="Ej: 1", key="adm_redis_id_estado")
        if st.button("Ver estado", key="adm_redis_btn_estado"):
            if id_punto:
                estado = redis_consultas.obtener_estado_punto_verde(id_punto)
                if estado:
                    st.json(estado)
                else:
                    st.warning("Sin datos para ese punto.")
            else:
                st.error("Ingresá un ID.")

    with tab_actualizar:
        st.subheader("Actualizar estado de un punto verde")
        id_punto    = st.text_input("ID punto verde", placeholder="Ej: 1", key="adm_redis_upd_id")
        nuevo_estado = st.selectbox("Nuevo estado", ["disponible", "saturado"], key="adm_redis_upd_estado")
        capacidad   = st.number_input("Capacidad actual (%)", min_value=0, max_value=100, step=1, key="adm_redis_upd_cap")

        if st.button("Actualizar", key="adm_redis_btn_upd"):
            if id_punto:
                st.success(redis_crud.actualizar_estado_punto(id_punto, nuevo_estado, capacidad))
            else:
                st.error("Ingresá un ID.")

    with tab_eliminar:
        st.subheader("Eliminar datos temporales")
        opcion_del = st.selectbox(
            "Qué querés eliminar",
            ["Estado de un punto verde", "Todas las alertas recientes"],
            key="adm_redis_del_opcion"
        )

        if opcion_del == "Estado de un punto verde":
            id_punto = st.text_input("ID del punto verde", placeholder="Ej: 1", key="adm_redis_del_id")
            if st.button("Eliminar estado", key="adm_redis_btn_del_estado"):
                if id_punto:
                    st.warning(redis_crud.eliminar_estado_punto(id_punto))
                else:
                    st.error("Ingresá un ID.")

        elif opcion_del == "Todas las alertas recientes":
            if st.button("Eliminar todas las alertas", key="adm_redis_btn_del_alertas"):
                st.warning(redis_crud.eliminar_alertas())


# ─────────────────────────────────────────────
# 3. DASHBOARD ESTADÍSTICO — Neo4j + Cassandra
# ─────────────────────────────────────────────

def _seccion_dashboard(driver_neo4j, neo4j_database, session_cassandra, capturar_salida):
    st.header("📊 Dashboard Estadístico")
    st.write("Métricas de actividad, distribución de usuarios y residuos más reciclados.")

    tab_neo, tab_cassandra = st.tabs(["Análisis de red (Neo4j)", "Métricas de actividad (Cassandra)"])

    # ── Neo4j ──
    with tab_neo:
        CONSULTAS_NEO = {
            "Usuarios por barrio": "usuarios_por_barrio",
            "Residuos más reciclados": "residuos_mas_reciclados",
            "Top 10 ciudadanos": "top_usuarios",
            "Usuarios por nivel": "usuarios_por_nivel",
            "Tipos de residuos por punto verde": "tipos_residuos_por_punto_verde",
            "Recicladores y residuos que recolectan": "recicladores_y_residuos",
            "Total de nodos en la red": "total_nodos",
            "Total de relaciones en la red": "total_relaciones",
        }

        opcion_neo = st.selectbox("Métrica", list(CONSULTAS_NEO.keys()), key="adm_dash_neo")

        if st.button("Ver métrica", key="adm_dash_btn_neo"):
            nombre_fn = CONSULTAS_NEO[opcion_neo]
            funcion = getattr(neo_consultas, nombre_fn, None)
            if funcion:
                _neo_exec(driver_neo4j, neo4j_database, funcion, capturar_salida)
            else:
                st.error(f"Función '{nombre_fn}' no encontrada.")

    # ── Cassandra ──
    with tab_cassandra:
        st.subheader("Análisis por usuario (Cassandra)")
        usuario_id = st.text_input("ID Usuario", value="1", key="adm_dash_cass_u")

        if st.button("Analizar usuario", key="adm_dash_btn_cass"):
            try:
                total  = cassandra_consultas.total_kg_usuario(session_cassandra, usuario_id)
                resumen = cassandra_consultas.recolecciones_por_tipo(session_cassandra, usuario_id)

                st.metric("Total reciclado (kg)", round(total, 2))

                if resumen:
                    df = pd.DataFrame(resumen.items(), columns=["Tipo de residuo", "Kg"])
                    st.dataframe(df)
                    st.bar_chart(df.set_index("Tipo de residuo"))
            except Exception as e:
                st.error(f"Error Cassandra: {e}")


# ─────────────────────────────────────────────
# 4. GESTIÓN DE PLATAFORMA (ABM)
# ─────────────────────────────────────────────

def _seccion_abm(coleccion_puntos, coleccion_residuos, driver_neo4j, neo4j_database):
    st.header("⚙️ Gestión de Plataforma")
    st.write("Creá, modificá y eliminá Puntos Verdes, Residuos, Usuarios y Recicladores.")

    tab_mongo, tab_neo = st.tabs(["MongoDB (Puntos Verdes y Residuos)", "Neo4j (Nodos y Relaciones)"])

    # ════════════════════════════════════════
    # ABM MONGODB
    # ════════════════════════════════════════
    with tab_mongo:
        operacion = st.selectbox(
            "Operación",
            ["Crear", "Actualizar", "Eliminar"],
            key="adm_mongo_op"
        )

        # ── CREAR ──
        if operacion == "Crear":
            tipo = st.selectbox(
                "¿Qué querés crear?",
                ["Residuo", "Punto verde", "Muchos puntos verdes (JSON)", "Muchos residuos (JSON)"],
                key="adm_mongo_crear_tipo"
            )

            if tipo == "Residuo":
                nombre    = st.text_input("Nombre del residuo", key="adm_m_c_res_nombre")
                color     = st.text_input("Color del contenedor", key="adm_m_c_res_color")
                categoria = st.text_input("Categoría", key="adm_m_c_res_cat")
                if st.button("Crear residuo", key="adm_m_btn_c_res"):
                    if all([nombre, color, categoria]):
                        st.success(mongo_crud.crear_residuo(nombre, color, categoria))
                    else:
                        st.error("Completá todos los campos.")

            elif tipo == "Punto verde":
                nombre    = st.text_input("Nombre", key="adm_m_c_pv_nombre")
                direccion = st.text_input("Dirección", key="adm_m_c_pv_dir")
                barrio    = st.text_input("Barrio", key="adm_m_c_pv_barrio")
                comuna    = st.text_input("Comuna", placeholder="Comuna 6", key="adm_m_c_pv_comuna")
                residuos  = st.text_input("Residuos aceptados", placeholder="R1,R2,R3", key="adm_m_c_pv_res")
                dias      = st.text_input("Días de atención", placeholder="Lunes,Sábado", key="adm_m_c_pv_dias")
                apertura  = st.text_input("Hora apertura", placeholder="09:00", key="adm_m_c_pv_apertura")
                cierre    = st.text_input("Hora cierre", placeholder="18:00", key="adm_m_c_pv_cierre")
                if st.button("Crear punto verde", key="adm_m_btn_c_pv"):
                    if all([nombre, direccion, barrio, comuna, residuos, dias, apertura, cierre]):
                        lista_res  = [r.strip().upper() for r in residuos.split(",")]
                        lista_dias = [d.strip() for d in dias.split(",")]
                        st.success(mongo_crud.crear_punto_verde(
                            nombre, direccion, barrio, comuna,
                            lista_res, lista_dias, apertura, cierre
                        ))
                    else:
                        st.error("Completá todos los campos.")

            elif tipo == "Muchos puntos verdes (JSON)":
                st.info("Pegá una lista JSON con los puntos verdes.")
                json_pv = st.text_area("JSON", key="adm_m_c_muchos_pv")
                if st.button("Crear puntos verdes", key="adm_m_btn_c_muchos_pv"):
                    if json_pv:
                        try:
                            lista = json.loads(json_pv)
                            if isinstance(lista, list) and lista:
                                st.success(mongo_crud.crear_muchos_puntos_verdes(coleccion_puntos, lista))
                            else:
                                st.error("El JSON debe ser una lista con al menos un elemento.")
                        except json.JSONDecodeError:
                            st.error("JSON inválido.")
                    else:
                        st.error("Ingresá el JSON.")

            elif tipo == "Muchos residuos (JSON)":
                st.info("Pegá una lista JSON con los residuos.")
                json_res = st.text_area("JSON", key="adm_m_c_muchos_res")
                if st.button("Crear residuos", key="adm_m_btn_c_muchos_res"):
                    if json_res:
                        try:
                            lista = json.loads(json_res)
                            if isinstance(lista, list) and lista:
                                st.success(mongo_crud.crear_muchos_residuos(coleccion_residuos, lista))
                            else:
                                st.error("El JSON debe ser una lista con al menos un elemento.")
                        except json.JSONDecodeError:
                            st.error("JSON inválido.")
                    else:
                        st.error("Ingresá el JSON.")

        # ── ACTUALIZAR ──
        elif operacion == "Actualizar":
            tipo_upd = st.selectbox(
                "¿Qué querés actualizar?",
                ["Horario de punto verde", "Tipo de residuo", "Agregar campo activo", "Eliminar campo activo"],
                key="adm_m_upd_tipo"
            )

            if tipo_upd == "Horario de punto verde":
                id_pv    = st.number_input("ID del punto verde", min_value=1, step=1, key="adm_m_upd_pv_id")
                apertura = st.text_input("Nueva hora apertura", placeholder="09:00", key="adm_m_upd_apertura")
                cierre   = st.text_input("Nueva hora cierre", placeholder="18:00", key="adm_m_upd_cierre")
                if st.button("Actualizar horario", key="adm_m_btn_upd_hor"):
                    if apertura and cierre:
                        st.info(mongo_crud.actualizar_horario_punto(int(id_pv), apertura, cierre))
                    else:
                        st.error("Completá apertura y cierre.")

            elif tipo_upd == "Tipo de residuo":
                id_res    = st.text_input("ID del residuo", placeholder="R1", key="adm_m_upd_res_id")
                nombre    = st.text_input("Nuevo nombre", key="adm_m_upd_res_nombre")
                color     = st.text_input("Nuevo color", key="adm_m_upd_res_color")
                categoria = st.text_input("Nueva categoría", key="adm_m_upd_res_cat")
                if st.button("Actualizar residuo", key="adm_m_btn_upd_res"):
                    if all([id_res, nombre, color, categoria]):
                        st.info(mongo_crud.actualizar_residuo(id_res.upper(), nombre, color, categoria))
                    else:
                        st.error("Completá todos los campos.")

            elif tipo_upd == "Agregar campo activo":
                st.write("Agrega `activo: True` a todos los puntos verdes que no lo tengan.")
                if st.button("Agregar campo activo", key="adm_m_btn_add_activo"):
                    st.info(mongo_crud.agregar_campo_activo(coleccion_puntos))

            elif tipo_upd == "Eliminar campo activo":
                st.write("Elimina el campo `activo` de todos los puntos verdes.")
                if st.button("Eliminar campo activo", key="adm_m_btn_del_activo"):
                    st.warning(mongo_crud.eliminar_campo_activo(coleccion_puntos))

        # ── ELIMINAR ──
        elif operacion == "Eliminar":
            tipo_del = st.selectbox(
                "¿Qué querés eliminar?",
                ["Punto verde", "Tipo de residuo", "Muchos puntos verdes", "Muchos residuos"],
                key="adm_m_del_tipo"
            )

            if tipo_del == "Punto verde":
                id_pv = st.number_input("ID del punto verde", min_value=1, step=1, key="adm_m_del_pv_id")
                if st.button("Eliminar", key="adm_m_btn_del_pv"):
                    st.warning(mongo_crud.eliminar_punto_verde(int(id_pv)))

            elif tipo_del == "Tipo de residuo":
                id_res = st.text_input("ID del residuo", placeholder="R17", key="adm_m_del_res_id")
                if st.button("Eliminar", key="adm_m_btn_del_res"):
                    if id_res:
                        st.warning(mongo_crud.eliminar_residuo(id_res.upper()))
                    else:
                        st.error("Ingresá un ID de residuo.")

            elif tipo_del == "Muchos puntos verdes":
                ids_input = st.text_input("IDs separados por coma", placeholder="1,2,3", key="adm_m_del_muchos_pv")
                if st.button("Eliminar puntos verdes", key="adm_m_btn_del_muchos_pv"):
                    if ids_input:
                        try:
                            ids = [int(i.strip()) for i in ids_input.split(",")]
                            st.warning(mongo_crud.eliminar_muchos_puntos_verdes(coleccion_puntos, ids))
                        except ValueError:
                            st.error("Los IDs deben ser enteros separados por coma.")
                    else:
                        st.error("Ingresá al menos un ID.")

            elif tipo_del == "Muchos residuos":
                codigos_input = st.text_input("Códigos separados por coma", placeholder="R1,R2,R3", key="adm_m_del_muchos_res")
                if st.button("Eliminar residuos", key="adm_m_btn_del_muchos_res"):
                    if codigos_input:
                        codigos = [c.strip().upper() for c in codigos_input.split(",")]
                        st.warning(mongo_crud.eliminar_muchos_residuos(coleccion_residuos, coleccion_puntos, codigos))
                    else:
                        st.error("Ingresá al menos un código.")

    # ════════════════════════════════════════
    # ABM NEO4J
    # ════════════════════════════════════════
    with tab_neo:
        operacion_neo = st.selectbox(
            "Operación",
            ["Crear", "Actualizar", "Eliminar"],
            key="adm_neo_op"
        )

        # ── CREAR ──
        if operacion_neo == "Crear":
            tipo = st.selectbox(
                "¿Qué querés crear?",
                [
                    "Usuario", "Tipo de Residuo", "Punto Verde", "Reciclador",
                    "Relación RECICLA", "Relación ENTREGA_EN", "Relación ACEPTA",
                    "Relación RECOLECTA", "Relación RETIRA_DE", "Relación TIENE_PUNTO_CERCANO",
                ],
                key="adm_neo_crear_tipo"
            )

            if tipo == "Usuario":
                nombre = st.text_input("Nombre", key="adm_n_c_u_nombre")
                email  = st.text_input("Email", key="adm_n_c_u_email")
                barrio = st.text_input("Barrio", key="adm_n_c_u_barrio")
                comuna = st.text_input("Comuna", placeholder="Comuna 6", key="adm_n_c_u_comuna")
                if st.button("Crear usuario", key="adm_n_btn_c_u"):
                    if all([nombre, email, barrio, comuna]):
                        st.success(neo_crud.crear_usuario(nombre, email, barrio, comuna))
                    else:
                        st.error("Completá todos los campos.")

            elif tipo == "Tipo de Residuo":
                nombre    = st.text_input("Nombre", key="adm_n_c_res_nombre")
                categoria = st.text_input("Categoría", key="adm_n_c_res_cat")
                color     = st.text_input("Color contenedor", key="adm_n_c_res_color")
                if st.button("Crear tipo de residuo", key="adm_n_btn_c_res"):
                    if all([nombre, categoria, color]):
                        st.success(neo_crud.crear_tipo_residuo(nombre, categoria, color))
                    else:
                        st.error("Completá todos los campos.")

            elif tipo == "Punto Verde":
                nombre    = st.text_input("Nombre", key="adm_n_c_pv_nombre")
                direccion = st.text_input("Dirección", key="adm_n_c_pv_dir")
                barrio    = st.text_input("Barrio", key="adm_n_c_pv_barrio")
                comuna    = st.text_input("Comuna", placeholder="Comuna 6", key="adm_n_c_pv_comuna")
                if st.button("Crear punto verde", key="adm_n_btn_c_pv"):
                    if all([nombre, direccion, barrio, comuna]):
                        st.success(neo_crud.crear_punto_verde(nombre, direccion, barrio, comuna))
                    else:
                        st.error("Completá todos los campos.")

            elif tipo == "Reciclador":
                nombre    = st.text_input("Nombre", key="adm_n_c_rec_nombre")
                tipo_rec  = st.selectbox("Tipo", ["Empresa", "Cooperativa", "Independiente"], key="adm_n_c_rec_tipo")
                direccion = st.text_input("Dirección", key="adm_n_c_rec_dir")
                barrio    = st.text_input("Barrio", key="adm_n_c_rec_barrio")
                comuna    = st.text_input("Comuna", placeholder="Comuna 6", key="adm_n_c_rec_comuna")
                if st.button("Crear reciclador", key="adm_n_btn_c_rec"):
                    if all([nombre, direccion, barrio, comuna]):
                        st.success(neo_crud.crear_reciclador(nombre, tipo_rec, direccion, barrio, comuna))
                    else:
                        st.error("Completá todos los campos.")

            elif tipo == "Relación RECICLA":
                id_u = st.number_input("ID Usuario", min_value=1, step=1, key="adm_n_c_rec_u")
                id_r = st.number_input("ID Residuo", min_value=1, step=1, key="adm_n_c_rec_r")
                if st.button("Crear RECICLA", key="adm_n_btn_recicla"):
                    st.success(neo_crud.crear_relacion_recicla(int(id_u), int(id_r)))

            elif tipo == "Relación ENTREGA_EN":
                id_u = st.number_input("ID Usuario", min_value=1, step=1, key="adm_n_c_ent_u")
                id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="adm_n_c_ent_p")
                if st.button("Crear ENTREGA_EN", key="adm_n_btn_entrega"):
                    st.success(neo_crud.crear_relacion_entrega_en(int(id_u), int(id_p)))

            elif tipo == "Relación ACEPTA":
                id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="adm_n_c_ace_p")
                id_r = st.number_input("ID Residuo", min_value=1, step=1, key="adm_n_c_ace_r")
                if st.button("Crear ACEPTA", key="adm_n_btn_acepta"):
                    st.success(neo_crud.crear_relacion_acepta(int(id_p), int(id_r)))

            elif tipo == "Relación RECOLECTA":
                id_rc = st.number_input("ID Reciclador", min_value=1, step=1, key="adm_n_c_rcol_rc")
                id_r  = st.number_input("ID Residuo", min_value=1, step=1, key="adm_n_c_rcol_r")
                if st.button("Crear RECOLECTA", key="adm_n_btn_recolecta"):
                    st.success(neo_crud.crear_relacion_recolecta(int(id_rc), int(id_r)))

            elif tipo == "Relación RETIRA_DE":
                id_rc = st.number_input("ID Reciclador", min_value=1, step=1, key="adm_n_c_ret_rc")
                id_p  = st.number_input("ID Punto Verde", min_value=1, step=1, key="adm_n_c_ret_p")
                if st.button("Crear RETIRA_DE", key="adm_n_btn_retira"):
                    st.success(neo_crud.crear_relacion_retira_de(int(id_rc), int(id_p)))

            elif tipo == "Relación TIENE_PUNTO_CERCANO":
                id_u = st.number_input("ID Usuario", min_value=1, step=1, key="adm_n_c_cerc_u")
                id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="adm_n_c_cerc_p")
                if st.button("Crear TIENE_PUNTO_CERCANO", key="adm_n_btn_cercano"):
                    st.success(neo_crud.crear_relacion_punto_cercano(int(id_u), int(id_p)))

        # ── ACTUALIZAR ──
        elif operacion_neo == "Actualizar":
            tipo_upd = st.selectbox(
                "¿Qué querés actualizar?",
                ["Puntos ecológicos de usuario", "Tipo de Residuo", "Punto Verde", "Reciclador"],
                key="adm_neo_upd_tipo"
            )

            if tipo_upd == "Puntos ecológicos de usuario":
                id_u   = st.number_input("ID del usuario", min_value=1, step=1, key="adm_n_upd_u_id")
                puntos = st.number_input("Nuevos puntos ecológicos", min_value=0, step=10, key="adm_n_upd_u_puntos")
                if st.button("Actualizar puntos", key="adm_n_btn_upd_u"):
                    st.info(neo_crud.actualizar_puntos_usuario(int(id_u), int(puntos)))

            elif tipo_upd == "Tipo de Residuo":
                id_r      = st.number_input("ID Residuo", min_value=1, step=1, key="adm_n_upd_res_id")
                nombre    = st.text_input("Nuevo nombre", key="adm_n_upd_res_nombre")
                categoria = st.text_input("Nueva categoría", key="adm_n_upd_res_cat")
                color     = st.text_input("Nuevo color", key="adm_n_upd_res_color")
                if st.button("Actualizar residuo", key="adm_n_btn_upd_res"):
                    if all([nombre, categoria, color]):
                        st.info(neo_crud.modificar_tipo_residuo(int(id_r), nombre, categoria, color))
                    else:
                        st.error("Completá todos los campos.")

            elif tipo_upd == "Punto Verde":
                id_p      = st.number_input("ID Punto Verde", min_value=1, step=1, key="adm_n_upd_pv_id")
                nombre    = st.text_input("Nuevo nombre", key="adm_n_upd_pv_nombre")
                direccion = st.text_input("Nueva dirección", key="adm_n_upd_pv_dir")
                if st.button("Actualizar punto verde", key="adm_n_btn_upd_pv"):
                    if all([nombre, direccion]):
                        st.info(neo_crud.modificar_punto_verde(int(id_p), nombre, direccion))
                    else:
                        st.error("Completá todos los campos.")

            elif tipo_upd == "Reciclador":
                id_rc    = st.number_input("ID Reciclador", min_value=1, step=1, key="adm_n_upd_rec_id")
                nombre   = st.text_input("Nuevo nombre", key="adm_n_upd_rec_nombre")
                tipo_rec = st.selectbox("Nuevo tipo", ["Empresa", "Cooperativa", "Independiente"], key="adm_n_upd_rec_tipo")
                if st.button("Actualizar reciclador", key="adm_n_btn_upd_rec"):
                    if nombre:
                        st.info(neo_crud.modificar_reciclador(int(id_rc), nombre, tipo_rec))
                    else:
                        st.error("Ingresá el nuevo nombre.")

        # ── ELIMINAR ──
        elif operacion_neo == "Eliminar":
            tipo_del = st.selectbox(
                "¿Qué querés eliminar?",
                [
                    "Usuario", "Tipo de Residuo", "Punto Verde", "Reciclador",
                    "Relación RECICLA", "Relación ENTREGA_EN", "Relación ACEPTA",
                    "Relación RECOLECTA", "Relación RETIRA_DE", "Relación TIENE_PUNTO_CERCANO",
                ],
                key="adm_neo_del_tipo"
            )

            if tipo_del == "Usuario":
                id_u = st.number_input("ID Usuario", min_value=1, step=1, key="adm_n_del_u")
                if st.button("Eliminar usuario", key="adm_n_btn_del_u"):
                    st.warning(neo_crud.eliminar_usuario(int(id_u)))

            elif tipo_del == "Tipo de Residuo":
                id_r = st.number_input("ID Residuo", min_value=1, step=1, key="adm_n_del_res")
                if st.button("Eliminar tipo de residuo", key="adm_n_btn_del_res"):
                    st.warning(neo_crud.eliminar_tipo_residuo(int(id_r)))

            elif tipo_del == "Punto Verde":
                id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="adm_n_del_pv")
                if st.button("Eliminar punto verde", key="adm_n_btn_del_pv"):
                    st.warning(neo_crud.eliminar_punto_verde(int(id_p)))

            elif tipo_del == "Reciclador":
                id_rc = st.number_input("ID Reciclador", min_value=1, step=1, key="adm_n_del_rec")
                if st.button("Eliminar reciclador", key="adm_n_btn_del_rec"):
                    st.warning(neo_crud.eliminar_reciclador(int(id_rc)))

            elif tipo_del == "Relación RECICLA":
                id_u = st.number_input("ID Usuario", min_value=1, step=1, key="adm_n_del_rel_u")
                id_r = st.number_input("ID Residuo", min_value=1, step=1, key="adm_n_del_rel_r")
                if st.button("Eliminar RECICLA", key="adm_n_btn_del_recicla"):
                    st.warning(neo_crud.eliminar_relacion_recicla(int(id_u), int(id_r)))

            elif tipo_del == "Relación ENTREGA_EN":
                id_u = st.number_input("ID Usuario", min_value=1, step=1, key="adm_n_del_ent_u")
                id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="adm_n_del_ent_p")
                if st.button("Eliminar ENTREGA_EN", key="adm_n_btn_del_entrega"):
                    st.warning(neo_crud.eliminar_relacion_entrega_en(int(id_u), int(id_p)))

            elif tipo_del == "Relación ACEPTA":
                id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="adm_n_del_ace_p")
                id_r = st.number_input("ID Residuo", min_value=1, step=1, key="adm_n_del_ace_r")
                if st.button("Eliminar ACEPTA", key="adm_n_btn_del_acepta"):
                    st.warning(neo_crud.eliminar_relacion_acepta(int(id_p), int(id_r)))

            elif tipo_del == "Relación RECOLECTA":
                id_rc = st.number_input("ID Reciclador", min_value=1, step=1, key="adm_n_del_rcol_rc")
                id_r  = st.number_input("ID Residuo", min_value=1, step=1, key="adm_n_del_rcol_r")
                if st.button("Eliminar RECOLECTA", key="adm_n_btn_del_recolecta"):
                    st.warning(neo_crud.eliminar_relacion_recolecta(int(id_rc), int(id_r)))

            elif tipo_del == "Relación RETIRA_DE":
                id_rc = st.number_input("ID Reciclador", min_value=1, step=1, key="adm_n_del_ret_rc")
                id_p  = st.number_input("ID Punto Verde", min_value=1, step=1, key="adm_n_del_ret_p")
                if st.button("Eliminar RETIRA_DE", key="adm_n_btn_del_retira"):
                    st.warning(neo_crud.eliminar_relacion_retira_de(int(id_rc), int(id_p)))

            elif tipo_del == "Relación TIENE_PUNTO_CERCANO":
                id_u = st.number_input("ID Usuario", min_value=1, step=1, key="adm_n_del_cerc_u")
                id_p = st.number_input("ID Punto Verde", min_value=1, step=1, key="adm_n_del_cerc_p")
                if st.button("Eliminar TIENE_PUNTO_CERCANO", key="adm_n_btn_del_cercano"):
                    st.warning(neo_crud.eliminar_relacion_punto_cercano(int(id_u), int(id_p)))