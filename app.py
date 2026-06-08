import os
import io
import base64
import contextlib
import streamlit as st
from PIL import Image

current_dir = os.path.dirname(os.path.abspath(__file__))

possible_image_dirs = [
    os.path.join(current_dir, "imagen"),
    os.path.join(os.path.dirname(current_dir), "imagen"),
]

image_dir = None

for path in possible_image_dirs:
    if os.path.exists(path):
        image_dir = path
        break

if image_dir is None:
    image_dir = os.path.join(current_dir, "imagen")

logo_path = os.path.join(image_dir, "logo_sira.png")
nombre_sira_path = os.path.join(image_dir, "nombre_sira.png")


def cargar_imagen(path):
    try:
        return Image.open(path)
    except Exception:
        return None


def imagen_base64(path):
    try:
        with open(path, "rb") as archivo:
            return base64.b64encode(archivo.read()).decode()
    except Exception:
        return None


logo_img = cargar_imagen(logo_path)
logo_b64 = imagen_base64(logo_path)
nombre_b64 = imagen_base64(nombre_sira_path)

st.set_page_config(
    page_title="SIRA",
    page_icon=logo_img if logo_img else "SIRA",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0F1719;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1180px;
}

section[data-testid="stSidebar"] {
    background: #151B20;
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] > div {
    padding: 1.4rem 1rem;
}

.sidebar-header {
    background: #1B2428;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1.15rem 1rem;
    margin-bottom: 1.2rem;
    text-align: center;
}

.sidebar-logo {
    display: flex;
    justify-content: center;
    margin-bottom: 0.65rem;
}

.sidebar-logo img {
    width: 74px;
    height: auto;
}

.sidebar-title {
    color: #EAF7F3;
    font-size: 1.15rem;
    font-weight: 800;
    margin-bottom: 0.15rem;
}

.sidebar-subtitle {
    color: #A7B8B3;
    font-size: 0.78rem;
    line-height: 1.35;
}

.sidebar-footer {
    border-top: 1px solid rgba(255,255,255,0.08);
    margin-top: 1.3rem;
    padding-top: 1rem;
    color: #A7B8B3;
    font-size: 0.8rem;
    line-height: 1.45;
}

.sidebar-footer strong {
    color: #D6F3EA;
}

div[data-testid="stRadio"] > label {
    color: #DCEAE6;
    font-weight: 700;
    font-size: 0.92rem;
    margin-bottom: 0.6rem;
}

div[data-testid="stRadio"] div[role="radiogroup"] {
    gap: 0.35rem;
}

div[data-testid="stRadio"] label[data-baseweb="radio"] {
    background: #1B2428;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.58rem 0.75rem;
    transition: all 0.15s ease-in-out;
}

div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    background: #20312F;
    border-color: rgba(86, 184, 158, 0.45);
}

div[data-testid="stRadio"] label[data-baseweb="radio"] p {
    color: #EAF7F3;
    font-size: 0.95rem;
    font-weight: 600;
}

h1, h2, h3, h4 {
    color: #EAF7F3 !important;
}

h1 {
    font-size: 2.05rem;
    font-weight: 800;
    letter-spacing: -0.035em;
    margin-bottom: 0.25rem;
}

h2 {
    font-weight: 800;
    letter-spacing: -0.025em;
}

h3 {
    font-weight: 750;
}

p, li, label, span {
    color: #CFDCD8;
}

hr {
    border: none;
    height: 1px;
    background: rgba(255,255,255,0.10);
    margin: 2rem 0;
}

.logo-main {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0.3rem 0 1.4rem 0;
}

.logo-main img {
    width: min(400px, 60vw);
    height: auto;
    object-fit: contain;
}

.hero-wrapper {
    background: #151F22;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 26px;
    padding: 2.1rem 2.3rem;
    box-shadow: 0 18px 40px rgba(0,0,0,0.25);
    margin-bottom: 1.4rem;
}

.hero-kicker {
    width: fit-content;
    padding: 0.42rem 0.8rem;
    border-radius: 999px;
    background: rgba(86, 184, 158, 0.13);
    border: 1px solid rgba(86, 184, 158, 0.30);
    color: #9DE3CF;
    font-size: 0.82rem;
    font-weight: 750;
    margin-bottom: 1rem;
}

.hero-title {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.18;
    color: #EAF7F3;
    margin-bottom: 0.85rem;
    letter-spacing: -0.035em;
}

.hero-subtitle {
    font-size: 1.02rem;
    line-height: 1.72;
    color: #AFC3BE;
    max-width: 900px;
}

.role-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.15rem;
    margin-top: 1.15rem;
}

.role-card {
    background: #151F22;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 1.55rem;
    min-height: 235px;
    box-shadow: 0 14px 30px rgba(0,0,0,0.22);
    transition: all 0.15s ease-in-out;
}

.role-card:hover {
    transform: translateY(-3px);
    border-color: rgba(86, 184, 158, 0.55);
    box-shadow: 0 18px 36px rgba(0,0,0,0.28);
}

.role-title {
    color: #9DE3CF;
    font-size: 1.32rem;
    font-weight: 800;
    margin-bottom: 0.65rem;
}

.role-text {
    color: #B7C8C4;
    font-size: 0.96rem;
    line-height: 1.62;
    margin-bottom: 0.95rem;
}

.role-list {
    padding-left: 1.15rem;
    margin-top: 0.8rem;
}

.role-list li {
    margin-bottom: 0.42rem;
    color: #CFDCD8;
}

.section-title {
    color: #EAF7F3;
    font-size: 1.18rem;
    font-weight: 800;
    margin-top: 1.7rem;
    margin-bottom: 0.9rem;
    letter-spacing: -0.02em;
}

.app-page-header {
    background: #151F22;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 12px 28px rgba(0,0,0,0.20);
}

.app-page-title {
    color: #EAF7F3;
    font-size: 2rem;
    font-weight: 850;
    letter-spacing: -0.04em;
    margin-bottom: 0.35rem;
}

.app-page-subtitle {
    color: #AFC3BE;
    font-size: 1rem;
    line-height: 1.6;
}

.app-section-info {
    background: rgba(86, 184, 158, 0.10);
    border: 1px solid rgba(86, 184, 158, 0.28);
    border-left: 5px solid #56B89E;
    border-radius: 18px;
    padding: 1rem 1.2rem;
    margin-bottom: 1.4rem;
    color: #CFEDE5;
}

.app-section-info strong {
    color: #9DE3CF;
}

[data-testid="stMetric"] {
    background: #151F22 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 20px !important;
    padding: 1rem 1.1rem;
    box-shadow: 0 12px 26px rgba(0,0,0,0.20);
}

[data-testid="stMetricLabel"] {
    color: #AFC3BE !important;
    font-weight: 650;
}

[data-testid="stMetricValue"] {
    color: #9DE3CF !important;
    font-size: 1.55rem;
    font-weight: 800;
}

div[data-testid="stTabs"] {
    background: #151F22;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 1rem 1rem 1.3rem 1rem;
    box-shadow: 0 12px 28px rgba(0,0,0,0.18);
}

div[data-testid="stTabs"] button {
    color: #C8D8D4 !important;
    font-weight: 650;
    background: transparent;
    border-radius: 12px 12px 0 0;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #9DE3CF !important;
    border-bottom-color: #56B89E !important;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background: #10181B !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    color: #EAF7F3 !important;
    border-radius: 13px !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: #56B89E !important;
    box-shadow: 0 0 0 1px rgba(86, 184, 158, 0.25) !important;
}

div[data-baseweb="select"] > div {
    background: #10181B !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 13px !important;
    color: #EAF7F3 !important;
}

.stButton > button {
    border-radius: 13px !important;
    border: 1px solid rgba(86, 184, 158, 0.45) !important;
    background: rgba(86, 184, 158, 0.13
</style>
""", unsafe_allow_html=True)

from conexiones import (
    obtener_colecciones_mongo,
    obtener_driver_neo4j,
    NEO4J_DATABASE,
    obtener_cassandra_session
)

import vistas.vista_ciudadano as vista_ciudadano
import vistas.vista_administrador as vista_administrador


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


if logo_b64:
    st.sidebar.markdown(
        f"""
        <div class="sidebar-header">
            <div class="sidebar-logo">
                <img src="data:image/png;base64,{logo_b64}">
            </div>
            <div class="sidebar-title">SIRA</div>
            <div class="sidebar-subtitle">Sistema Inteligente de Reciclaje Ambiental</div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.title("SIRA")

rol = st.sidebar.radio(
    "Seleccioná tu perfil",
    ["Inicio", "Ciudadano", "Administrador"],
    key="sidebar_rol"
)

st.sidebar.markdown(
    """
    <div class="sidebar-footer">
        <strong>Proyecto de Ingeniería de Datos II</strong><br>
        Plataforma NoSQL para gestión de reciclaje urbano.
    </div>
    """,
    unsafe_allow_html=True
)


if rol == "Inicio":
    if nombre_b64:
        st.markdown(
            f"""
            <div class="logo-main">
                <img src="data:image/png;base64,{nombre_b64}">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.title("SIRA")

    st.markdown(
        """
        <div class="hero-wrapper">
            <div class="hero-kicker">Gestión ambiental urbana</div>
            <div class="hero-title">Una plataforma para organizar puntos verdes, reciclaje y recolecciones</div>
            <div class="hero-subtitle">
                SIRA centraliza información ambiental y operativa de la Ciudad de Buenos Aires.
                Permite consultar puntos verdes, monitorear disponibilidad, analizar relaciones entre entidades
                y registrar históricos de recolección mediante bases de datos NoSQL especializadas.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="role-grid">
            <div class="role-card">
                <div class="role-title">Portal del ciudadano</div>
                <div class="role-text">
                    Acceso a información útil para reciclar de forma simple y rápida.
                </div>
                <ul class="role-list">
                    <li>Búsqueda de puntos verdes por barrio, residuo, horario o zona.</li>
                    <li>Consulta de disponibilidad y saturación en tiempo real.</li>
                    <li>Visualización de comunidad, ranking y hábitos de reciclaje.</li>
                </ul>
            </div>
            <div class="role-card">
                <div class="role-title">Panel del administrador</div>
                <div class="role-text">
                    Herramientas para gestionar datos, monitorear operaciones y consultar métricas.
                </div>
                <ul class="role-list">
                    <li>Administración de puntos verdes, residuos, usuarios y relaciones.</li>
                    <li>Monitoreo de alertas, estados temporales y disponibilidad.</li>
                    <li>Registro histórico de recolecciones y análisis operativo.</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    import redis_app.consultas_redis as redis_consultas

    total_puntos = coleccion_puntos.count_documents({})
    total_residuos = coleccion_residuos.count_documents({})

    try:
        puntos_disponibles = len(redis_consultas.obtener_puntos_disponibles())
        puntos_saturados = len(redis_consultas.obtener_puntos_saturados())
    except Exception:
        puntos_disponibles = 0
        puntos_saturados = 0

    st.markdown(
        """
        <div class="section-title">Resumen del sistema</div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Puntos verdes", total_puntos)
    c2.metric("Tipos de residuos", total_residuos)
    c3.metric("Disponibles", puntos_disponibles)
    c4.metric("Saturados", puntos_saturados)


elif rol == "Ciudadano":
    vista_ciudadano.render(
        coleccion_puntos=coleccion_puntos,
        coleccion_residuos=coleccion_residuos,
        driver_neo4j=driver_neo4j,
        neo4j_database=NEO4J_DATABASE,
        capturar_salida=capturar_salida,
    )


elif rol == "Administrador":
    vista_administrador.render(
        coleccion_puntos=coleccion_puntos,
        coleccion_residuos=coleccion_residuos,
        driver_neo4j=driver_neo4j,
        neo4j_database=NEO4J_DATABASE,
        session_cassandra=session_cassandra,
        capturar_salida=capturar_salida,
    )