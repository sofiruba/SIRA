import os
import pandas as pd
from conexiones import obtener_cassandra_session

# =====================================
# RUTA BASE DEL PROYECTO (SIRA)
# =====================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# =====================================
# RUTAS CSV
# =====================================
RUTA_RECOLECCIONES = os.path.join(BASE_DIR, "cassandra", "recolecciones.csv")
RUTA_RETIROS = os.path.join(BASE_DIR, "cassandra", "retiros.csv")
RUTA_PUNTOS = os.path.join(BASE_DIR, "neo4j", "puntos_verdes.csv")

def cargar_mapa_puntos():
    try:
        df_puntos = pd.read_csv(RUTA_PUNTOS)
        return dict(zip(df_puntos["id"], df_puntos["barrio"]))
    except FileNotFoundError:
        print("No se encontró puntos_verdes.csv en carpeta neo4j")
        return {}

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
            row["recoleccion_id"],
            row["punto_verde_id"],
            row["tipo_residuo"],
            float(row["peso_kg"])
        ))


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
            row["punto_verde_id"],
            pd.to_datetime(row["fecha_recoleccion"]),
            row["recoleccion_id"],
            str(row["usuario_id"]),
            row["tipo_residuo"],
            float(row["peso_kg"])
        ))


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
            row["recoleccion_id"],
            str(row["usuario_id"]),
            row["punto_verde_id"],
            pd.to_datetime(row["fecha_recoleccion"]),
            row["tipo_residuo"],
            float(row["peso_kg"])
        ))


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
            row["recoleccion_id"],
            row["tipo_residuo"],
            float(row["peso_kg"]),
            row["punto_verde_id"]
        ))


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
            row["reciclador_id"],
            pd.to_datetime(row["fecha_retiro"]),
            row["retiro_id"],
            row["punto_verde_id"],
            float(row["peso_total_kg"])
        ))


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
        # Acá usa el diccionario dinámico que le pasamos desde el main
        zona = mapa_puntos.get(row["punto_verde_id"], "Desconocida")
        
        session.execute(query, (
            zona,
            pd.to_datetime(row["fecha_recoleccion"]),
            row["recoleccion_id"],
            row["punto_verde_id"],
            float(row["peso_kg"])
        ))


# =====================================
# MAIN
# =====================================

def main():
    print("Iniciando carga en Cassandra...")

    session = obtener_cassandra_session()

    # ==============================
    # MAPA PUNTOS VERDES
    # ==============================
    mapa_puntos_verdes = cargar_mapa_puntos()

    # ==============================
    # CSV CASSANDRA
    # ==============================
    recolecciones = pd.read_csv(RUTA_RECOLECCIONES)
    retiros = pd.read_csv(RUTA_RETIROS)

    # ==============================
    # CARGAS
    # ==============================
    cargar_recolecciones_por_usuario(session, recolecciones)
    cargar_recolecciones_por_punto_verde(session, recolecciones)
    cargar_recolecciones_por_id(session, recolecciones)
    cargar_residuos_por_mes(session, recolecciones)
    cargar_actividad_por_zona(session, recolecciones, mapa_puntos_verdes)

    cargar_retiros_por_reciclador(session, retiros)

    print("Carga finalizada correctamente en Cassandra")

    session.shutdown()


if __name__ == "__main__":
    main()