from datetime import datetime
from conexiones import obtener_cliente_redis

# Declaramos la conexion global
r = obtener_cliente_redis()

def actualizar_estado_punto(id_punto, estado, capacidad_actual):
    id_punto = str(id_punto)

    ultima_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    clave = f"puntoverde:{id_punto}:estado"

    r.hset(
        clave,
        mapping={
            "estado": estado,
            "capacidad_actual": capacidad_actual,
            "ultima_actualizacion": ultima_actualizacion
        }
    )

    r.srem("puntosverdes:disponibles", id_punto)
    r.srem("puntosverdes:saturados", id_punto)

    if estado == "disponible":
        r.sadd("puntosverdes:disponibles", id_punto)

    elif estado == "saturado":
        r.sadd("puntosverdes:saturados", id_punto)

    return f"Estado del punto verde {id_punto} actualizado correctamente."


def eliminar_estado_punto(id_punto):
    id_punto = str(id_punto)

    r.delete(f"puntoverde:{id_punto}:estado")
    r.srem("puntosverdes:disponibles", id_punto)
    r.srem("puntosverdes:saturados", id_punto)
    r.zrem("ranking:puntosverdes:uso", id_punto)

    return f"Datos temporales del punto verde {id_punto} eliminados de Redis."


def eliminar_alertas():
    r.delete("alertas:recientes")
    return "Alertas recientes eliminadas correctamente."