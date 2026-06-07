from datetime import datetime
import carga_redis as redis_mod


def actualizar_estado_punto(id_punto, estado, capacidad_actual):
    id_punto = str(id_punto)

    ultima_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    clave = f"puntoverde:{id_punto}:estado"

    redis_mod.r.hset(
        clave,
        mapping={
            "estado": estado,
            "capacidad_actual": capacidad_actual,
            "ultima_actualizacion": ultima_actualizacion
        }
    )

    redis_mod.r.srem("puntosverdes:disponibles", id_punto)
    redis_mod.r.srem("puntosverdes:saturados", id_punto)

    if estado == "disponible":
        redis_mod.r.sadd("puntosverdes:disponibles", id_punto)

    elif estado == "saturado":
        redis_mod.r.sadd("puntosverdes:saturados", id_punto)

    return f"Estado del punto verde {id_punto} actualizado correctamente."


def eliminar_estado_punto(id_punto):
    id_punto = str(id_punto)

    redis_mod.r.delete(f"puntoverde:{id_punto}:estado")
    redis_mod.r.srem("puntosverdes:disponibles", id_punto)
    redis_mod.r.srem("puntosverdes:saturados", id_punto)
    redis_mod.r.zrem("ranking:puntosverdes:uso", id_punto)

    return f"Datos temporales del punto verde {id_punto} eliminados de Redis."


def eliminar_alertas():
    redis_mod.r.delete("alertas:recientes")
    return "Alertas recientes eliminadas correctamente."