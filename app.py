```python
import streamlit as st
import pandas as pd
import io
import contextlib

import mongodb.SIRA_mongodb_funciones as mongo
import neo4j.consultas_neo as neo_consultas
import redis.consultas_redis as redis_consultas
import cassandra.consultas_cassandra as cassandra_consultas

import mongodb.mongo_crud_app as mongo_crud
import neo4j.neo_crud_app as neo_crud
import redis.redis_crud_app as redis_crud
import cassandra.cassandra_crud_app as cassandra_crud

from conexiones import obtener_colecciones_mongo, obtener_driver_neo4j, NEO4J_DATABASE, obtener_cliente_redis, obtener_cassandra_session


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="SIRA",
    page_icon="♻️",
    layout="wide"
)


# ============================================================
# CONEXIONES
# ============================================================

@st.cache_resource
def cargar_mongo():
    return obtener_colecciones_mongo()


@st.cache_resource
def cargar_neo4j():
    return obtener_driver_neo4j()

@st.cache_resource
def cargar_redis(): 
    return obtener_cliente_redis()

@st.cache_resource
def cargar_cassandra(): 
    return obtener_cassandra_session()


coleccion_puntos, coleccion_residuos = cargar_mongo()
driver_neo4j = cargar_neo4j()
cliente_redis = cargar_redis()
session_cassandra = cargar_cassandra()


# ============================================================
# FUNCIONES AUXILIARES
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


def ejecutar_consulta_neo(funcion):
    try:
        with driver_neo4j.session(database=NEO4J_DATABASE) as session:
            capturar_salida(funcion, session)

    except Exception as e:
        st.error(f"Error de conexión o consulta en Neo4j: {e}")


def buscar_funcion(modulo, posibles_nombres):
    for nombre in posibles_nombres:
        if hasattr(modulo, nombre):
            return getattr(modulo, nombre)
    return None


def ejecutar_neo_por_nombre(posibles_nombres):
    funcion = buscar_funcion(neo_consultas, posibles_nombres)

    if funcion is None:
        st.error("No encontré esa función en consultasNeo.py.")
        st.write("Nombres buscados:", posibles_nombres)
        return

    ejecutar_consulta_neo(funcion)


def mostrar_lista_como_tabla(datos, nombre_columna):
    if datos:
        df = pd.DataFrame({nombre_columna: datos})
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No se encontraron resultados.")


# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #1B5E20;
}

[data-testid="stMetricValue"] {
    font-size: 24px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("♻️ SIRA")
st.sidebar.caption("Sistema Inteligente de Reciclaje Ambiental")

seccion = st.sidebar.radio(
    "Menú principal",
    [
        "Inicio",
        "MongoDB",
        "Neo4j",
        "Redis",
        "Cassandra",
        "Análisis general"
    ],
    key="sidebar_menu_principal"
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
    Esta interfaz reutiliza los módulos ya desarrollados para MongoDB, Neo4j y Redis.
    MongoDB almacena datos descriptivos de puntos verdes y residuos.
    Neo4j representa relaciones entre usuarios, residuos, puntos verdes y recicladores.
    Redis administra estados temporales y en tiempo real.
    Cassandra guarda registros históricos de recolecciones, usuarios y puntos verdes.
    """)


# ============================================================
# MONGODB
# ============================================================

elif seccion == "MongoDB":
    st.title("🍃 MongoDB")

    st.write("""
    MongoDB se utiliza para almacenar información flexible y descriptiva,
    como puntos verdes, residuos aceptados, horarios, barrios y comunas.
    """)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Consultas",
        "Crear",
        "Actualizar",
        "Eliminar"
    ])

    with tab1:
        st.subheader("Consultas MongoDB")

        opcion_mongo = st.selectbox(
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
                "Buscar punto verde por ID"
            ],
            key="mongo_select_consulta"
        )

        if opcion_mongo == "Buscar punto verde por ID":
            id_punto_buscar = st.number_input(
                "ID del punto verde",
                min_value=1,
                step=1,
                key="mongo_buscar_punto_id"
            )

        if st.button("Ejecutar consulta MongoDB", key="mongo_btn_ejecutar_consulta"):
            if opcion_mongo.startswith("Consulta 1"):
                capturar_salida(mongo.consulta1, coleccion_puntos)

            elif opcion_mongo.startswith("Consulta 2"):
                capturar_salida(mongo.consulta2, coleccion_puntos)

            elif opcion_mongo.startswith("Consulta 3"):
                capturar_salida(mongo.consulta3, coleccion_puntos)

            elif opcion_mongo.startswith("Consulta 4"):
                capturar_salida(mongo.consulta4, coleccion_puntos)

            elif opcion_mongo.startswith("Consulta 5"):
                capturar_salida(mongo.consulta5, coleccion_puntos)

            elif opcion_mongo.startswith("Consulta 6"):
                capturar_salida(mongo.consulta6, coleccion_residuos)

            elif opcion_mongo.startswith("Consulta 7"):
                capturar_salida(mongo.consulta7, coleccion_residuos)

            elif opcion_mongo.startswith("Consulta 8"):
                capturar_salida(mongo.consulta8, coleccion_residuos)

            elif opcion_mongo.startswith("Consulta 9"):
                capturar_salida(mongo.consulta9, coleccion_residuos)

            elif opcion_mongo == "Buscar punto verde por ID":
                punto = mongo_crud.buscar_punto_verde_por_id(int(id_punto_buscar))

                if punto:
                    st.json(punto)
                else:
                    st.warning("No se encontró un punto verde con ese ID.")

    with tab2:
        st.subheader("Crear datos en MongoDB")

        tipo_creacion_mongo = st.selectbox(
            "Qué querés crear",
            [
                "Residuo",
                "Punto verde"
            ],
            key="mongo_select_crear"
        )

        if tipo_creacion_mongo == "Residuo":
            nombre_residuo_crear = st.text_input(
                "Nombre del residuo",
                key="mongo_crear_residuo_nombre"
            )

            color_residuo_crear = st.text_input(
                "Color del contenedor",
                key="mongo_crear_residuo_color"
            )

            categoria_residuo_crear = st.text_input(
                "Categoría",
                key="mongo_crear_residuo_categoria"
            )

            if st.button("Crear residuo", key="mongo_btn_crear_residuo"):
                if nombre_residuo_crear and color_residuo_crear and categoria_residuo_crear:
                    mensaje = mongo_crud.crear_residuo(
                        nombre_residuo_crear,
                        color_residuo_crear,
                        categoria_residuo_crear
                    )
                    st.success(mensaje)
                else:
                    st.error("Completá todos los campos.")

        elif tipo_creacion_mongo == "Punto verde":
            nombre_punto_crear = st.text_input(
                "Nombre del punto verde",
                key="mongo_crear_punto_nombre"
            )

            direccion_punto_crear = st.text_input(
                "Dirección",
                key="mongo_crear_punto_direccion"
            )

            barrio_punto_crear = st.text_input(
                "Barrio",
                key="mongo_crear_punto_barrio"
            )

            comuna_punto_crear = st.text_input(
                "Comuna",
                placeholder="Comuna 6",
                key="mongo_crear_punto_comuna"
            )

            residuos_punto_crear = st.text_input(
                "Residuos aceptados",
                placeholder="R1,R2,R3",
                key="mongo_crear_punto_residuos"
            )

            dias_punto_crear = st.text_input(
                "Días de atención",
                placeholder="Lunes,Martes,Sabado",
                key="mongo_crear_punto_dias"
            )

            apertura_punto_crear = st.text_input(
                "Hora apertura",
                placeholder="09:00",
                key="mongo_crear_punto_apertura"
            )

            cierre_punto_crear = st.text_input(
                "Hora cierre",
                placeholder="18:00",
                key="mongo_crear_punto_cierre"
            )

            if st.button("Crear punto verde", key="mongo_btn_crear_punto"):
                if (
                    nombre_punto_crear
                    and direccion_punto_crear
                    and barrio_punto_crear
                    and comuna_punto_crear
                    and residuos_punto_crear
                    and dias_punto_crear
                    and apertura_punto_crear
                    and cierre_punto_crear
                ):
                    lista_residuos = [
                        r.strip().upper()
                        for r in residuos_punto_crear.split(",")
                    ]

                    lista_dias = [
                        d.strip()
                        for d in dias_punto_crear.split(",")
                    ]

                    mensaje = mongo_crud.crear_punto_verde(
                        nombre_punto_crear,
                        direccion_punto_crear,
                        barrio_punto_crear,
                        comuna_punto_crear,
                        lista_residuos,
                        lista_dias,
                        apertura_punto_crear,
                        cierre_punto_crear
                    )

                    st.success(mensaje)
                else:
                    st.error("Completá todos los campos.")

    with tab3:
        st.subheader("Actualizar datos en MongoDB")

        tipo_update_mongo = st.selectbox(
            "Qué querés actualizar",
            [
                "Horario de punto verde",
                "Tipo de residuo"
            ],
            key="mongo_select_update"
        )

        if tipo_update_mongo == "Horario de punto verde":
            id_punto_update = st.number_input(
                "ID del punto verde",
                min_value=1,
                step=1,
                key="mongo_update_punto_id"
            )

            apertura_update = st.text_input(
                "Nueva hora apertura",
                placeholder="09:00",
                key="mongo_update_punto_apertura"
            )

            cierre_update = st.text_input(
                "Nueva hora cierre",
                placeholder="18:00",
                key="mongo_update_punto_cierre"
            )

            if st.button("Actualizar horario", key="mongo_btn_actualizar_horario"):
                if apertura_update and cierre_update:
                    mensaje = mongo_crud.actualizar_horario_punto(
                        int(id_punto_update),
                        apertura_update,
                        cierre_update
                    )
                    st.info(mensaje)
                else:
                    st.error("Completá apertura y cierre.")

        elif tipo_update_mongo == "Tipo de residuo":
            id_residuo_update = st.text_input(
                "ID del residuo",
                placeholder="R1",
                key="mongo_update_residuo_id"
            )

            nombre_residuo_update = st.text_input(
                "Nuevo nombre",
                key="mongo_update_residuo_nombre"
            )

            color_residuo_update = st.text_input(
                "Nuevo color de contenedor",
                key="mongo_update_residuo_color"
            )

            categoria_residuo_update = st.text_input(
                "Nueva categoría",
                key="mongo_update_residuo_categoria"
            )

            if st.button("Actualizar residuo", key="mongo_btn_actualizar_residuo"):
                if (
                    id_residuo_update
                    and nombre_residuo_update
                    and color_residuo_update
                    and categoria_residuo_update
                ):
                    mensaje = mongo_crud.actualizar_residuo(
                        id_residuo_update.upper(),
                        nombre_residuo_update,
                        color_residuo_update,
                        categoria_residuo_update
                    )
                    st.info(mensaje)
                else:
                    st.error("Completá todos los campos.")

    with tab4:
        st.subheader("Eliminar datos en MongoDB")

        tipo_delete_mongo = st.selectbox(
            "Qué querés eliminar",
            [
                "Punto verde",
                "Tipo de residuo"
            ],
            key="mongo_select_delete"
        )

        if tipo_delete_mongo == "Punto verde":
            id_punto_delete = st.number_input(
                "ID del punto verde a eliminar",
                min_value=1,
                step=1,
                key="mongo_delete_punto_id"
            )

            if st.button("Eliminar punto verde", key="mongo_btn_eliminar_punto"):
                mensaje = mongo_crud.eliminar_punto_verde(int(id_punto_delete))
                st.warning(mensaje)

        elif tipo_delete_mongo == "Tipo de residuo":
            id_residuo_delete = st.text_input(
                "ID del residuo a eliminar",
                placeholder="R17",
                key="mongo_delete_residuo_id"
            )

            if st.button("Eliminar residuo", key="mongo_btn_eliminar_residuo"):
                if id_residuo_delete:
                    mensaje = mongo_crud.eliminar_residuo(id_residuo_delete.upper())
                    st.warning(mensaje)
                else:
                    st.error("Ingresá un ID de residuo.")


# ============================================================
# NEO4J
# ============================================================

elif seccion == "Neo4j":
    st.title("🔗 Neo4j")

    st.write("""
    Neo4j se utiliza para modelar relaciones entre usuarios,
    residuos, puntos verdes y recicladores.
    """)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Consultas",
        "Crear",
        "Actualizar",
        "Eliminar"
    ])

    with tab1:
        st.subheader("Consultas Neo4j")

        opcion_neo = st.selectbox(
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

        if st.button("Ejecutar consulta Neo4j", key="neo_btn_ejecutar_consulta"):
            if opcion_neo == "Puntos verdes cercanos":
                ejecutar_neo_por_nombre(["puntos_verdes_cercanos", "consulta1"])

            elif opcion_neo == "Usuarios por barrio":
                ejecutar_neo_por_nombre(["usuarios_por_barrio", "consulta2"])

            elif opcion_neo == "Puntos verdes por comuna":
                ejecutar_neo_por_nombre(["puntos_verdes_por_comuna", "consulta3"])

            elif opcion_neo == "Top 10 usuarios":
                ejecutar_neo_por_nombre(["top_usuarios", "consulta4"])

            elif opcion_neo == "Usuarios y residuos":
                ejecutar_neo_por_nombre(["usuarios_y_residuos", "consulta5"])

            elif opcion_neo == "Puntos verdes y residuos aceptados":
                ejecutar_neo_por_nombre(["puntos_verdes_y_residuos", "consulta6"])

            elif opcion_neo == "Recicladores y residuos":
                ejecutar_neo_por_nombre(["recicladores_y_residuos", "consulta7"])

            elif opcion_neo == "Recicladores y puntos verdes":
                ejecutar_neo_por_nombre(["recicladores_y_puntos_verdes", "consulta8"])

            elif opcion_neo == "Residuos más reciclados":
                ejecutar_neo_por_nombre(["residuos_mas_reciclados", "consulta9"])

            elif opcion_neo == "Tipos de residuos por punto verde":
                ejecutar_neo_por_nombre(["tipos_residuos_por_punto_verde", "consulta10"])

            elif opcion_neo == "Usuarios por nivel":
                ejecutar_neo_por_nombre(["usuarios_por_nivel", "consulta11"])

            elif opcion_neo == "Total de nodos":
                ejecutar_neo_por_nombre(["total_nodos", "consulta12"])

            elif opcion_neo == "Total de relaciones":
                ejecutar_neo_por_nombre(["total_relaciones", "consulta13"])

    with tab2:
        st.subheader("Crear datos en Neo4j")

        tipo_creacion_neo = st.selectbox(
            "Qué querés crear",
            [
                "Usuario",
                "Relación RECICLA",
                "Relación ENTREGA_EN",
                "Relación ACEPTA"
            ],
            key="neo_select_crear"
        )

        if tipo_creacion_neo == "Usuario":
            nombre_usuario_crear = st.text_input(
                "Nombre",
                key="neo_crear_usuario_nombre"
            )

            email_usuario_crear = st.text_input(
                "Email",
                key="neo_crear_usuario_email"
            )

            barrio_usuario_crear = st.text_input(
                "Barrio",
                key="neo_crear_usuario_barrio"
            )

            comuna_usuario_crear = st.text_input(
                "Comuna",
                placeholder="Comuna 6",
                key="neo_crear_usuario_comuna"
            )

            if st.button("Crear usuario", key="neo_btn_crear_usuario"):
                if (
                    nombre_usuario_crear
                    and email_usuario_crear
                    and barrio_usuario_crear
                    and comuna_usuario_crear
                ):
                    mensaje = neo_crud.crear_usuario(
                        nombre_usuario_crear,
                        email_usuario_crear,
                        barrio_usuario_crear,
                        comuna_usuario_crear
                    )
                    st.success(mensaje)
                else:
                    st.error("Completá todos los campos.")

        elif tipo_creacion_neo == "Relación RECICLA":
            id_usuario_recicla = st.number_input(
                "ID Usuario",
                min_value=1,
                step=1,
                key="neo_crear_recicla_id_usuario"
            )

            id_residuo_recicla = st.number_input(
                "ID Residuo",
                min_value=1,
                step=1,
                key="neo_crear_recicla_id_residuo"
            )

            if st.button("Crear relación RECICLA", key="neo_btn_crear_recicla"):
                mensaje = neo_crud.crear_relacion_recicla(
                    int(id_usuario_recicla),
                    int(id_residuo_recicla)
                )
                st.success(mensaje)

        elif tipo_creacion_neo == "Relación ENTREGA_EN":
            id_usuario_entrega = st.number_input(
                "ID Usuario",
                min_value=1,
                step=1,
                key="neo_crear_entrega_id_usuario"
            )

            id_punto_entrega = st.number_input(
                "ID Punto Verde",
                min_value=1,
                step=1,
                key="neo_crear_entrega_id_punto"
            )

            if st.button("Crear relación ENTREGA_EN", key="neo_btn_crear_entrega"):
                mensaje = neo_crud.crear_relacion_entrega_en(
                    int(id_usuario_entrega),
                    int(id_punto_entrega)
                )
                st.success(mensaje)

        elif tipo_creacion_neo == "Relación ACEPTA":
            id_punto_acepta = st.number_input(
                "ID Punto Verde",
                min_value=1,
                step=1,
                key="neo_crear_acepta_id_punto"
            )

            id_residuo_acepta = st.number_input(
                "ID Residuo",
                min_value=1,
                step=1,
                key="neo_crear_acepta_id_residuo"
            )

            if st.button("Crear relación ACEPTA", key="neo_btn_crear_acepta"):
                mensaje = neo_crud.crear_relacion_acepta(
                    int(id_punto_acepta),
                    int(id_residuo_acepta)
                )
                st.success(mensaje)

    with tab3:
        st.subheader("Actualizar datos en Neo4j")

        id_usuario_update_neo = st.number_input(
            "ID del usuario",
            min_value=1,
            step=1,
            key="neo_update_usuario_id"
        )

        puntos_update_neo = st.number_input(
            "Nuevos puntos ecológicos",
            min_value=0,
            step=10,
            key="neo_update_usuario_puntos"
        )

        if st.button("Actualizar puntos", key="neo_btn_actualizar_puntos"):
            mensaje = neo_crud.actualizar_puntos_usuario(
                int(id_usuario_update_neo),
                int(puntos_update_neo)
            )
            st.info(mensaje)

    with tab4:
        st.subheader("Eliminar datos en Neo4j")

        tipo_delete_neo = st.selectbox(
            "Qué querés eliminar",
            [
                "Usuario",
                "Relación RECICLA"
            ],
            key="neo_select_delete"
        )

        if tipo_delete_neo == "Usuario":
            id_usuario_delete_neo = st.number_input(
                "ID Usuario a eliminar",
                min_value=1,
                step=1,
                key="neo_delete_usuario_id"
            )

            if st.button("Eliminar usuario", key="neo_btn_eliminar_usuario"):
                mensaje = neo_crud.eliminar_usuario(int(id_usuario_delete_neo))
                st.warning(mensaje)

        elif tipo_delete_neo == "Relación RECICLA":
            id_usuario_delete_rel = st.number_input(
                "ID Usuario",
                min_value=1,
                step=1,
                key="neo_delete_recicla_id_usuario"
            )

            id_residuo_delete_rel = st.number_input(
                "ID Residuo",
                min_value=1,
                step=1,
                key="neo_delete_recicla_id_residuo"
            )

            if st.button("Eliminar relación RECICLA", key="neo_btn_eliminar_recicla"):
                mensaje = neo_crud.eliminar_relacion_recicla(
                    int(id_usuario_delete_rel),
                    int(id_residuo_delete_rel)
                )
                st.warning(mensaje)


# ============================================================
# REDIS
# ============================================================

elif seccion == "Redis":
    st.title("⚡ Redis - Estado en tiempo real")

    st.write("""
    Redis se utiliza para información temporal y de acceso rápido:
    estado de puntos verdes, disponibilidad, saturación, ranking y alertas.
    """)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Consultas",
        "Actualizar",
        "Eliminar",
        "Cargar datos"
    ])

    with tab1:
        st.subheader("Consultas Redis")

        consulta_redis = st.selectbox(
            "Seleccioná una consulta",
            [
                "Estado de punto verde por ID",
                "Puntos verdes disponibles",
                "Puntos verdes saturados",
                "Ranking de puntos verdes por uso",
                "Alertas recientes"
            ],
            key="redis_select_consulta"
        )

        if consulta_redis == "Estado de punto verde por ID":
            id_punto_redis_consulta = st.text_input(
                "ID del punto verde",
                placeholder="Ej: 1",
                key="redis_consulta_estado_id"
            )

        if st.button("Ejecutar consulta Redis", key="redis_btn_ejecutar_consulta"):
            if consulta_redis == "Estado de punto verde por ID":
                if id_punto_redis_consulta:
                    estado = redis_consultas.obtener_estado_punto_verde(cliente_redis, id_punto_redis_consulta)

                    if estado:
                        st.json(estado)
                    else:
                        st.warning("No se encontró estado para ese punto verde.")
                else:
                    st.error("Ingresá un ID.")

            elif consulta_redis == "Puntos verdes disponibles":
                disponibles = redis_consultas.obtener_puntos_disponibles(cliente_redis)
                mostrar_lista_como_tabla(disponibles, "punto_verde_disponible")

            elif consulta_redis == "Puntos verdes saturados":
                saturados = redis_consultas.obtener_puntos_saturados(cliente_redis)
                mostrar_lista_como_tabla(saturados, "punto_verde_saturado")

            elif consulta_redis == "Ranking de puntos verdes por uso":
                ranking = redis_consultas.obtener_ranking(cliente_redis)

                datos = [
                    {
                        "id_punto_verde": item[0],
                        "puntaje": item[1]
                    }
                    for item in ranking
                ]

                if datos:
                    df = pd.DataFrame(datos)
                    st.dataframe(df, use_container_width=True)
                    st.bar_chart(df.set_index("id_punto_verde"))
                else:
                    st.warning("No hay ranking cargado.")

            elif consulta_redis == "Alertas recientes":
                alertas = redis_consultas.obtener_alertas(cliente_redis)

                if alertas:
                    st.dataframe(pd.DataFrame(alertas), use_container_width=True)
                else:
                    st.warning("No hay alertas cargadas.")

    with tab2:
        st.subheader("Actualizar estado y capacidad de un punto verde")

        id_punto_redis_update = st.text_input(
            "ID punto verde",
            placeholder="Ej: 1",
            key="redis_update_estado_id"
        )

        estado_nuevo_redis = st.selectbox(
            "Nuevo estado",
            [
                "disponible",
                "saturado"
            ],
            key="redis_update_estado_nuevo"
        )

        capacidad_nueva_redis = st.number_input(
            "Nueva capacidad actual",
            min_value=0,
            max_value=100,
            step=1,
            key="redis_update_capacidad"
        )

        if st.button("Actualizar estado en Redis", key="redis_btn_actualizar_estado"):
            if id_punto_redis_update:
                mensaje = redis_crud.actualizar_estado_punto(
                    cliente_redis,
                    id_punto_redis_update,
                    estado_nuevo_redis,
                    capacidad_nueva_redis
                )
                st.success(mensaje)
            else:
                st.error("Ingresá un ID de punto verde.")

    with tab3:
        st.subheader("Eliminar datos temporales de Redis")

        opcion_delete_redis = st.selectbox(
            "Qué querés eliminar",
            [
                "Estado de un punto verde",
                "Todas las alertas recientes"
            ],
            key="redis_select_delete"
        )

        if opcion_delete_redis == "Estado de un punto verde":
            id_punto_redis_delete = st.text_input(
                "ID del punto verde a eliminar de Redis",
                placeholder="Ej: 1",
                key="redis_delete_estado_id"
            )

            if st.button("Eliminar estado del punto verde", key="redis_btn_eliminar_estado"):
                if id_punto_redis_delete:
                    mensaje = redis_crud.eliminar_estado_punto(cliente_redis,id_punto_redis_delete)
                    st.warning(mensaje)
                else:
                    st.error("Ingresá un ID.")

        elif opcion_delete_redis == "Todas las alertas recientes":
            if st.button("Eliminar alertas", key="redis_btn_eliminar_alertas"):
                mensaje = redis_crud.eliminar_alertas(cliente_redis)
                st.warning(mensaje)

    with tab4:
        st.subheader("Cargar datos de prueba en Redis")

        st.write("""
        Esta operación carga el archivo `redis_data.json` utilizando la función
        `cargar_datos()` del módulo `carga_Redis.py`.
        """)

        if st.button("Cargar redis_data.json", key="redis_btn_cargar_datos"):
            try:
                redis_carga.cargar_datos()
                st.success("Datos cargados correctamente en Redis.")
            except Exception as e:
                st.error(f"Error al cargar datos en Redis: {e}")

# ============================================================
# CASSANDRA
# ============================================================

elif seccion == "Cassandra":
    st.title("📦 Cassandra - Registros de recolecciones y analítica")

    st.write("""
    Cassandra almacena grandes volúmenes de recolecciones y retiros históricos.
    Se utiliza para consultas rápidas por usuario, punto verde, reciclador y zona.
    """)

    tab1, tab2, tab3 = st.tabs([
        "Consultas",
        "CRUD",
        "Análisis"
    ])

    # ====================================================
    # CONSULTAS
    # ====================================================

    with tab1:

        consulta = st.selectbox(
            "Seleccioná una consulta",
            [
                "Recolecciones por usuario",
                "Recolecciones por punto verde",
                "Retiros por reciclador",
                "Actividad por zona"
            ]
        )

        if consulta == "Recolecciones por usuario":
            usuario_id = st.text_input("ID Usuario")

        elif consulta == "Recolecciones por punto verde":
            punto_verde_id = st.text_input("ID Punto Verde")

        elif consulta == "Retiros por reciclador":
            reciclador_id = st.text_input("ID Reciclador")

        elif consulta == "Actividad por zona":
            zona = st.text_input("Zona")

        if st.button("Ejecutar consulta Cassandra"):

            try:

                if consulta == "Recolecciones por usuario":

                    datos = cassandra_consultas.consultar_usuario(
                        session_cassandra,
                        usuario_id
                    )

                elif consulta == "Recolecciones por punto verde":

                    datos = cassandra_consultas.consultar_punto_verde(
                        session_cassandra,
                        punto_verde_id
                    )

                elif consulta == "Retiros por reciclador":

                    datos = cassandra_consultas.consultar_reciclador(
                        session_cassandra,
                        reciclador_id
                    )

                else:

                    datos = cassandra_consultas.consultar_zona(
                        session_cassandra,
                        zona
                    )

                if datos:
                    st.dataframe(pd.DataFrame(datos))
                else:
                    st.warning("No se encontraron registros.")

            except Exception as e:
                st.error(e)

    # ====================================================
    # CRUD
    # ====================================================

    with tab2:

        crud = st.selectbox(
            "Operación",
            [
                "Crear",
                "Buscar por ID",
                "Actualizar peso",
                "Actualizar tipo",
                "Eliminar"
            ]
        )

        if crud == "Crear":

            recoleccion_id = st.text_input("ID Recolección")
            usuario_id = st.text_input("Usuario")
            punto_verde_id = st.text_input("Punto Verde")
            fecha = st.text_input("Fecha (YYYY-MM-DD)")
            tipo = st.text_input("Tipo Residuo")
            peso = st.number_input("Peso KG")

            if st.button("Crear recolección"):

                mensaje = cassandra_crud.crear_recoleccion(
                    recoleccion_id,
                    usuario_id,
                    punto_verde_id,
                    fecha,
                    tipo,
                    peso
                )

                st.success(mensaje)

        elif crud == "Buscar por ID":

            recoleccion_id = st.text_input("ID")

            if st.button("Buscar"):

                dato = cassandra_crud.obtener_recoleccion_por_id(
                    recoleccion_id
                )

                if dato:
                    st.json(dict(dato._asdict()))
                else:
                    st.warning("No encontrado.")

        elif crud == "Actualizar peso":

            recoleccion_id = st.text_input("ID Recolección")
            peso = st.number_input("Nuevo peso")

            if st.button("Actualizar peso"):

                mensaje = cassandra_crud.actualizar_peso_recoleccion(
                    recoleccion_id,
                    peso
                )

                st.success(mensaje)

        elif crud == "Actualizar tipo":

            recoleccion_id = st.text_input("ID Recolección")
            tipo = st.text_input("Nuevo tipo")

            if st.button("Actualizar tipo"):

                mensaje = cassandra_crud.actualizar_tipo_residuo(
                    recoleccion_id,
                    tipo
                )

                st.success(mensaje)

        elif crud == "Eliminar":

            recoleccion_id = st.text_input("ID Recolección")

            if st.button("Eliminar"):

                mensaje = cassandra_crud.eliminar_recoleccion(
                    recoleccion_id
                )

                st.warning(mensaje)

    # ====================================================
    # ANÁLISIS
    # ====================================================

    with tab3:

        usuario_id = st.text_input(
            "Usuario para análisis",
            value="1"
        )

        if st.button("Generar análisis"):

            try:

                total = cassandra_consultas.total_kg_usuario(
                    session_cassandra,
                    usuario_id
                )

                resumen = cassandra_consultas.recolecciones_por_tipo(
                    session_cassandra,
                    usuario_id
                )

                st.metric(
                    "Total reciclado (kg)",
                    round(total, 2)
                )

                if resumen:

                    df = pd.DataFrame(
                        resumen.items(),
                        columns=["Tipo", "Kg"]
                    )

                    st.dataframe(df)

                    st.bar_chart(
                        df.set_index("Tipo")
                    )

            except Exception as e:
                st.error(e)


# ============================================================
# ANÁLISIS GENERAL
# ============================================================

elif seccion == "Análisis general":
    st.title("📊 Análisis general")

    total_puntos = coleccion_puntos.count_documents({})
    total_residuos = coleccion_residuos.count_documents({})

    try:
        puntos_disponibles = len(redis_consultas.obtener_puntos_disponibles(cliente_redis))
        puntos_saturados = len(redis_consultas.obtener_puntos_saturados(cliente_redis))
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

    st.write("Usuarios por barrio:")
    ejecutar_neo_por_nombre(["usuarios_por_barrio", "consulta2"])

    st.write("Residuos más reciclados:")
    ejecutar_neo_por_nombre(["residuos_mas_reciclados", "consulta9"])
```
