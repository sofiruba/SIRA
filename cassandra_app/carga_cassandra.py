import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from conexiones import obtener_cassandra_session

# =====================================
# RUTA BASE DEL PROYECTO (SIRA)
# =====================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# =====================================
# RUTAS CSV
# =====================================
RUTA_RECOLECCIONES = os.path.join(BASE_DIR, "cassandra_app", "recolecciones.csv")
RUTA_RETIROS = os.path.join(BASE_DIR, "cassandra_app", "retiros.csv")
RUTA_PUNTOS = os.path.join(BASE_DIR, "cassandra_app", "puntos_verdes.csv")


# =====================================
# MAPA PUNTOS VERDES
# =====================================

def cargar_mapa_puntos():
    try:
        df_puntos = pd.read_csv(RUTA_PUNTOS)
        return dict(zip(df_puntos["id"], df_puntos["barrio"]))
    except FileNotFoundError:
        print("No se encontró puntos_verdes.csv en carpeta neo4j")
        return {}


# =====================================
# CREAR TABLAS
# =====================================
def crear_tablas(session):

    session.execute("""
    CREATE TABLE IF NOT EXISTS recolecciones_por_usuario (
        usuario_id        TEXT,
        fecha_recoleccion TIMESTAMP,
        recoleccion_id    TEXT,
        punto_verde_id    TEXT,
        tipo_residuo      TEXT,
        peso_kg           FLOAT,
        PRIMARY KEY (usuario_id, fecha_recoleccion, recoleccion_id)
    ) WITH CLUSTERING ORDER BY (fecha_recoleccion DESC)
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS recolecciones_por_punto_verde (
        punto_verde_id    TEXT,
        fecha_recoleccion TIMESTAMP,
        recoleccion_id    TEXT,
        usuario_id        TEXT,
        tipo_residuo      TEXT,
        peso_kg           FLOAT,
        PRIMARY KEY (punto_verde_id, fecha_recoleccion, recoleccion_id)
    ) WITH CLUSTERING ORDER BY (fecha_recoleccion DESC)
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS recolecciones_por_id (
        recoleccion_id    TEXT,
        usuario_id        TEXT,
        punto_verde_id    TEXT,
        fecha_recoleccion TIMESTAMP,
        tipo_residuo      TEXT,
        peso_kg           FLOAT,
        PRIMARY KEY (recoleccion_id)
    )
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS residuos_por_mes (
        anio_mes          TEXT,
        fecha_recoleccion TIMESTAMP,
        recoleccion_id    TEXT,
        tipo_residuo      TEXT,
        peso_kg           FLOAT,
        punto_verde_id    TEXT,
        PRIMARY KEY (anio_mes, fecha_recoleccion, recoleccion_id)
    ) WITH CLUSTERING ORDER BY (fecha_recoleccion DESC)
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS retiros_por_reciclador (
        reciclador_id  TEXT,
        fecha_retiro   TIMESTAMP,
        retiro_id      TEXT,
        punto_verde_id TEXT,
        peso_total_kg  FLOAT,
        PRIMARY KEY (reciclador_id, fecha_retiro, retiro_id)
    ) WITH CLUSTERING ORDER BY (fecha_retiro DESC)
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS actividad_por_zona (
        zona              TEXT,
        fecha_recoleccion TIMESTAMP,
        recoleccion_id    TEXT,
        punto_verde_id    TEXT,
        peso_kg           FLOAT,
        PRIMARY KEY (zona, fecha_recoleccion, recoleccion_id)
    ) WITH CLUSTERING ORDER BY (fecha_recoleccion DESC)
    """)

    print("Tablas verificadas/creadas correctamente")
# =====================================
# TABLA 1
# =====================================

def cargar_recolecciones_por_usuario(session, df):

    query = session.prepare("""
    INSERT INTO recolecciones_por_usuario
    (usuario_id, fecha_recoleccion, recoleccion_id,
     punto_verde_id, tipo_residuo, peso_kg)
    VALUES (?, ?, ?, ?, ?, ?)
    """)

    for _, row in df.iterrows():
        session.execute(query, (
            str(row["usuario_id"]),
            pd.to_datetime(row["fecha_recoleccion"]),
            str(row["recoleccion_id"]),
            str(row["punto_verde_id"]),
            row["tipo_residuo"],
            float(row["peso_kg"])
        ))

    print(f"  Tabla 1 cargada: {len(df)} registros en recolecciones_por_usuario")


# =====================================
# TABLA 2
# =====================================

def cargar_recolecciones_por_punto_verde(session, df):

    query = session.prepare("""
    INSERT INTO recolecciones_por_punto_verde
    (punto_verde_id, fecha_recoleccion, recoleccion_id,
     usuario_id, tipo_residuo, peso_kg)
    VALUES (?, ?, ?, ?, ?, ?)
    """)

    for _, row in df.iterrows():
        session.execute(query, (
            str(row["punto_verde_id"]),
            pd.to_datetime(row["fecha_recoleccion"]),
            str(row["recoleccion_id"]),
            str(row["usuario_id"]),
            row["tipo_residuo"],
            float(row["peso_kg"])
        ))

    print(f"  Tabla 2 cargada: {len(df)} registros en recolecciones_por_punto_verde")


# =====================================
# TABLA 3
# =====================================

def cargar_recolecciones_por_id(session, df):

    query = session.prepare("""
    INSERT INTO recolecciones_por_id
    (recoleccion_id, usuario_id, punto_verde_id,
     fecha_recoleccion, tipo_residuo, peso_kg)
    VALUES (?, ?, ?, ?, ?, ?)
    """)

    for _, row in df.iterrows():
        session.execute(query, (
            str(row["recoleccion_id"]),
            str(row["usuario_id"]),
            str(row["punto_verde_id"]),
            pd.to_datetime(row["fecha_recoleccion"]),
            row["tipo_residuo"],
            float(row["peso_kg"])
        ))

    print(f"  Tabla 3 cargada: {len(df)} registros en recolecciones_por_id")


# =====================================
# TABLA 4
# =====================================

def cargar_residuos_por_mes(session, df):

    query = session.prepare("""
    INSERT INTO residuos_por_mes
    (anio_mes, fecha_recoleccion, recoleccion_id,
     tipo_residuo, peso_kg, punto_verde_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """)

    for _, row in df.iterrows():
        fecha = pd.to_datetime(row["fecha_recoleccion"])
        anio_mes = fecha.strftime("%Y-%m")

        session.execute(query, (
            anio_mes,
            fecha,
            str(row["recoleccion_id"]),
            row["tipo_residuo"],
            float(row["peso_kg"]),
            str(row["punto_verde_id"])
        ))

    print(f"  Tabla 4 cargada: {len(df)} registros en residuos_por_mes")


# =====================================
# TABLA 5
# =====================================

def cargar_retiros_por_reciclador(session, df):

    query = session.prepare("""
    INSERT INTO retiros_por_reciclador
    (reciclador_id, fecha_retiro, retiro_id,
     punto_verde_id, peso_total_kg)
    VALUES (?, ?, ?, ?, ?)
    """)

    for _, row in df.iterrows():
        session.execute(query, (
            str(row["reciclador_id"]),
            pd.to_datetime(row["fecha_retiro"]),
            str(row["retiro_id"]),
            str(row["punto_verde_id"]),
            float(row["peso_total_kg"])
        ))

    print(f"  Tabla 5 cargada: {len(df)} registros en retiros_por_reciclador")


# =====================================
# TABLA 6
# =====================================

def cargar_actividad_por_zona(session, df, mapa_puntos):

    query = session.prepare("""
    INSERT INTO actividad_por_zona
    (zona, fecha_recoleccion, recoleccion_id,
     punto_verde_id, peso_kg)
    VALUES (?, ?, ?, ?, ?)
    """)

    for _, row in df.iterrows():
        zona = mapa_puntos.get(str(row["punto_verde_id"]), "Desconocida")

        session.execute(query, (
            zona,
            pd.to_datetime(row["fecha_recoleccion"]),
            str(row["recoleccion_id"]),
            str(row["punto_verde_id"]),
            float(row["peso_kg"])
        ))

    print(f"  Tabla 6 cargada: {len(df)} registros en actividad_por_zona")


# =====================================
# MAIN
# =====================================

def main():
    print("Iniciando carga en Cassandra...")

    session = obtener_cassandra_session()

    # ==============================
    # CREAR TABLAS SI NO EXISTEN
    # ==============================
    crear_tablas(session)

    # ==============================
    # MAPA PUNTOS VERDES
    # ==============================
    mapa_puntos_verdes = cargar_mapa_puntos()

    # ==============================
    # LEER CSV
    # ==============================
    recolecciones = pd.read_csv(RUTA_RECOLECCIONES)
    retiros = pd.read_csv(RUTA_RETIROS)

    print(f"\nCSV leídos: {len(recolecciones)} recolecciones, {len(retiros)} retiros")
    print("\nCargando tablas...")

    # ==============================
    # CARGAS
    # ==============================
    cargar_recolecciones_por_usuario(session, recolecciones)
    cargar_recolecciones_por_punto_verde(session, recolecciones)
    cargar_recolecciones_por_id(session, recolecciones)
    cargar_residuos_por_mes(session, recolecciones)
    cargar_actividad_por_zona(session, recolecciones, mapa_puntos_verdes)
    cargar_retiros_por_reciclador(session, retiros)

    print("\nCarga finalizada correctamente en Cassandra")

    session.shutdown()


if __name__ == "__main__":
    main()