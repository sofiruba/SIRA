import redis
import json

# ==========================================
# CONEXIÓN A REDIS, docker run --name redis -p 6379:6379 -d redis
# ==========================================

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# ==========================================
# CARGA DE DATOS
# ==========================================

def cargar_datos(ruta_json="redis_data.json"):

    with open(ruta_json, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    # Limpiar la base de datos antes de cargar nuevos datos, esto para evitar duoplicados 
    r.flushdb()

    # Carga de puntos verdes en hashes y sets para estados
    for punto in datos["puntos_verdes"]:

        punto_id = punto["_id"]

        r.hset(
            f"puntoverde:{punto_id}:estado",
            mapping={
                "estado": punto["estado"],
                "capacidad_actual": punto["capacidad_actual"],
                "ultima_actualizacion": punto["ultima_actualizacion"]
            }
        )

        if punto["estado"] == "disponible":
            r.sadd("puntosverdes:disponibles", punto_id)

        elif punto["estado"] == "saturado":
            r.sadd("puntosverdes:saturados", punto_id)

    # carga de ranking en un sorted set 
    for ranking in datos["ranking_uso"]:

        r.zadd(
            "ranking:puntosverdes:uso",
            {
                str(ranking["id_punto_verde"]):
                ranking["puntaje"]
            }
        )

    # carga de alertas en una lista (list)
    for alerta in datos["alertas"]:

        r.rpush(
            "alertas:recientes",
            json.dumps(alerta, ensure_ascii=False)
        )

# ==========================================
# CONSULTAS
# ==========================================

def obtener_estado_punto_verde(id_punto):
    return r.hgetall(
        f"puntoverde:{id_punto}:estado"
    )

def obtener_puntos_disponibles():
    return list(
        r.smembers("puntosverdes:disponibles")
    )

def obtener_puntos_saturados():
    return list(
        r.smembers("puntosverdes:saturados")
    )

def obtener_ranking():
    return r.zrevrange(
        "ranking:puntosverdes:uso",
        0,
        -1,
        withscores=True
    )

def obtener_alertas():
    alertas = r.lrange(
        "alertas:recientes",
        0,
        -1
    )

    return [
        json.loads(alerta)
        for alerta in alertas
    ]

# ==========================================
# EJECUCION A LO CRIOLLO, se ejecuta de forma manual desde la terminal para carga de datos
# ==========================================

if __name__ == "__main__":

    cargar_datos()

    print("Datos cargados correctamente en Redis.")