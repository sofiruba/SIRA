from conexiones import obtener_driver_neo4j, NEO4J_DATABASE

def ejecutar_write(query, parametros=None):
    driver = obtener_driver_neo4j()
    try:
        # Usamos un bloque contextual para la sesión
        with driver.session(database=NEO4J_DATABASE) as session:
            # execute_write asegura que los cambios se guarden de forma atómica en el disco
            def transaccion(tx):
                resultado = tx.run(query, parametros or {})
                return [dict(fila) for fila in resultado]
            return session.execute_write(transaccion)
    finally:
        driver.close()


def siguiente_id(etiqueta, campo):
    driver = obtener_driver_neo4j()
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            def transaccion(tx):
                resultado = tx.run(f"MATCH (n:{etiqueta}) RETURN coalesce(max(n.{campo}), 0) AS ultimo")
                return resultado.single()["ultimo"] + 1
            return session.execute_read(transaccion) # Para leer usamos execute_read
    finally:
        driver.close()


# ══════════════════════════════════════════════════════════════════════════════
#  USUARIO (CORREGIDO)
# ══════════════════════════════════════════════════════════════════════════════

def crear_usuario(nombre, email, barrio, comuna):
    nuevo_id = siguiente_id("Usuario", "id_usuario")

    # Nos aseguramos de que las variables coincidan perfectamente
    ejecutar_write("""
        CREATE (u:Usuario {
            id_usuario: $id_usuario,
            nombre: $nombre,
            email: $email,
            barrio: $barrio,
            comuna: $comuna,
            puntos_ecologicos: 0,
            nivel_usuario: 'Novato'
        })
    """, {
        "id_usuario": nuevo_id,
        "nombre": nombre,
        "email": email,
        "barrio": barrio,
        "comuna": comuna
    })

    return f"Usuario creado correctamente con ID {nuevo_id}"


def actualizar_puntos_usuario(id_usuario, puntos):
    datos = ejecutar_write("""
        MATCH (u:Usuario {id_usuario: $id_usuario})
        SET u.puntos_ecologicos = $puntos
        RETURN u.nombre AS nombre
    """, {
        "id_usuario": int(id_usuario), # Forzamos entero por si Streamlit lo envía como string
        "puntos": int(puntos)
    })

    if datos:
        return f"Usuario actualizado: {datos[0]['nombre']}"

    return "No se encontró el usuario."


def eliminar_usuario(id_usuario):
    ejecutar_write("""
        MATCH (u:Usuario {id_usuario: $id_usuario})
        DETACH DELETE u
    """, {
        "id_usuario": int(id_usuario)
    })

    return "Usuario eliminado correctamente."
# ══════════════════════════════════════════════════════════════════════════════
#  TIPO DE RESIDUO
# ══════════════════════════════════════════════════════════════════════════════
 
def crear_tipo_residuo(nombre, categoria, color):
    nuevo_id = siguiente_id("TipoResiduo", "id_residuo")
 
    ejecutar_write("""
        CREATE (r:TipoResiduo {
            id_residuo: $id,
            nombre: $nombre,
            categoria: $categoria,
            color_contenedor: $color
        })
    """, {
        "id": nuevo_id,
        "nombre": nombre,
        "categoria": categoria,
        "color": color
    })
 
    return f"Tipo de Residuo creado correctamente con ID {nuevo_id}"
 
 
def modificar_tipo_residuo(id_residuo, nombre, categoria, color):
    datos = ejecutar_write("""
        MATCH (r:TipoResiduo {id_residuo: $id})
        SET r.nombre = $nombre,
            r.categoria = $categoria,
            r.color_contenedor = $color
        RETURN r.nombre AS nombre
    """, {
        "id": id_residuo,
        "nombre": nombre,
        "categoria": categoria,
        "color": color
    })
 
    if datos:
        return f"Tipo de Residuo actualizado correctamente."
 
    return "No se encontró el tipo de residuo."
 
 
def eliminar_tipo_residuo(id_residuo):
    ejecutar_write("""
        MATCH (r:TipoResiduo {id_residuo: $id})
        DETACH DELETE r
    """, {
        "id": id_residuo
    })
 
    return "Tipo de Residuo eliminado correctamente."
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  PUNTO VERDE
# ══════════════════════════════════════════════════════════════════════════════
 
def crear_punto_verde(nombre, direccion, barrio, comuna):
    nuevo_id = siguiente_id("PuntoVerde", "id")
 
    ejecutar_write("""
        CREATE (p:PuntoVerde {
            id: $id,
            nombre: $nombre,
            direccion: $direccion,
            barrio: $barrio,
            comuna: $comuna
        })
    """, {
        "id": nuevo_id,
        "nombre": nombre,
        "direccion": direccion,
        "barrio": barrio,
        "comuna": comuna
    })
 
    return f"Punto Verde creado correctamente con ID {nuevo_id}"
 
 
def modificar_punto_verde(id_punto, nombre, direccion):
    datos = ejecutar_write("""
        MATCH (p:PuntoVerde {id: $id})
        SET p.nombre = $nombre,
            p.direccion = $direccion
        RETURN p.nombre AS nombre
    """, {
        "id": id_punto,
        "nombre": nombre,
        "direccion": direccion
    })
 
    if datos:
        return "Punto Verde actualizado correctamente."
 
    return "No se encontró el punto verde."
 
 
def eliminar_punto_verde(id_punto):
    ejecutar_write("""
        MATCH (p:PuntoVerde {id: $id})
        DETACH DELETE p
    """, {
        "id": id_punto
    })
 
    return "Punto Verde eliminado correctamente."
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  RECICLADOR
# ══════════════════════════════════════════════════════════════════════════════
 
def crear_reciclador(nombre, tipo, direccion, barrio, comuna):
    nuevo_id = siguiente_id("Reciclador", "id")
 
    ejecutar_write("""
        CREATE (r:Reciclador {
            id: $id,
            nombre: $nombre,
            tipo: $tipo,
            direccion: $direccion,
            barrio: $barrio,
            comuna: $comuna
        })
    """, {
        "id": nuevo_id,
        "nombre": nombre,
        "tipo": tipo,
        "direccion": direccion,
        "barrio": barrio,
        "comuna": comuna
    })
 
    return f"Reciclador creado correctamente con ID {nuevo_id}"
 
 
def modificar_reciclador(id_reciclador, nombre, tipo):
    datos = ejecutar_write("""
        MATCH (r:Reciclador {id: $id})
        SET r.nombre = $nombre,
            r.tipo = $tipo
        RETURN r.nombre AS nombre
    """, {
        "id": id_reciclador,
        "nombre": nombre,
        "tipo": tipo
    })
 
    if datos:
        return "Reciclador actualizado correctamente."
 
    return "No se encontró el reciclador."
 
 
def eliminar_reciclador(id_reciclador):
    ejecutar_write("""
        MATCH (r:Reciclador {id: $id})
        DETACH DELETE r
    """, {
        "id": id_reciclador
    })
 
    return "Reciclador eliminado correctamente."
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  RELACIONES
# ══════════════════════════════════════════════════════════════════════════════
 
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
 
 
def eliminar_relacion_recicla(id_usuario, id_residuo):
    ejecutar_write("""
        MATCH (u:Usuario {id_usuario: $id_usuario})-[rel:RECICLA]->(r:TipoResiduo {id_residuo: $id_residuo})
        DELETE rel
    """, {
        "id_usuario": id_usuario,
        "id_residuo": id_residuo
    })
 
    return "Relación RECICLA eliminada correctamente."
 
 
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
 
 
def eliminar_relacion_entrega_en(id_usuario, id_punto):
    ejecutar_write("""
        MATCH (u:Usuario {id_usuario: $id_usuario})-[rel:ENTREGA_EN]->(p:PuntoVerde {id: $id_punto})
        DELETE rel
    """, {
        "id_usuario": id_usuario,
        "id_punto": id_punto
    })
 
    return "Relación ENTREGA_EN eliminada correctamente."
 
 
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
 
 
def eliminar_relacion_acepta(id_punto, id_residuo):
    ejecutar_write("""
        MATCH (p:PuntoVerde {id: $id_punto})-[rel:ACEPTA]->(r:TipoResiduo {id_residuo: $id_residuo})
        DELETE rel
    """, {
        "id_punto": id_punto,
        "id_residuo": id_residuo
    })
 
    return "Relación ACEPTA eliminada correctamente."
 
 
def crear_relacion_recolecta(id_reciclador, id_residuo):
    ejecutar_write("""
        MATCH (rc:Reciclador {id: $id_reciclador})
        MATCH (r:TipoResiduo {id_residuo: $id_residuo})
        MERGE (rc)-[:RECOLECTA]->(r)
    """, {
        "id_reciclador": id_reciclador,
        "id_residuo": id_residuo
    })
 
    return "Relación RECOLECTA creada correctamente."
 
 
def eliminar_relacion_recolecta(id_reciclador, id_residuo):
    ejecutar_write("""
        MATCH (rc:Reciclador {id: $id_reciclador})-[rel:RECOLECTA]->(r:TipoResiduo {id_residuo: $id_residuo})
        DELETE rel
    """, {
        "id_reciclador": id_reciclador,
        "id_residuo": id_residuo
    })
 
    return "Relación RECOLECTA eliminada correctamente."
 
 
def crear_relacion_retira_de(id_reciclador, id_punto):
    ejecutar_write("""
        MATCH (rc:Reciclador {id: $id_reciclador})
        MATCH (p:PuntoVerde {id: $id_punto})
        MERGE (rc)-[:RETIRA_DE]->(p)
    """, {
        "id_reciclador": id_reciclador,
        "id_punto": id_punto
    })
 
    return "Relación RETIRA_DE creada correctamente."
 
 
def eliminar_relacion_retira_de(id_reciclador, id_punto):
    ejecutar_write("""
        MATCH (rc:Reciclador {id: $id_reciclador})-[rel:RETIRA_DE]->(p:PuntoVerde {id: $id_punto})
        DELETE rel
    """, {
        "id_reciclador": id_reciclador,
        "id_punto": id_punto
    })
 
    return "Relación RETIRA_DE eliminada correctamente."
 
 
def crear_relacion_punto_cercano(id_usuario, id_punto):
    ejecutar_write("""
        MATCH (u:Usuario {id_usuario: $id_usuario})
        MATCH (p:PuntoVerde {id: $id_punto})
        MERGE (u)-[:TIENE_PUNTO_CERCANO]->(p)
    """, {
        "id_usuario": id_usuario,
        "id_punto": id_punto
    })
 
    return "Relación TIENE_PUNTO_CERCANO creada correctamente."
 
 
def eliminar_relacion_punto_cercano(id_usuario, id_punto):
    ejecutar_write("""
        MATCH (u:Usuario {id_usuario: $id_usuario})-[rel:TIENE_PUNTO_CERCANO]->(p:PuntoVerde {id: $id_punto})
        DELETE rel
    """, {
        "id_usuario": id_usuario,
        "id_punto": id_punto
    })
 
    return "Relación TIENE_PUNTO_CERCANO eliminada correctamente."