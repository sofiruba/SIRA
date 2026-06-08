import json
from redis_app import carga_redis as redis_mod

r = redis_mod.r


def obtener_estado_punto_verde(id_punto):
    return r.hgetall(f"puntoverde:{id_punto}:estado")


def obtener_puntos_disponibles():
    return list(r.smembers("puntosverdes:disponibles"))


def obtener_puntos_saturados():
    return list(r.smembers("puntosverdes:saturados"))


def obtener_ranking():
    return r.zrevrange(
        "ranking:puntosverdes:uso",
        0,
        -1,
        withscores=True
    )


def obtener_alertas():
    alertas_raw = r.lrange("alertas:recientes", 0, -1)

    if not alertas_raw:
        return []

    alertas = []

    for alerta in alertas_raw:
        if isinstance(alerta, bytes):
            alerta = alerta.decode("utf-8")

        alerta_dict = json.loads(alerta)
        alertas.append(alerta_dict)

    return alertas