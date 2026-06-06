from neo4j import GraphDatabase

# =====================================
# CONEXIÓN A NEO4J
# =====================================

URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "Homero1234")


def get_driver():
    return GraphDatabase.driver(URI, auth=AUTH)


# =====================================
# CONSULTAS
# =====================================

def puntos_verdes_cercanos(session, limit=15):
    resultado = session.run("""
        MATCH (u:Usuario)-[:TIENE_PUNTO_CERCANO]->(p:PuntoVerde)
        RETURN u.nombre AS usuario,
               p.nombre AS punto_verde
        LIMIT $limit
    """, limit=limit)

    print("\n=== PUNTOS VERDES CERCANOS ===")
    for fila in resultado:
        print(fila["usuario"], "->", fila["punto_verde"])


def usuarios_por_barrio(session):
    resultado = session.run("""
        MATCH (u:Usuario)
        RETURN u.barrio AS barrio,
               count(*) AS cantidad
        ORDER BY cantidad DESC
    """)

    print("\n=== USUARIOS POR BARRIO ===")
    for fila in resultado:
        print(fila["barrio"], ":", fila["cantidad"])


def puntos_verdes_por_comuna(session):
    resultado = session.run("""
        MATCH (p:PuntoVerde)
        RETURN p.comuna AS comuna,
               count(*) AS cantidad
        ORDER BY cantidad DESC
    """)

    print("\n=== PUNTOS VERDES POR COMUNA ===")
    for fila in resultado:
        print(fila["comuna"], ":", fila["cantidad"])


def top_usuarios(session, limit=10):
    resultado = session.run("""
        MATCH (u:Usuario)
        RETURN u.nombre AS nombre,
               u.puntos_ecologicos AS puntos
        ORDER BY puntos DESC
        LIMIT $limit
    """, limit=limit)

    print(f"\n=== TOP {limit} USUARIOS ===")
    for fila in resultado:
        print(fila["nombre"], "-", fila["puntos"])


def usuarios_y_residuos(session, limit=15):
    resultado = session.run("""
        MATCH (u:Usuario)-[:RECICLA]->(r:TipoResiduo)
        RETURN u.nombre AS usuario,
               r.nombre AS residuo
        LIMIT $limit
    """, limit=limit)

    print("\n=== USUARIOS Y RESIDUOS ===")
    for fila in resultado:
        print(fila["usuario"], "->", fila["residuo"])


def puntos_verdes_y_residuos(session, limit=15):
    resultado = session.run("""
        MATCH (p:PuntoVerde)-[:ACEPTA]->(r:TipoResiduo)
        RETURN p.nombre AS punto,
               r.nombre AS residuo
        LIMIT $limit
    """, limit=limit)

    print("\n=== RESIDUOS ACEPTADOS ===")
    for fila in resultado:
        print(fila["punto"], "acepta", fila["residuo"])


def recicladores_y_residuos(session, limit=15):
    resultado = session.run("""
        MATCH (rec:Reciclador)-[:RECOLECTA]->(r:TipoResiduo)
        RETURN rec.nombre AS reciclador,
               r.nombre AS residuo
        LIMIT $limit
    """, limit=limit)

    print("\n=== RECOLECTORES ===")
    for fila in resultado:
        print(fila["reciclador"], "->", fila["residuo"])


def recicladores_y_puntos_verdes(session, limit=15):
    resultado = session.run("""
        MATCH (rec:Reciclador)-[:RETIRA_DE]->(p:PuntoVerde)
        RETURN rec.nombre AS reciclador,
               p.nombre AS punto
        LIMIT $limit
    """, limit=limit)

    print("\n=== RETIRO DE PUNTOS VERDES ===")
    for fila in resultado:
        print(fila["reciclador"], "->", fila["punto"])


def residuos_mas_reciclados(session):
    resultado = session.run("""
        MATCH (:Usuario)-[:RECICLA]->(r:TipoResiduo)
        RETURN r.nombre AS residuo,
               count(*) AS cantidad
        ORDER BY cantidad DESC
    """)

    print("\n=== RESIDUOS MÁS RECICLADOS ===")
    for fila in resultado:
        print(fila["residuo"], ":", fila["cantidad"])


def tipos_residuos_por_punto_verde(session):
    resultado = session.run("""
        MATCH (p:PuntoVerde)-[:ACEPTA]->(r:TipoResiduo)
        RETURN p.nombre AS punto,
               count(r) AS cantidad
        ORDER BY cantidad DESC
    """)

    print("\n=== TIPOS DE RESIDUOS POR PUNTO VERDE ===")
    for fila in resultado:
        print(fila["punto"], ":", fila["cantidad"])


def usuarios_por_nivel(session):
    resultado = session.run("""
        MATCH (u:Usuario)
        RETURN u.nivel_usuario AS nivel,
               count(*) AS cantidad
        ORDER BY cantidad DESC
    """)

    print("\n=== USUARIOS POR NIVEL ===")
    for fila in resultado:
        print(fila["nivel"], ":", fila["cantidad"])


def total_nodos(session):
    resultado = session.run("""
        MATCH (n)
        RETURN count(n) AS total
    """)

    print("\n=== TOTAL DE NODOS ===")
    print(resultado.single()["total"])


def total_relaciones(session):
    resultado = session.run("""
        MATCH ()-[r]->()
        RETURN count(r) AS total
    """)

    print("\n=== TOTAL DE RELACIONES ===")
    print(resultado.single()["total"])


# =====================================
# EJECUCIÓN PRINCIPAL
# =====================================

def main():
    driver = get_driver()

    with driver.session() as session:
        puntos_verdes_cercanos(session)
        usuarios_por_barrio(session)
        puntos_verdes_por_comuna(session)
        top_usuarios(session)
        usuarios_y_residuos(session)
        puntos_verdes_y_residuos(session)
        recicladores_y_residuos(session)
        recicladores_y_puntos_verdes(session)
        residuos_mas_reciclados(session)
        tipos_residuos_por_punto_verde(session)
        usuarios_por_nivel(session)
        total_nodos(session)
        total_relaciones(session)

    driver.close()
    print("\nConexión cerrada.")


if __name__ == "__main__":
    main()