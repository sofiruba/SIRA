from conexiones import obtener_colecciones_mongo
import re


coleccion_puntos, coleccion_residuos = obtener_colecciones_mongo()


def _normalizar_texto(texto):
    if texto is None:
        return ""
    return str(texto).strip()


def _normalizar_titulo(texto):
    return _normalizar_texto(texto).title()


def _regex_exacto(texto):
    texto = _normalizar_texto(texto)
    return {"$regex": f"^{re.escape(texto)}$", "$options": "i"}


def _regex_contiene(texto):
    texto = _normalizar_texto(texto)
    return {"$regex": re.escape(texto), "$options": "i"}


def _limpiar_id_residuo(id_residuo):
    return _normalizar_texto(id_residuo).upper()


def buscar_punto_verde_por_barrio(coleccion, barrio):
    barrio = _normalizar_texto(barrio)

    if not barrio:
        return []

    return list(coleccion.find(
        {"barrio": _regex_exacto(barrio)},
        {"_id": 0}
    ))


def buscar_punto_verde_por_id(id_punto):
    try:
        id_punto = int(id_punto)
    except ValueError:
        return None

    return coleccion_puntos.find_one(
        {"id": id_punto},
        {"_id": 0}
    )


def buscar_residuo_por_nombre(coleccion, nombre):
    nombre = _normalizar_texto(nombre)

    if not nombre:
        return []

    return list(coleccion.find(
        {"nombre": _regex_contiene(nombre)},
        {"_id": 0}
    ))


def crear_residuo(nombre, color, categoria):
    nombre = _normalizar_titulo(nombre)
    color = _normalizar_titulo(color)
    categoria = _normalizar_titulo(categoria)

    if not nombre or not color or not categoria:
        return "No se pudo crear el residuo: faltan datos."

    existente = coleccion_residuos.find_one({
        "nombre": _regex_exacto(nombre)
    })

    if existente:
        return f"Ya existe un residuo con el nombre '{nombre}'."

    ultimo = coleccion_residuos.find_one(
        sort=[("id", -1)]
    )

    if ultimo and "id" in ultimo:
        try:
            ultimo_numero = int(str(ultimo["id"]).replace("R", ""))
            nuevo_id = f"R{ultimo_numero + 1}"
        except Exception:
            nuevo_id = "R1"
    else:
        nuevo_id = "R1"

    nuevo_residuo = {
        "id": nuevo_id,
        "nombre": nombre,
        "color_contenedor": color,
        "categoria": categoria
    }

    coleccion_residuos.insert_one(nuevo_residuo)

    return f"Residuo {nuevo_id} creado correctamente."


def crear_punto_verde(
    nombre,
    direccion,
    barrio,
    comuna,
    residuos_aceptados,
    dias_atencion,
    hora_apertura,
    hora_cierre
):
    nombre = _normalizar_texto(nombre)
    direccion = _normalizar_texto(direccion)
    barrio = _normalizar_titulo(barrio)
    comuna = _normalizar_titulo(comuna)
    hora_apertura = _normalizar_texto(hora_apertura)
    hora_cierre = _normalizar_texto(hora_cierre)

    residuos_aceptados = [
        _limpiar_id_residuo(r)
        for r in residuos_aceptados
        if _normalizar_texto(r)
    ]

    dias_atencion = [
        _normalizar_titulo(d)
        for d in dias_atencion
        if _normalizar_texto(d)
    ]

    if not all([nombre, direccion, barrio, comuna, residuos_aceptados, dias_atencion, hora_apertura, hora_cierre]):
        return "No se pudo crear el punto verde: faltan datos."

    existente = coleccion_puntos.find_one({
        "nombre": _regex_exacto(nombre),
        "direccion": _regex_exacto(direccion)
    })

    if existente:
        return f"Ya existe un punto verde con nombre '{nombre}' en esa dirección."

    ultimo = coleccion_puntos.find_one(
        sort=[("id", -1)]
    )

    nuevo_id = int(ultimo["id"]) + 1 if ultimo and "id" in ultimo else 1

    nuevo_punto = {
        "id": nuevo_id,
        "nombre": nombre,
        "direccion": direccion,
        "barrio": barrio,
        "comuna": comuna,
        "residuos_aceptados": residuos_aceptados,
        "horario": {
            "dias": dias_atencion,
            "apertura": hora_apertura,
            "cierre": hora_cierre
        }
    }

    coleccion_puntos.insert_one(nuevo_punto)

    return f"Punto verde {nuevo_id} creado correctamente."


def crear_muchos_puntos_verdes(coleccion, lista_puntos):
    if not isinstance(lista_puntos, list) or not lista_puntos:
        return "La lista de puntos verdes está vacía o no es válida."

    puntos_normalizados = []

    for punto in lista_puntos:
        punto_limpio = dict(punto)

        if "barrio" in punto_limpio:
            punto_limpio["barrio"] = _normalizar_titulo(punto_limpio["barrio"])

        if "comuna" in punto_limpio:
            punto_limpio["comuna"] = _normalizar_titulo(punto_limpio["comuna"])

        if "residuos_aceptados" in punto_limpio and isinstance(punto_limpio["residuos_aceptados"], list):
            punto_limpio["residuos_aceptados"] = [
                _limpiar_id_residuo(r)
                for r in punto_limpio["residuos_aceptados"]
            ]

        puntos_normalizados.append(punto_limpio)

    resultado = coleccion.insert_many(puntos_normalizados)

    return f"Se crearon {len(resultado.inserted_ids)} puntos verdes correctamente."


def crear_muchos_residuos(coleccion, lista_residuos):
    if not isinstance(lista_residuos, list) or not lista_residuos:
        return "La lista de residuos está vacía o no es válida."

    residuos_normalizados = []

    for residuo in lista_residuos:
        residuo_limpio = dict(residuo)

        if "id" in residuo_limpio:
            residuo_limpio["id"] = _limpiar_id_residuo(residuo_limpio["id"])

        if "nombre" in residuo_limpio:
            residuo_limpio["nombre"] = _normalizar_titulo(residuo_limpio["nombre"])

        if "color_contenedor" in residuo_limpio:
            residuo_limpio["color_contenedor"] = _normalizar_titulo(residuo_limpio["color_contenedor"])

        if "categoria" in residuo_limpio:
            residuo_limpio["categoria"] = _normalizar_titulo(residuo_limpio["categoria"])

        residuos_normalizados.append(residuo_limpio)

    resultado = coleccion.insert_many(residuos_normalizados)

    return f"Se crearon {len(resultado.inserted_ids)} residuos correctamente."


def actualizar_horario_punto(id_punto, nueva_apertura, nuevo_cierre):
    try:
        id_punto = int(id_punto)
    except ValueError:
        return "ID inválido."

    nueva_apertura = _normalizar_texto(nueva_apertura)
    nuevo_cierre = _normalizar_texto(nuevo_cierre)

    resultado = coleccion_puntos.update_one(
        {"id": id_punto},
        {
            "$set": {
                "horario.apertura": nueva_apertura,
                "horario.cierre": nuevo_cierre
            }
        }
    )

    if resultado.matched_count == 0:
        return f"No se encontró el punto verde {id_punto}."

    return f"Horario del punto verde {id_punto} actualizado correctamente."


def actualizar_residuo(id_residuo, nuevo_nombre, nuevo_color, nueva_categoria):
    id_residuo = _limpiar_id_residuo(id_residuo)
    nuevo_nombre = _normalizar_titulo(nuevo_nombre)
    nuevo_color = _normalizar_titulo(nuevo_color)
    nueva_categoria = _normalizar_titulo(nueva_categoria)

    if not all([id_residuo, nuevo_nombre, nuevo_color, nueva_categoria]):
        return "No se pudo actualizar el residuo: faltan datos."

    resultado = coleccion_residuos.update_one(
        {"id": id_residuo},
        {
            "$set": {
                "nombre": nuevo_nombre,
                "color_contenedor": nuevo_color,
                "categoria": nueva_categoria
            }
        }
    )

    if resultado.matched_count == 0:
        return f"No se encontró el residuo {id_residuo}."

    return f"Residuo {id_residuo} actualizado correctamente."


def agregar_campo_activo(coleccion):
    resultado = coleccion.update_many(
        {},
        {"$set": {"activo": True}}
    )

    return f"Campo activo agregado a {resultado.modified_count} documentos."


def eliminar_campo_activo(coleccion):
    resultado = coleccion.update_many(
        {},
        {"$unset": {"activo": ""}}
    )

    return f"Campo activo eliminado de {resultado.modified_count} documentos."


def eliminar_punto_verde(id_punto):
    try:
        id_punto = int(id_punto)
    except ValueError:
        return "ID inválido."

    resultado = coleccion_puntos.delete_one(
        {"id": id_punto}
    )

    if resultado.deleted_count == 0:
        return f"No se encontró el punto verde {id_punto}."

    return f"Punto verde {id_punto} eliminado correctamente."


def eliminar_residuo(id_residuo):
    id_residuo = _limpiar_id_residuo(id_residuo)

    resultado = coleccion_residuos.delete_one(
        {"id": id_residuo}
    )

    if resultado.deleted_count == 0:
        return f"No se encontró el residuo {id_residuo}."

    coleccion_puntos.update_many(
        {"residuos_aceptados": id_residuo},
        {"$pull": {"residuos_aceptados": id_residuo}}
    )

    return f"Residuo {id_residuo} eliminado correctamente."


def eliminar_muchos_puntos_verdes(coleccion, ids):
    ids_normalizados = []

    for id_punto in ids:
        try:
            ids_normalizados.append(int(id_punto))
        except ValueError:
            pass

    if not ids_normalizados:
        return "No se ingresaron IDs válidos."

    resultado = coleccion.delete_many(
        {"id": {"$in": ids_normalizados}}
    )

    return f"Se eliminaron {resultado.deleted_count} puntos verdes."


def eliminar_muchos_residuos(coleccion_residuos_param, coleccion_puntos_param, codigos):
    codigos = [
        _limpiar_id_residuo(c)
        for c in codigos
        if _normalizar_texto(c)
    ]

    if not codigos:
        return "No se ingresaron códigos válidos."

    resultado = coleccion_residuos_param.delete_many(
        {"id": {"$in": codigos}}
    )

    coleccion_puntos_param.update_many(
        {"residuos_aceptados": {"$in": codigos}},
        {"$pull": {"residuos_aceptados": {"$in": codigos}}}
    )

    return f"Se eliminaron {resultado.deleted_count} residuos."