from conexiones import obtener_cassandra_session
import pandas as pd


def crear_recoleccion(
    recoleccion_id,
    usuario_id,
    punto_verde_id,
    fecha_recoleccion,
    tipo_residuo,
    peso_kg,
    session=None
):
    if session is None:
        session = obtener_cassandra_session()

    fecha = pd.to_datetime(fecha_recoleccion)

    recoleccion_id = str(recoleccion_id)
    usuario_id = str(usuario_id)
    punto_verde_id = str(punto_verde_id)
    tipo_residuo = str(tipo_residuo)
    peso_kg = float(peso_kg)

    # 1. Insertar por ID
    query_id = session.prepare("""
        INSERT INTO recolecciones_por_id
        (recoleccion_id, usuario_id, punto_verde_id, fecha_recoleccion, tipo_residuo, peso_kg)
        VALUES (?, ?, ?, ?, ?, ?)
    """)

    session.execute(query_id, (
        recoleccion_id,
        usuario_id,
        punto_verde_id,
        fecha,
        tipo_residuo,
        peso_kg
    ))

    # 2. Insertar por usuario
    query_usuario = session.prepare("""
        INSERT INTO recolecciones_por_usuario
        (usuario_id, fecha_recoleccion, recoleccion_id, punto_verde_id, tipo_residuo, peso_kg)
        VALUES (?, ?, ?, ?, ?, ?)
    """)

    session.execute(query_usuario, (
        usuario_id,
        fecha,
        recoleccion_id,
        punto_verde_id,
        tipo_residuo,
        peso_kg
    ))

    # 3. Insertar por punto verde
    query_punto = session.prepare("""
        INSERT INTO recolecciones_por_punto_verde
        (punto_verde_id, fecha_recoleccion, recoleccion_id, usuario_id, tipo_residuo, peso_kg)
        VALUES (?, ?, ?, ?, ?, ?)
    """)

    session.execute(query_punto, (
        punto_verde_id,
        fecha,
        recoleccion_id,
        usuario_id,
        tipo_residuo,
        peso_kg
    ))

    return f"Recolección {recoleccion_id} creada correctamente"

def obtener_recoleccion_por_id(recoleccion_id, session=None):
    if session is None:
        session = obtener_cassandra_session()

    query = session.prepare("""
    SELECT * FROM recolecciones_por_id
    WHERE recoleccion_id = ?
    """)

    return session.execute(query, (str(recoleccion_id),)).one()


def obtener_recolecciones_por_usuario(usuario_id, session=None):
    if session is None:
        session = obtener_cassandra_session()

    query = session.prepare("""
    SELECT * FROM recolecciones_por_usuario
    WHERE usuario_id = ?
    """)

    return list(session.execute(query, (str(usuario_id),)))


def actualizar_peso_recoleccion(recoleccion_id, nuevo_peso, session=None):
    if session is None:
        session = obtener_cassandra_session()

    query = session.prepare("""
    UPDATE recolecciones_por_id
    SET peso_kg = ?
    WHERE recoleccion_id = ?
    """)

    session.execute(query, (float(nuevo_peso), str(recoleccion_id)))

    return "Peso actualizado correctamente"


def actualizar_tipo_residuo(recoleccion_id, nuevo_tipo, session=None):
    if session is None:
        session = obtener_cassandra_session()

    query = session.prepare("""
    UPDATE recolecciones_por_id
    SET tipo_residuo = ?
    WHERE recoleccion_id = ?
    """)

    session.execute(query, (str(nuevo_tipo), str(recoleccion_id)))

    return "Tipo de residuo actualizado correctamente"


def eliminar_recoleccion(recoleccion_id, session=None):
    if session is None:
        session = obtener_cassandra_session()

    query = session.prepare("""
    DELETE FROM recolecciones_por_id
    WHERE recoleccion_id = ?
    """)

    session.execute(query, (str(recoleccion_id),))

    return f"Recolección {recoleccion_id} eliminada correctamente"