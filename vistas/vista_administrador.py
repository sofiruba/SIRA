import streamlit as st

import vistas.seccion_mongo as seccion_mongo
import vistas.seccion_neo as seccion_neo
import vistas.seccion_redis as seccion_redis
import vistas.seccion_cassandra as seccion_cassandra


def render(
    coleccion_puntos,
    coleccion_residuos,
    driver_neo4j,
    neo4j_database,
    session_cassandra,
    capturar_salida,
):
    st.markdown(
        """
        <div class="app-page-header">
            <div class="app-page-title">Panel del Administrador</div>
            <div class="app-page-subtitle">
                Gestión técnica de la plataforma SIRA: datos, relaciones, estados en tiempo real e históricos.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    seccion = st.sidebar.radio(
        "Base de datos / módulo",
        [
            "MongoDB - Gestión de puntos verdes y residuos",
            "Neo4j - Gestión de nodos y relaciones",
            "Redis - Monitoreo en tiempo real",
            "Cassandra - Registro histórico",
            "Dashboard técnico",
        ],
        key="admin_menu"
    )

    if seccion == "MongoDB - Gestión de puntos verdes y residuos":
        st.markdown(
            """
            <div class="app-section-info">
                <strong>MongoDB:</strong> gestión de documentos flexibles asociados a puntos verdes,
                residuos, horarios, barrios y comunas.
            </div>
            """,
            unsafe_allow_html=True
        )

        seccion_mongo.render_admin(
            coleccion_puntos=coleccion_puntos,
            coleccion_residuos=coleccion_residuos
        )

    elif seccion == "Neo4j - Gestión de nodos y relaciones":
        st.markdown(
            """
            <div class="app-section-info">
                <strong>Neo4j:</strong> administración de nodos y relaciones del grafo:
                usuarios, puntos verdes, residuos y recicladores.
            </div>
            """,
            unsafe_allow_html=True
        )

        seccion_neo.render_admin()

    elif seccion == "Redis - Monitoreo en tiempo real":
        st.markdown(
            """
            <div class="app-section-info">
                <strong>Redis:</strong> monitoreo de disponibilidad, saturación, capacidad,
                ranking y alertas temporales.
            </div>
            """,
            unsafe_allow_html=True
        )

        seccion_redis.render_admin()

    elif seccion == "Cassandra - Registro histórico":
        st.markdown(
            """
            <div class="app-section-info">
                <strong>Cassandra:</strong> registro histórico de recolecciones y consultas modeladas por acceso,
                como historial por usuario, punto verde, zona o reciclador.
            </div>
            """,
            unsafe_allow_html=True
        )

        seccion_cassandra.render_admin(session_cassandra)

    elif seccion == "Dashboard técnico":
        st.markdown(
            """
            <div class="app-section-info">
                <strong>Dashboard técnico:</strong> resumen de métricas obtenidas desde las distintas bases
                de datos del sistema.
            </div>
            """,
            unsafe_allow_html=True
        )

        tab_neo, tab_cassandra, tab_redis, tab_mongo = st.tabs([
            "Neo4j",
            "Cassandra",
            "Redis",
            "MongoDB"
        ])

        with tab_neo:
            seccion_neo.render_dashboard(
                driver_neo4j=driver_neo4j,
                neo4j_database=neo4j_database,
                capturar_salida=capturar_salida
            )

        with tab_cassandra:
            seccion_cassandra.render_dashboard(session_cassandra)

        with tab_redis:
            seccion_redis.render_dashboard()

        with tab_mongo:
            seccion_mongo.render_dashboard(
                coleccion_puntos=coleccion_puntos,
                coleccion_residuos=coleccion_residuos
            )