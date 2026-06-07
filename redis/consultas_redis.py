import json

# ==========================================
# CONSULTAS
# ==========================================


def obtener_estado_punto_verde(r,id_punto):
    return r.hgetall(
        f"puntoverde:{id_punto}:estado"
    )

def obtener_puntos_disponibles(r):
    return list(
        r.smembers("puntosverdes:disponibles")
    )

def obtener_puntos_saturados(r):
    return list(
        r.smembers("puntosverdes:saturados")
    )

def obtener_ranking(r):
    return r.zrevrange(
        "ranking:puntosverdes:uso",
        0,
        -1,
        withscores=True
    )

def obtener_alertas(r):
    alertas = r.lrange(
        "alertas:recientes",
        0,
        -1
    )

    return [
        json.loads(alerta)
        for alerta in alertas
    ]