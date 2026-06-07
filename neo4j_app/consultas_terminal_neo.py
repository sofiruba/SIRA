from neo4j import GraphDatabase

# =====================================
# CONEXIÓN A NEO4J
# =====================================

driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j", "Homero1234")
)

# =====================================
# TODAS LAS CONSULTAS VAN DENTRO DEL
# WITH DRIVER.SESSION()
# =====================================

with driver.session(database="sira") as session:

    # ---------------------------------
    # PUNTOS VERDES CERCANOS
    # ---------------------------------

    resultado = session.run("""
        MATCH (u:Usuario)-[:TIENE_PUNTO_CERCANO]->(p:PuntoVerde)

        RETURN u.nombre AS usuario,
               p.nombre AS punto_verde

        LIMIT 15
    """)

    print("\n=== PUNTOS VERDES CERCANOS ===")

    for fila in resultado:
        print(fila["usuario"], "->", fila["punto_verde"])

    # ---------------------------------
    # USUARIOS POR BARRIO
    # ---------------------------------

    resultado = session.run("""
        MATCH (u:Usuario)

        RETURN u.barrio AS barrio,
               count(*) AS cantidad

        ORDER BY cantidad DESC
    """)

    print("\n=== USUARIOS POR BARRIO ===")

    for fila in resultado:
        print(fila["barrio"], ":", fila["cantidad"])

    # ---------------------------------
    # PUNTOS VERDES POR COMUNA
    # ---------------------------------

    resultado = session.run("""
        MATCH (p:PuntoVerde)

        RETURN p.comuna AS comuna,
               count(*) AS cantidad

        ORDER BY cantidad DESC
    """)

    print("\n=== PUNTOS VERDES POR COMUNA ===")

    for fila in resultado:
        print(fila["comuna"], ":", fila["cantidad"])

    # ---------------------------------
    # TOP USUARIOS
    # ---------------------------------

    resultado = session.run("""
        MATCH (u:Usuario)

        RETURN u.nombre AS nombre,
               u.puntos_ecologicos AS puntos

        ORDER BY puntos DESC

        LIMIT 10
    """)

    print("\n=== TOP 10 USUARIOS ===")

    for fila in resultado:
        print(fila["nombre"], "-", fila["puntos"])

    # ---------------------------------
    # USUARIOS Y RESIDUOS
    # ---------------------------------

    resultado = session.run("""
        MATCH (u:Usuario)-[:RECICLA]->(r:TipoResiduo)

        RETURN u.nombre AS usuario,
               r.nombre AS residuo

        LIMIT 15
    """)

    print("\n=== USUARIOS Y RESIDUOS ===")

    for fila in resultado:
        print(fila["usuario"], "->", fila["residuo"])

    # ---------------------------------
    # PUNTOS VERDES Y RESIDUOS
    # ---------------------------------

    resultado = session.run("""
        MATCH (p:PuntoVerde)-[:ACEPTA]->(r:TipoResiduo)

        RETURN p.nombre AS punto,
               r.nombre AS residuo

        LIMIT 15
    """)

    print("\n=== RESIDUOS ACEPTADOS ===")

    for fila in resultado:
        print(fila["punto"], "acepta", fila["residuo"])

    # ---------------------------------
    # RECICLADORES Y RESIDUOS
    # ---------------------------------

    resultado = session.run("""
        MATCH (rec:Reciclador)-[:RECOLECTA]->(r:TipoResiduo)

        RETURN rec.nombre AS reciclador,
               r.nombre AS residuo

        LIMIT 15
    """)

    print("\n=== RECOLECTORES ===")

    for fila in resultado:
        print(fila["reciclador"], "->", fila["residuo"])

    # ---------------------------------
    # RECICLADORES Y PUNTOS VERDES
    # ---------------------------------

    resultado = session.run("""
        MATCH (rec:Reciclador)-[:RETIRA_DE]->(p:PuntoVerde)

        RETURN rec.nombre AS reciclador,
               p.nombre AS punto

        LIMIT 15
    """)

    print("\n=== RETIRO DE PUNTOS VERDES ===")

    for fila in resultado:
        print(fila["reciclador"], "->", fila["punto"])

    # ---------------------------------
    # RESIDUOS MÁS RECICLADOS
    # ---------------------------------

    resultado = session.run("""
        MATCH (:Usuario)-[:RECICLA]->(r:TipoResiduo)

        RETURN r.nombre AS residuo,
               count(*) AS cantidad

        ORDER BY cantidad DESC
    """)

    print("\n=== RESIDUOS MÁS RECICLADOS ===")

    for fila in resultado:
        print(fila["residuo"], ":", fila["cantidad"])

    # ---------------------------------
    # TIPOS DE RESIDUOS POR PUNTO VERDE
    # ---------------------------------

    resultado = session.run("""
        MATCH (p:PuntoVerde)-[:ACEPTA]->(r:TipoResiduo)

        RETURN p.nombre AS punto,
               count(r) AS cantidad

        ORDER BY cantidad DESC
    """)

    print("\n=== TIPOS DE RESIDUOS POR PUNTO VERDE ===")

    for fila in resultado:
        print(fila["punto"], ":", fila["cantidad"])

    # ---------------------------------
    # USUARIOS POR NIVEL
    # ---------------------------------

    resultado = session.run("""
        MATCH (u:Usuario)

        RETURN u.nivel_usuario AS nivel,
               count(*) AS cantidad

        ORDER BY cantidad DESC
    """)

    print("\n=== USUARIOS POR NIVEL ===")

    for fila in resultado:
        print(fila["nivel"], ":", fila["cantidad"])

    # ---------------------------------
    # TOTAL DE NODOS
    # ---------------------------------

    resultado = session.run("""
        MATCH (n)

        RETURN count(n) AS total
    """)

    print("\n=== TOTAL DE NODOS ===")
    print(resultado.single()["total"])

    # ---------------------------------
    # TOTAL DE RELACIONES
    # ---------------------------------

    resultado = session.run("""
        MATCH ()-[r]->()

        RETURN count(r) AS total
    """)

    print("\n=== TOTAL DE RELACIONES ===")
    print(resultado.single()["total"])

# =====================================
# CERRAR CONEXIÓN
# =====================================

driver.close()
print("\nConexión cerrada.")