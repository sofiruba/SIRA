import streamlit as st

import vistas.seccion_mongo as seccion_mongo
import vistas.seccion_redis as seccion_redis
import vistas.seccion_neo as seccion_neo


def render(
    coleccion_puntos,
    coleccion_residuos,
    driver_neo4j,
    neo4j_database,
    capturar_salida,
):
    st.markdown(
        """
        <div class="app-page-header">
            <div class="app-page-title">Portal del Ciudadano</div>
            <div class="app-page-subtitle">
                Consultá puntos verdes, disponibilidad en tiempo real y relaciones de la comunidad de reciclaje.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    seccion = st.sidebar.radio(
        "Funcionalidades del ciudadano",
        [
            "MongoDB - Buscar puntos verdes y residuos",
            "Redis - Estado en tiempo real",
            "Neo4j - Comunidad y relaciones",
        ],
        key="ciudadano_menu"
    )

    if seccion == "MongoDB - Buscar puntos verdes y residuos":
        st.markdown(
            """
            <div class="app-section-info">
                <strong>MongoDB:</strong> se utiliza para consultar información descriptiva de puntos verdes,
                residuos aceptados, barrios, comunas y horarios.
            </div>
            """,
            unsafe_allow_html=True
        )

        seccion_mongo.render_ciudadano(
            coleccion_puntos=coleccion_puntos,
            coleccion_residuos=coleccion_residuos,
            capturar_salida=capturar_salida
        )

    elif seccion == "Redis - Estado en tiempo real":
        st.markdown(
            """
            <div class="app-section-info">
                <strong>Redis:</strong> se utiliza para consultar estados temporales de los puntos verdes,
                como disponibilidad, saturación, capacidad y ranking.
            </div>
            """,
            unsafe_allow_html=True
        )

        seccion_redis.render_ciudadano()

    elif seccion == "Neo4j - Comunidad y relaciones":
        st.markdown(
            """
            <div class="app-section-info">
                <strong>Neo4j:</strong> se utiliza para representar relaciones entre usuarios, puntos verdes,
                residuos y recicladores.
            </div>
            """,
            unsafe_allow_html=True
        )

        seccion_neo.render_ciudadano(
            driver_neo4j=driver_neo4j,
            neo4j_database=neo4j_database,
            capturar_salida=capturar_salida
        )