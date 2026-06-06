import redis
import json

# Conexión a Redis
r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


# Limpiar Redis antes de cargar
r.flushdb()

# Leer archivo JSON
with open("redis_data.json", "r", encoding="utf-8") as f:
    datos = json.load(f)

# Cargar puntos verdes
for punto in datos["puntos_verdes"]:

    key = f"puntoverde:{punto['_id']}:estado"

    r.hset(
        key,
        mapping={
            "estado": punto["estado"],
            "capacidad_actual": punto["capacidad_actual"],
            "ultima_actualizacion": punto["ultima_actualizacion"]
        }
    )


#SETs para puntos verdes disponibles y saturados
for punto in datos["puntos_verdes"]:

    punto_id = punto["_id"]
    estado = punto["estado"]

    if estado == "disponible":

        r.sadd(
            "puntosverdes:disponibles",
            punto_id
        )

    elif estado == "saturado":

        r.sadd(
            "puntosverdes:saturados",
            punto_id
        )

#Carga de ranking de uso
for ranking in datos["ranking_uso"]:

    r.zadd(
        "ranking:puntosverdes:uso",
        {
            str(ranking["id_punto_verde"]):
            ranking["puntaje"]
        }
    )

#Carga de alertas recientes
for alerta in datos["alertas"]:

    r.rpush(
        "alertas:recientes",
        json.dumps(alerta, ensure_ascii=False)
    )

print("Datos cargados correctamente")
