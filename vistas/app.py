
import streamlit as st
import pandas as pd
import io
import contextlib
 
from conexiones import (
    obtener_colecciones_mongo,
    obtener_driver_neo4j,
    NEO4J_DATABASE,
    obtener_cassandra_session
)
 
import redis_app.consultas_redis as redis_consultas
import vistas.seccion_mongo as seccion_mongo
import vistas.seccion_neo as seccion_neo4j
import vistas.seccion_redis as seccion_redis
import vistas.seccion_cassandra as seccion_cassandra
# ============================================================
# CONFIGURACIÓN
# ============================================================
 
st.set_page_config(page_title="SIRA", page_icon="♻️", layout="wide")
 
st.markdown("""
<style>
.block-container { padding-top: 2rem; }
h1, h2, h3 { color: #1B5E20; }
[data-testid="stMetricValue"] { font-size: 24px; }
</style>
""", unsafe_allow_html=True)
 
 
# ============================================================
# CONEXIONES (cacheadas para no reconectar en cada interacción)
# ============================================================
 
@st.cache_resource
def cargar_mongo():
    return obtener_colecciones_mongo()
 
@st.cache_resource
def cargar_neo4j():
    return obtener_driver_neo4j()
 
@st.cache_resource
def cargar_cassandra():
    return obtener_cassandra_session()
 
 
coleccion_puntos, coleccion_residuos = cargar_mongo()
driver_neo4j = cargar_neo4j()
session_cassandra = cargar_cassandra()
 
 
# ============================================================
# FUNCIÓN AUXILIAR (usada por seccion_mongo y análisis general)
# ============================================================
 
def capturar_salida(funcion, *args):
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
        st.error(f"Error al ejecutar la función: {e}")
 
 
# ============================================================
# SIDEBAR
# ============================================================
 
st.sidebar.title("♻️ SIRA")
st.sidebar.caption("Sistema Inteligente de Reciclaje Ambiental")
 
seccion = st.sidebar.radio(
    "Menú principal",
    ["Inicio", "MongoDB", "Neo4j", "Redis", "Cassandra", "Análisis general"],
    key="sidebar_menu"
)
 
 
# ============================================================
# INICIO
# ============================================================
 
if seccion == "Inicio":
    st.title("♻️ SIRA - Sistema Inteligente de Reciclaje Ambiental")
    st.write("""
    Plataforma digital orientada a mejorar la gestión de residuos reciclables,
    integrando distintas bases de datos NoSQL según el tipo de información.
    """)
 
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("MongoDB", "Datos flexibles")
    col2.metric("Neo4j", "Relaciones")
    col3.metric("Redis", "Tiempo real")
    col4.metric("Cassandra", "Históricos")
 
    st.divider()
    st.write("""
    MongoDB almacena datos descriptivos de puntos verdes y residuos.
    Neo4j representa relaciones entre usuarios, residuos, puntos verdes y recicladores.
    Redis administra estados temporales y en tiempo real.
    Cassandra guarda registros históricos de recolecciones y retiros.
    """)
 
 
# ============================================================
# SECCIONES
# ============================================================
 
elif seccion == "MongoDB":
    seccion_mongo.render(coleccion_puntos, coleccion_residuos)
 
elif seccion == "Neo4j":
    seccion_neo4j.render(driver_neo4j, NEO4J_DATABASE)
 
elif seccion == "Redis":
    seccion_redis.render()
 
elif seccion == "Cassandra":
    seccion_cassandra.render(session_cassandra)
 
 
# ============================================================
# ANÁLISIS GENERAL
# ============================================================
 
elif seccion == "Análisis general":
    st.title("📊 Análisis general")
 
    total_puntos = coleccion_puntos.count_documents({})
    total_residuos = coleccion_residuos.count_documents({})
 
    try:
        puntos_disponibles = len(redis_consultas.obtener_puntos_disponibles())
        puntos_saturados = len(redis_consultas.obtener_puntos_saturados())
    except Exception:
        puntos_disponibles = 0
        puntos_saturados = 0
 
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Puntos verdes en MongoDB", total_puntos)
    col2.metric("Tipos de residuos en MongoDB", total_residuos)
    col3.metric("Disponibles en Redis", puntos_disponibles)
    col4.metric("Saturados en Redis", puntos_saturados)
 
    st.divider()
    st.subheader("Análisis desde Neo4j")
 
    import neo4j_app.consultas_neo as neo_consultas
 
    def _ejecutar_neo(nombre_funcion):
        funcion = getattr(neo_consultas, nombre_funcion, None)
        if funcion:
            try:
                with driver_neo4j.session(database=NEO4J_DATABASE) as session:
                    capturar_salida(funcion, session)
            except Exception as e:
                st.error(f"Error Neo4j: {e}")
 
    st.write("Usuarios por barrio:")
    _ejecutar_neo("usuarios_por_barrio")
 
    st.write("Residuos más reciclados:")
    _ejecutar_neo("residuos_mas_reciclados")