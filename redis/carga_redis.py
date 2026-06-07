import redis
import json
from conexiones import obtener_cliente_redis

# ==========================================
# CONEXIÓN A REDIS, docker run --name redis -p 6379:6379 -d redis
# ==========================================

# ==========================================
# CARGA DE DATOS
# ==========================================

def cargar_datos(ruta_json="redis_data.json"):

    r = obtener_cliente_redis()

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

if __name__ == "__main__":

    cargar_datos()

    print("Datos cargados correctamente en Redis.")



