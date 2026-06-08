"""
vista_ciudadano.py
==================
Sección del ROL CIUDADANO en SIRA.

Subsecciones:
  1. 📍 Mapa / Búsqueda de Puntos Verdes   → MongoDB + Neo4j
  2. ⚡ Estado en Tiempo Real               → Redis
  3. 🏆 Comunidad y Gamificación           → Neo4j + Redis
"""

import streamlit as st
import pandas as pd

import mongodb_app.consultas_mongo as mongo
import mongodb_app.mongo_crud_app as mongo_crud
import redis_app.consultas_redis as redis_consultas
import neo4j_app.consultas_neo as neo_consultas


# ─────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────

def _neo_exec(driver, database, funcion, capturar_salida):
    """Ejecuta una función Neo4j dentro de una sesión."""
    try:
        with driver.session(database=database) as session:
            capturar_salida(funcion, session)
    except Exception as e:
        st.error(f"Error Neo4j: {e}")


# ─────────────────────────────────────────────
# RENDER PRINCIPAL
# ─────────────────────────────────────────────

def render(coleccion_puntos, coleccion_residuos, driver_neo4j, neo4j_database, capturar_salida):
    st.title("🌿 Portal del Ciudadano")
    st.caption("Encontrá puntos verdes, revisá disponibilidad y participá en la comunidad.")

    seccion = st.sidebar.radio(
        "¿Qué querés hacer?",
        [
            "📍 Buscar Puntos Verdes",
            "⚡ Estado en Tiempo Real",
            "🏆 Comunidad y Gamificación",
        ],
        key="ciudadano_menu"
    )

    if seccion == "📍 Buscar Puntos Verdes":
        _seccion_mapa(coleccion_puntos, coleccion_residuos, driver_neo4j, neo4j_database, capturar_salida)

    elif seccion == "⚡ Estado en Tiempo Real":
        _seccion_tiempo_real()

    elif seccion == "🏆 Comunidad y Gamificación":
        _seccion_comunidad(driver_neo4j, neo4j_database, capturar_salida)


# ─────────────────────────────────────────────
# 1. BÚSQUEDA DE PUNTOS VERDES
# ─────────────────────────────────────────────

def _seccion_mapa(coleccion_puntos, coleccion_residuos, driver_neo4j, neo4j_database, capturar_salida):
    st.header("📍 Búsqueda de Puntos Verdes")
    st.write("Encontrá el punto verde más conveniente según tu barrio, horario o el tipo de residuo que querés reciclar.")

    tab_barrio, tab_residuo, tab_horario, tab_neo = st.tabs([
        "Por barrio",
        "Por tipo de residuo",
        "Por horario / día",
        "Consultas de red",
    ])

    # ── Por barrio ──
    with tab_barrio:
        st.subheader("Buscar por barrio")
        barrio = st.text_input("Ingresá el nombre del barrio", key="ciu_barrio")
        if st.button("Buscar", key="ciu_btn_barrio"):
            if barrio:
                resultados = mongo_crud.buscar_punto_verde_por_barrio(coleccion_puntos, barrio)
                if resultados:
                    for r in resultados:
                        st.json(r)
                else:
                    st.warning("No se encontraron puntos verdes en ese barrio.")
            else:
                st.error("Ingresá un barrio.")

        st.divider()
        st.subheader("Buscar por ID")
        id_pv = st.number_input("ID del punto verde", min_value=1, step=1, key="ciu_id_pv")
        if st.button("Buscar por ID", key="ciu_btn_id"):
            punto = mongo_crud.buscar_punto_verde_por_id(int(id_pv))
            if punto:
                st.json(punto)
            else:
                st.warning("No se encontró un punto verde con ese ID.")

    # ── Por tipo de residuo ──
    with tab_residuo:
        st.subheader("¿Qué residuo querés reciclar?")

        opcion_res = st.selectbox(
            "Tipo de búsqueda",
            [
                "Buscar residuo por nombre",
                "Puntos verdes que aceptan RAEEs (electrónicos)",
                "Botellas de Amor y Cápsulas de Café",
                "Residuos reciclables",
                "Residuos de tratamiento especial",
                "Residuos del contenedor amarillo",
                "Residuos reutilizables u orgánicos",
            ],
            key="ciu_select_residuo"
        )

        if opcion_res == "Buscar residuo por nombre":
            nombre_res = st.text_input("Nombre del residuo", key="ciu_nombre_res")

        if st.button("Buscar", key="ciu_btn_residuo"):
            if opcion_res == "Buscar residuo por nombre":
                if nombre_res:
                    resultados = mongo_crud.buscar_residuo_por_nombre(coleccion_residuos, nombre_res)
                    if resultados:
                        for r in resultados:
                            st.json(r)
                    else:
                        st.warning("No se encontraron residuos con ese nombre.")
                else:
                    st.error("Ingresá un nombre.")
            elif opcion_res == "Puntos verdes que aceptan RAEEs (electrónicos)":
                capturar_salida(mongo.consulta1, coleccion_puntos)
            elif opcion_res == "Botellas de Amor y Cápsulas de Café":
                capturar_salida(mongo.consulta3, coleccion_puntos)
            elif opcion_res == "Residuos reciclables":
                capturar_salida(mongo.consulta6, coleccion_residuos)
            elif opcion_res == "Residuos de tratamiento especial":
                capturar_salida(mongo.consulta7, coleccion_residuos)
            elif opcion_res == "Residuos del contenedor amarillo":
                capturar_salida(mongo.consulta8, coleccion_residuos)
            elif opcion_res == "Residuos reutilizables u orgánicos":
                capturar_salida(mongo.consulta9, coleccion_residuos)

    # ── Por horario / día ──
    with tab_horario:
        st.subheader("Puntos verdes según horario o zona")

        opcion_hor = st.selectbox(
            "Filtro",
            [
                "Abiertos los sábados",
                "En Villa Lugano",
                "En comunas 7 y 8",
            ],
            key="ciu_select_horario"
        )

        if st.button("Buscar", key="ciu_btn_horario"):
            if opcion_hor == "Abiertos los sábados":
                capturar_salida(mongo.consulta2, coleccion_puntos)
            elif opcion_hor == "En Villa Lugano":
                capturar_salida(mongo.consulta4, coleccion_puntos)
            elif opcion_hor == "En comunas 7 y 8":
                capturar_salida(mongo.consulta5, coleccion_puntos)

    # ── Consultas de red (Neo4j) ──
    with tab_neo:
        st.subheader("Puntos verdes y conexiones (Neo4j)")

        opcion_neo = st.selectbox(
            "Consulta",
            [
                "Puntos verdes cercanos a mí",
                "Puntos verdes por comuna",
                "Puntos verdes y residuos que aceptan",
                "Recicladores y puntos verdes",
            ],
            key="ciu_select_neo"
        )

        MAPA_NEO = {
            "Puntos verdes cercanos a mí": "puntos_verdes_cercanos",
            "Puntos verdes por comuna": "puntos_verdes_por_comuna",
            "Puntos verdes y residuos que aceptan": "puntos_verdes_y_residuos",
            "Recicladores y puntos verdes": "recicladores_y_puntos_verdes",
        }

        if st.button("Consultar", key="ciu_btn_neo"):
            nombre_fn = MAPA_NEO.get(opcion_neo)
            funcion = getattr(neo_consultas, nombre_fn, None)
            if funcion:
                _neo_exec(driver_neo4j, neo4j_database, funcion, capturar_salida)
            else:
                st.error(f"Función no encontrada: {nombre_fn}")


# ─────────────────────────────────────────────
# 2. ESTADO EN TIEMPO REAL (Redis)
# ─────────────────────────────────────────────

def _seccion_tiempo_real():
    st.header("⚡ Estado en Tiempo Real")
    st.write("Consultá la disponibilidad y saturación de los puntos verdes antes de ir.")

    col_disp, col_sat = st.columns(2)

    with col_disp:
        st.subheader("✅ Puntos disponibles")
        if st.button("Ver disponibles", key="ciu_rt_disponibles"):
            datos = redis_consultas.obtener_puntos_disponibles()
            if datos:
                st.dataframe(
                    pd.DataFrame({"Punto Verde (disponible)": datos}),
                    use_container_width=True
                )
            else:
                st.info("No hay puntos marcados como disponibles.")

    with col_sat:
        st.subheader("🔴 Puntos saturados")
        if st.button("Ver saturados", key="ciu_rt_saturados"):
            datos = redis_consultas.obtener_puntos_saturados()
            if datos:
                st.dataframe(
                    pd.DataFrame({"Punto Verde (saturado)": datos}),
                    use_container_width=True
                )
            else:
                st.info("No hay puntos marcados como saturados.")

    st.divider()
    st.subheader("🔍 Consultá el estado de un punto verde específico")
    id_punto = st.text_input("ID del punto verde", placeholder="Ej: 1", key="ciu_rt_id")
    if st.button("Ver estado", key="ciu_rt_btn_estado"):
        if id_punto:
            estado = redis_consultas.obtener_estado_punto_verde(id_punto)
            if estado:
                st.json(estado)
            else:
                st.warning("No se encontró estado para ese punto verde.")
        else:
            st.error("Ingresá un ID.")

    st.divider()
    st.subheader("📊 Ranking de puntos verdes por uso")
    if st.button("Ver ranking", key="ciu_rt_ranking"):
        ranking = redis_consultas.obtener_ranking()
        datos = [{"id_punto_verde": item[0], "puntaje": item[1]} for item in ranking]
        if datos:
            df = pd.DataFrame(datos)
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("id_punto_verde"))
        else:
            st.info("No hay datos de ranking cargados.")


# ─────────────────────────────────────────────
# 3. COMUNIDAD Y GAMIFICACIÓN (Neo4j + Redis)
# ─────────────────────────────────────────────

def _seccion_comunidad(driver_neo4j, neo4j_database, capturar_salida):
    st.header("🏆 Comunidad y Gamificación")
    st.write("Conocé a los ciudadanos más comprometidos y tu posición en el ranking de reciclaje.")

    tab_top, tab_nivel, tab_actividad = st.tabs([
        "🥇 Top 10 ciudadanos",
        "📶 Usuarios por nivel",
        "🔄 Mi actividad",
    ])

    # ── Top 10 ──
    with tab_top:
        st.subheader("Top 10 ciudadanos más comprometidos")
        st.info("Ranking basado en puntos ecológicos acumulados (Neo4j).")
        if st.button("Ver Top 10", key="ciu_com_top10"):
            funcion = getattr(neo_consultas, "top_usuarios", None)
            if funcion:
                _neo_exec(driver_neo4j, neo4j_database, funcion, capturar_salida)
            else:
                st.error("Función 'top_usuarios' no encontrada en neo_consultas.")

    # ── Por nivel ──
    with tab_nivel:
        st.subheader("Distribución de usuarios por nivel")
        if st.button("Ver niveles", key="ciu_com_nivel"):
            funcion = getattr(neo_consultas, "usuarios_por_nivel", None)
            if funcion:
                _neo_exec(driver_neo4j, neo4j_database, funcion, capturar_salida)
            else:
                st.error("Función 'usuarios_por_nivel' no encontrada.")

    # ── Mi actividad ──
    with tab_actividad:
        st.subheader("¿Qué residuos reciclé?")
        st.info("Consultá tus hábitos de reciclaje a partir de las relaciones en Neo4j.")

        opcion = st.selectbox(
            "Ver",
            ["Usuarios y sus residuos reciclados", "Residuos más reciclados en la comunidad"],
            key="ciu_com_actividad"
        )

        if st.button("Consultar", key="ciu_com_btn_actividad"):
            if opcion == "Usuarios y sus residuos reciclados":
                funcion = getattr(neo_consultas, "usuarios_y_residuos", None)
            else:
                funcion = getattr(neo_consultas, "residuos_mas_reciclados", None)

            if funcion:
                _neo_exec(driver_neo4j, neo4j_database, funcion, capturar_salida)
            else:
                st.error("Función no encontrada.")