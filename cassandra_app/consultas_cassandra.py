from cassandra.cluster import Cluster


def conectar():
    cluster = Cluster(['localhost'])
    session = cluster.connect('sira')
    return cluster, session


# =========================
# CONSULTAS BÁSICAS
# =========================

def consultar_usuario(session, usuario_id):
    rows = session.execute("""
        SELECT * FROM recolecciones_por_usuario
        WHERE usuario_id = %s
    """, (str(usuario_id),))

    return list(rows)


def consultar_punto_verde(session, punto_verde_id):
    rows = session.execute("""
        SELECT * FROM recolecciones_por_punto_verde
        WHERE punto_verde_id = %s
    """, (str(punto_verde_id),))

    return list(rows)


def consultar_reciclador(session, reciclador_id):
    rows = session.execute("""
        SELECT * FROM retiros_por_reciclador
        WHERE reciclador_id = %s
    """, (str(reciclador_id),))

    return list(rows)


def consultar_zona(session, zona):
    rows = session.execute("""
        SELECT * FROM actividad_por_zona
        WHERE zona = %s
    """, (str(zona),))

    return list(rows)


# =========================
# CONSULTAS AVANZADAS
# =========================

def total_kg_usuario(session, usuario_id):
    rows = consultar_usuario(session, usuario_id)
    return sum(r.peso_kg for r in rows)


def recolecciones_por_tipo(session, usuario_id):
    rows = consultar_usuario(session, usuario_id)

    resumen = {}
    for r in rows:
        tipo = r.tipo_residuo
        resumen[tipo] = resumen.get(tipo, 0) + float(r.peso_kg)

    return resumen


def ultimas_recolecciones_usuario(session, usuario_id, limite=5):
    limite = int(limite)
    rows = session.execute(
        f"SELECT * FROM recolecciones_por_usuario WHERE usuario_id = %s LIMIT {limite}",
        (str(usuario_id),)
    )

    return list(rows)


def rango_fechas_punto_verde(session, punto_verde_id):
    rows = consultar_punto_verde(session, punto_verde_id)

    return [r for r in rows if r.peso_kg > 20]


# =========================
# MAIN DEMO
# =========================

def main():
    cluster, session = conectar()

    print("\n=== Usuario 1 ===")
    print(consultar_usuario(session, 1))

    print("\n=== Total kg usuario 1 ===")
    print(total_kg_usuario(session, 1))

    print("\n=== Resumen por tipo ===")
    print(recolecciones_por_tipo(session, 1))

    print("\n=== Punto verde PV008 ===")
    print(consultar_punto_verde(session, "PV008"))

    print("\n=== Últimas recolecciones usuario ===")
    print(ultimas_recolecciones_usuario(session, 1))

    cluster.shutdown()


if __name__ == "__main__":
    main()