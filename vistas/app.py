import os
import io
import contextlib
import streamlit as st
from PIL import Image


# ============================================================
# ENRUTAMIENTO DINÁMICO DE IMÁGENES
# ============================================================
current_dir = os.path.dirname(os.path.abspath(__file__))

# Ruta del Logo para el ícono y la barra lateral
logo_path = os.path.join(current_dir, "..", "imagen", "logo_sira.png")

# ¡NUEVA RUTA! Para el título principal de la página
nombre_sira_path = os.path.join(current_dir, "..", "imagen", "nombre_sira.png")

try:
    logo_img = Image.open(logo_path)
except Exception:
    logo_img = "♻️"
# ============================================================
# CONFIGURACIÓN DE LA PÁGINA (Debe ser lo primero de Streamlit)
# ============================================================
st.set_page_config(page_title="SIRA", page_icon=logo_img, layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 2rem; }
h1, h2, h3 { color: #1B5E20; }
[data-testid="stMetricValue"] { font-size: 24px; }
.sidebar-title { font-size: 1.3rem; font-weight: bold; color: #1B5E20; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# RESTO DE IMPORTS DEL PROYECTO
# ============================================================
from conexiones import (
    obtener_colecciones_mongo,
    obtener_driver_neo4j,
    NEO4J_DATABASE,
    obtener_cassandra_session
)

import vistas.vista_ciudadano as vista_ciudadano
import vistas.vista_administrador as vista_administrador


# ============================================================
# CONEXIONES (cacheadas)
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
# FUNCIÓN AUXILIAR
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
# SIDEBAR — SELECCIÓN DE ROL
# ============================================================

# Usamos la ruta corregida para mostrar el logo en la barra lateral
st.sidebar.image(logo_path, use_container_width=True)   
st.sidebar.markdown("---")

rol = st.sidebar.radio(
    "Seleccioná tu perfil",
    ["🏠 Inicio", "🌿 Ciudadano", "🏭 Administrador"],
    key="sidebar_rol"
)

st.sidebar.markdown("---")
st.sidebar.caption("♻️ SIRA · Sistema Inteligente de Reciclaje Ambiental")


# ============================================================
# INICIO
# ============================================================

if rol == "🏠 Inicio":
    # 🛠️ CAMBIO AQUÍ: Reemplazamos st.title por st.image
    st.image(nombre_sira_path, use_container_width=True)
    
    st.write(
        "Plataforma digital orientada a mejorar la gestión de residuos reciclables "
        "en la Ciudad de Buenos Aires."
    )
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌿 Soy Ciudadano")
        st.write(
            "Encontrá puntos verdes cerca tuyo, conocé su disponibilidad en tiempo real "
            "y participá en la comunidad de reciclaje."
        )
        st.markdown("- 📍 Mapa y búsqueda de puntos verdes")
        st.markdown("- ⚡ Estado y disponibilidad en tiempo real")
        st.markdown("- 🏆 Comunidad y gamificación")

    with col2:
        st.subheader("🏭 Soy Administrador")
        st.write(
            "Gestioná operaciones, monitoreá alertas, analizá estadísticas "
            "y administrá la plataforma completa."
        )
        st.markdown("- 📋 Registro operativo de recolecciones")
        st.markdown("- 🔔 Monitoreo y alertas")
        st.markdown("- 📊 Dashboard estadístico")
        st.markdown("- ⚙️ Gestión de plataforma (ABM)")

    st.divider()

    import redis_app.consultas_redis as redis_consultas

    total_puntos = coleccion_puntos.count_documents({})
    total_residuos = coleccion_residuos.count_documents({})

    try:
        puntos_disponibles = len(redis_consultas.obtener_puntos_disponibles())
        puntos_saturados = len(redis_consultas.obtener_puntos_saturados())
    except Exception:
        puntos_disponibles = 0
        puntos_saturados = 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Puntos Verdes", total_puntos)
    c2.metric("Tipos de Residuos", total_residuos)
    c3.metric("Puntos Disponibles", puntos_disponibles)
    c4.metric("Puntos Saturados", puntos_saturados)


# ============================================================
# ROL: CIUDADANO
# ============================================================

elif rol == "🌿 Ciudadano":
    vista_ciudadano.render(
        coleccion_puntos=coleccion_puntos,
        coleccion_residuos=coleccion_residuos,
        driver_neo4j=driver_neo4j,
        neo4j_database=NEO4J_DATABASE,
        capturar_salida=capturar_salida,
    )


# ============================================================
# ROL: ADMINISTRADOR
# ============================================================

elif rol == "🏭 Administrador":
    vista_administrador.render(
        coleccion_puntos=coleccion_puntos,
        coleccion_residuos=coleccion_residuos,
        driver_neo4j=driver_neo4j,
        neo4j_database=NEO4J_DATABASE,
        session_cassandra=session_cassandra,
        capturar_salida=capturar_salida,
    )