from cassandra.cluster import Cluster

def conectar():
    cluster = Cluster(['localhost'])
    session = cluster.connect('sira')
    return cluster, session


def consultar_usuario(session, usuario_id):

    rows = session.execute("""
        SELECT *
        FROM recolecciones_por_usuario
        WHERE usuario_id = %s
    """, [str(usuario_id)])

    for row in rows:
        print(row)


def consultar_punto_verde(session, punto_verde_id):

    rows = session.execute("""
        SELECT *
        FROM recolecciones_por_punto_verde
        WHERE punto_verde_id = %s
    """, [punto_verde_id])

    for row in rows:
        print(row)


def consultar_reciclador(session, reciclador_id):

    rows = session.execute("""
        SELECT *
        FROM retiros_por_reciclador
        WHERE reciclador_id = %s
    """, [reciclador_id])

    for row in rows:
        print(row)


def consultar_zona(session, zona):

    rows = session.execute("""
        SELECT *
        FROM actividad_por_zona
        WHERE zona = %s
    """, [zona])

    for row in rows:
        print(row)


def main():

    cluster, session = conectar()

    print("\n=== Recolecciones del usuario 1 ===")
    consultar_usuario(session, 1)

    print("\n=== Actividad del punto verde PV10 ===")
    consultar_punto_verde(session, "PV10")

    print("\n=== Retiros del reciclador RCL5 ===")
    consultar_reciclador(session, "RCL5")

    print("\n=== Actividad en Caballito ===")
    consultar_zona(session, "Caballito")

    cluster.shutdown()


if __name__ == "__main__":
    main()