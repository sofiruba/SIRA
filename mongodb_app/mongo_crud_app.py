from conexiones import obtener_colecciones_mongo


def crear_residuo(nombre, color_contenedor, categoria):
    _, coleccion_residuos = obtener_colecciones_mongo()

    ids = []

    for residuo in coleccion_residuos.find({}, {"id_residuo": 1}):
        try:
            numero = int(str(residuo["id_residuo"]).replace("R", ""))
            ids.append(numero)
        except:
            pass

    nuevo_id = f"R{max(ids) + 1}" if ids else "R1"

    nuevo_residuo = {
        "id_residuo": nuevo_id,
        "nombre": nombre,
        "color_contenedor": color_contenedor,
        "categoria": categoria
    }

    coleccion_residuos.insert_one(nuevo_residuo)

    return f"Residuo creado correctamente con ID {nuevo_id}"


def crear_punto_verde(nombre, direccion, barrio, comuna, residuos_aceptados, dias, apertura, cierre):
    coleccion_puntos, _ = obtener_colecciones_mongo()

    ultimo = coleccion_puntos.find_one({}, sort=[("id", -1)])
    nuevo_id = ultimo["id"] + 1 if ultimo else 1

    nuevo_punto = {
        "id": nuevo_id,
        "nombre": nombre,
        "residuos_aceptados": residuos_aceptados,
        "horario": {
            "dias": dias,
            "apertura": apertura,
            "cierre": cierre
        },
        "direccion": direccion,
        "barrio": barrio,
        "comuna": comuna
    }

    coleccion_puntos.insert_one(nuevo_punto)

    return f"Punto verde creado correctamente con ID {nuevo_id}"


def buscar_punto_verde_por_id(id_punto):
    coleccion_puntos, _ = obtener_colecciones_mongo()

    return coleccion_puntos.find_one(
        {"id": id_punto},
        {"_id": 0}
    )


def actualizar_horario_punto(id_punto, apertura, cierre):
    coleccion_puntos, _ = obtener_colecciones_mongo()

    resultado = coleccion_puntos.update_one(
        {"id": id_punto},
        {
            "$set": {
                "horario.apertura": apertura,
                "horario.cierre": cierre
            }
        }
    )

    if resultado.modified_count > 0:
        return "Horario actualizado correctamente."

    return "No se encontró el punto verde o no hubo cambios."


def actualizar_residuo(id_residuo, nombre, color_contenedor, categoria):
    _, coleccion_residuos = obtener_colecciones_mongo()

    resultado = coleccion_residuos.update_one(
        {"id_residuo": id_residuo},
        {
            "$set": {
                "nombre": nombre,
                "color_contenedor": color_contenedor,
                "categoria": categoria
            }
        }
    )

    if resultado.modified_count > 0:
        return "Residuo actualizado correctamente."

    return "No se encontró el residuo o no hubo cambios."


def eliminar_punto_verde(id_punto):
    coleccion_puntos, _ = obtener_colecciones_mongo()

    resultado = coleccion_puntos.delete_one({"id": id_punto})

    if resultado.deleted_count > 0:
        return "Punto verde eliminado correctamente."

    return "No se encontró un punto verde con ese ID."


def eliminar_residuo(id_residuo):
    coleccion_puntos, coleccion_residuos = obtener_colecciones_mongo()

    resultado = coleccion_residuos.delete_one({"id_residuo": id_residuo})

    coleccion_puntos.update_many(
        {},
        {
            "$pull": {
                "residuos_aceptados": id_residuo
            }
        }
    )

    if resultado.deleted_count > 0:
        return f"Residuo {id_residuo} eliminado correctamente."

    return "No se encontró un residuo con ese ID."

def buscar_punto_verde_por_barrio(coleccion_puntos, barrio):
    return list(coleccion_puntos.find(
        {"barrio": barrio},
        {"_id": 0}
    ))


def buscar_residuo_por_nombre(coleccion_residuos, nombre):
    return list(coleccion_residuos.find(
        {"nombre": {"$regex": nombre, "$options": "i"}},
        {"_id": 0}
    ))


def crear_muchos_puntos_verdes(coleccion_puntos, lista):
    coleccion_puntos.insert_many(lista)
    return f"{len(lista)} puntos verdes creados correctamente."


def crear_muchos_residuos(coleccion_residuos, lista):
    coleccion_residuos.insert_many(lista)
    return f"{len(lista)} residuos creados correctamente."


def eliminar_muchos_puntos_verdes(coleccion_puntos, ids):
    resultado = coleccion_puntos.delete_many({"id": {"$in": ids}})
    return f"Se eliminaron {resultado.deleted_count} puntos verdes."


def eliminar_muchos_residuos(coleccion_residuos, coleccion_puntos, codigos):
    resultado = coleccion_residuos.delete_many({"id_residuo": {"$in": codigos}})
    coleccion_puntos.update_many(
        {},
        {"$pull": {"residuos_aceptados": {"$in": codigos}}}
    )
    return f"Se eliminaron {resultado.deleted_count} residuos."


def agregar_campo_activo(coleccion_puntos):
    resultado = coleccion_puntos.update_many({}, {"$set": {"activo": True}})
    return f"Campo activo agregado a {resultado.modified_count} documentos."


def eliminar_campo_activo(coleccion_puntos):
    resultado = coleccion_puntos.update_many({}, {"$unset": {"activo": ""}})
    return f"Campo activo eliminado de {resultado.modified_count} documentos."
