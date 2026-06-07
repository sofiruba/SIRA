from cassandra.cluster import Cluster
import pandas as pd


# =====================================
# CONEXION A CASSANDRA
# =====================================

def conectar():
    cluster = Cluster(['localhost'])
    session = cluster.connect('sira')
    return cluster, session


# =====================================
# MAP PUNTO VERDE PARA BARRIO
# =====================================

PUNTOS_VERDES = {
    "PV1": "Villa Lugano",
    "PV2": "Flores",
    "PV3": "Palermo",
    "PV4": "Caballito",
    "PV5": "Belgrano",
    "PV6": "Almagro",
    "PV7": "Recoleta",
    "PV8": "Barracas",
    "PV9": "Mataderos",
    "PV10": "Nuñez",
    "PV11": "Parque Chacabuco",
    "PV12": "Saavedra",
    "PV13": "Villa Urquiza",
    "PV14": "Palermo",
    "PV15": "Constitucion",
    "PV16": "Caballito",
    "PV17": "Boedo",
    "PV18": "Villa Devoto",
    "PV19": "Parque Avellaneda",
    "PV20": "San Cristobal",
    "PV21": "Caballito",
    "PV22": "Retiro",
    "PV23": "Colegiales",
    "PV24": "Villa Crespo",
    "PV25": "Floresta",
    "PV26": "Puerto Madero",
    "PV27": "Chacarita",
    "PV28": "Monte Castro",
    "PV29": "Parque Patricios",
    "PV30": "Villa Pueyrredon",
    "PV31": "Versalles",
    "PV32": "Villa Real",
    "PV33": "Villa del Parque",
    "PV34": "San Telmo",
    "PV35": "Agronomia",
    "PV36": "Villa Ortuzar",
    "PV37": "Balvanera",
    "PV38": "Belgrano",
    "PV39": "Nueva Pompeya",
    "PV40": "Liniers",
    "PV41": "Coghlan",
    "PV42": "Parque Chas",
    "PV43": "Villa Santa Rita",
    "PV44": "Villa General Mitre",
    "PV45": "Caballito"
}


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

def cargar_actividad_por_zona(session, df):

    query = session.prepare("""
    INSERT INTO actividad_por_zona
    (zona, fecha_recoleccion, recoleccion_id,
     punto_verde_id, peso_kg)
    VALUES (?, ?, ?, ?, ?)
    """)

    for _, row in df.iterrows():

        zona = PUNTOS_VERDES.get(
            row["punto_verde_id"],
            "Desconocida"
        )

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

    cluster, session = conectar()

    recolecciones = pd.read_csv("recolecciones.csv")
    retiros = pd.read_csv("retiros.csv")

    cargar_recolecciones_por_usuario(session, recolecciones)
    cargar_recolecciones_por_punto_verde(session, recolecciones)
    cargar_recolecciones_por_id(session, recolecciones)
    cargar_residuos_por_mes(session, recolecciones)
    cargar_actividad_por_zona(session, recolecciones)

    cargar_retiros_por_reciclador(session, retiros)

    print("Datos cargados correctamente en Cassandra.")

    cluster.shutdown()


if __name__ == "__main__":
    main()