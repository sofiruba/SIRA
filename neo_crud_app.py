from conexiones import obtener_driver_neo4j, NEO4J_DATABASE


def ejecutar_write(query, parametros=None):
    driver = obtener_driver_neo4j()

    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            resultado = session.run(query, parametros or {})
            return [dict(fila) for fila in resultado]
    finally:
        driver.close()


def siguiente_id(etiqueta, campo):
    driver = obtener_driver_neo4j()

    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            resultado = session.run(
                f"MATCH (n:{etiqueta}) RETURN coalesce(max(n.{campo}), 0) AS ultimo"
            )
            return resultado.single()["ultimo"] + 1
    finally:
        driver.close()


def crear_usuario(nombre, email, barrio, comuna):
    nuevo_id = siguiente_id("Usuario", "id_usuario")

    ejecutar_write("""
        CREATE (u:Usuario {
            id_usuario: $id,
            nombre: $nombre,
            email: $email,
            barrio: $barrio,
            comuna: $comuna,
            puntos_ecologicos: 0,
            nivel_usuario: 'Novato'
        })
    """, {
        "id": nuevo_id,
        "nombre": nombre,
        "email": email,
        "barrio": barrio,
        "comuna": comuna
    })

    return f"Usuario creado correctamente con ID {nuevo_id}"


def actualizar_puntos_usuario(id_usuario, puntos):
    datos = ejecutar_write("""
        MATCH (u:Usuario {id_usuario: $id})
        SET u.puntos_ecologicos = $puntos
        RETURN u.nombre AS nombre
    """, {
        "id": id_usuario,
        "puntos": puntos
    })

    if datos:
        return f"Usuario actualizado: {datos[0]['nombre']}"

    return "No se encontró el usuario."


def eliminar_usuario(id_usuario):
    ejecutar_write("""
        MATCH (u:Usuario {id_usuario: $id})
        DETACH DELETE u
    """, {
        "id": id_usuario
    })

    return "Usuario eliminado correctamente."


def crear_relacion_recicla(id_usuario, id_residuo):
    ejecutar_write("""
        MATCH (u:Usuario {id_usuario: $id_usuario})
        MATCH (r:TipoResiduo {id_residuo: $id_residuo})
        MERGE (u)-[:RECICLA]->(r)
    """, {
        "id_usuario": id_usuario,
        "id_residuo": id_residuo
    })

    return "Relación RECICLA creada correctamente."


def crear_relacion_entrega_en(id_usuario, id_punto):
    ejecutar_write("""
        MATCH (u:Usuario {id_usuario: $id_usuario})
        MATCH (p:PuntoVerde {id: $id_punto})
        MERGE (u)-[:ENTREGA_EN]->(p)
    """, {
        "id_usuario": id_usuario,
        "id_punto": id_punto
    })

    return "Relación ENTREGA_EN creada correctamente."


def crear_relacion_acepta(id_punto, id_residuo):
    ejecutar_write("""
        MATCH (p:PuntoVerde {id: $id_punto})
        MATCH (r:TipoResiduo {id_residuo: $id_residuo})
        MERGE (p)-[:ACEPTA]->(r)
    """, {
        "id_punto": id_punto,
        "id_residuo": id_residuo
    })

    return "Relación ACEPTA creada correctamente."


def eliminar_relacion_recicla(id_usuario, id_residuo):
    ejecutar_write("""
        MATCH (u:Usuario {id_usuario: $id_usuario})-[rel:RECICLA]->(r:TipoResiduo {id_residuo: $id_residuo})
        DELETE rel
    """, {
        "id_usuario": id_usuario,
        "id_residuo": id_residuo
    })

    return "Relación RECICLA eliminada correctamente."