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
    return r.zrevrange("ranking:puntosverdes:uso", 0, -1, withscores=True)

def obtener_alertas():
    # 1. Traemos todos los elementos de la lista en Redis (del primero al último)
    alertas_raw = redis_mod.r.lrange("alertas:recientes", 0, -1)
    
    if not alertas_raw:
        return []

    alertas_decodificadas = []
    
    for alerta in alertas_raw:
        alerta_dict = json.loads(alerta.decode('utf-8'))
        alertas_decodificadas.append(alerta_dict)
        
    return alertas_decodificadas