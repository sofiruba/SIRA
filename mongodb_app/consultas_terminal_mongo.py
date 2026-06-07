import json
import os

print("Directorio actual:")
print(os.getcwd())
from pymongo import MongoClient
# Conexión al servidor MongoDB local
client = MongoClient("mongodb://localhost:27017/")

# Obtener lista de bases de datos
bases = client.list_database_names()
print("Bases de datos disponibles:")
for db in bases:
    print("-", db)

# Base de datos (se crea automáticamente si no existe)
db = client["sira"]

# 2. COLECCIONES
coleccion_puntos = db["puntos_verdes"]
coleccion_residuos = db["tipos_residuos"]

print("Conexión establecida con MongoDB")


# 3. CARGA DE PUNTOS VERDES
with open("puntos_verdes.json", "r", encoding="utf-8") as archivo:
    puntos = json.load(archivo)

# Evita duplicados si corrés el script varias veces
if coleccion_puntos.count_documents({}) == 0:
    coleccion_puntos.insert_many(puntos)
    print("Colección puntos_verdes cargada")
else:
    print("puntos_verdes ya tenía datos (no se duplicó)")


# 4. CARGA DE TIPOS DE RESIDUOS
with open("tipos_residuos.json", "r", encoding="utf-8") as archivo:
    residuos = json.load(archivo)

if coleccion_residuos.count_documents({}) == 0:
    coleccion_residuos.insert_many(residuos)
    print("Colección tipos_residuos cargada")
else:
    print("tipos_residuos ya tenía datos (no se duplicó)")

# 5. VERIFICACIÓN FINAL
print("\n verifico que cargaron bien las colecciones:")
print("Puntos verdes:", coleccion_puntos.count_documents({}))
print("Tipos de residuos:", coleccion_residuos.count_documents({}))

# hasta aca hice la carga de datos, ahora consultas y ops

#===========================================================
# CONSULTAS (READ)
#===========================================================
# nuestras consultas principales se centran en responder preguntas de negocio 

#====================sobre puntos verdes====================

#CONSULTA 1: ¿Dónde se pueden reciclar residuos electrónicos?

print("\nPUNTOS VERDES QUE ACEPTAN RAEEs (R16)")

for punto in coleccion_puntos.find(
    {"residuos_aceptados": "R16"},
    {"_id": 0, "nombre": 1, "barrio": 1, "direccion": 1}
):
    print(f"• {punto['nombre']}")
    print(f"  Barrio: {punto['barrio']}")
    print(f"  Dirección: {punto['direccion']}")
    print()

#CONSULTA 2: ¿Que puntos verdes estan abiertos los sabados?
print("\nPUNTOS VERDES ABIERTOS LOS SÁBADOS")

for punto in coleccion_puntos.find(
    {"horario.dias": "Sabado"},
    {
        "_id": 0,
        "nombre": 1,
        "horario": 1,
        "barrio": 1,
        "direccion": 1
    }
):
    print(f"• {punto['nombre']}")
    print(f"  Horario: {punto['horario']['apertura']} - {punto['horario']['cierre']}")
    print(f"  Barrio: {punto['barrio']}")
    print(f"  Dirección: {punto['direccion']}")
    print()

#CONSULTA 3: ¿Que centros se especializan en botellas de amor (R13) y capsulas de cafe (R14)?
print("\nCENTROS QUE RECIBEN BOTELLAS DE AMOR Y CÁPSULAS DE CAFÉ")

for punto in coleccion_puntos.find(
    {
        "residuos_aceptados": {
            "$all": ["R13", "R14"]
        }
    },
    {
        "_id": 0,
        "nombre": 1,
        "barrio": 1
    }
):
    print(f"• {punto['nombre']} - {punto['barrio']}")

#CONSULTA 4: ¿Que puntos verde hay en Villa lugano?
print("\nPUNTOS VERDES EN VILLA LUGANO")

for punto in coleccion_puntos.find(
    {"barrio": "Villa Lugano"},
    {
        "_id": 0,
        "nombre": 1,
        "direccion": 1,
        "horario": 1
    }
):
    print(f"• {punto['nombre']}")
    print(f"  Dirección: {punto['direccion']}")
    print(
        f"  Horario: "
        f"{punto['horario']['apertura']} - "
        f"{punto['horario']['cierre']}"
    )
    print()

#CONSULTA 5: ¿Que puntos verdes hay en comunas 7 y 8?
print("\nPUNTOS VERDES EN COMUNAS 7 Y 8")
for punto in coleccion_puntos.find(
    {
        "comuna": {
            "$in": ["Comuna 7", "Comuna 8"]
        }
    },
    {
        "_id": 0,
        "nombre": 1,
        "barrio": 1,
        "comuna": 1
    }
):
    print(
        f"• {punto['nombre']} "
        f"({punto['barrio']} - {punto['comuna']})"
    )

#==================sobre tipos de residuos==================

#CONSULTA 6: ¿Qué residuos pueden depositarse en los contenedores de reciclaje?
print("\nRESIDUOS QUE PUEDEN DEPOSITARSE EN CONTENEDORES DE RECICLAJE")

for residuo in coleccion_residuos.find(
    {"categoria": "Reciclable"},
    {
        "_id": 0,
        "nombre": 1,
        "color_contenedor": 1
    }
):
    print(
        f"• {residuo['nombre']}"
        f" → Contenedor {residuo['color_contenedor']}"
    )

#CONSULTA 7: ¿Qué residuos requieren un tratamiento especial?
print("\nRESIDUOS DE TRATAMIENTO ESPECIAL")

for residuo in coleccion_residuos.find(
    {
        "$or": [
            {"categoria": "Reciclable Especial"},
            {"categoria": "Organico Especial"},
            {"categoria": "Electronico"}
        ]
    },
    {
        "_id": 0,
        "nombre": 1,
        "categoria": 1
    }
):
    print(
        f"• {residuo['nombre']} "
        f"({residuo['categoria']})"
    )

#CONSULTA 8: ¿Qué residuos utilizan contenedores amarillos?
print("\nRESIDUOS DEL CONTENEDOR AMARILLO")

for residuo in coleccion_residuos.find(
    {"color_contenedor": "Amarillo"},
    {
        "_id": 0,
        "nombre": 1,
        "categoria": 1
    }
):
    print(
        f"• {residuo['nombre']} "
        f"({residuo['categoria']})"
    )

#CONSULTA 9: ¿Qué residuos son reutilizables u orgánicos?
print("\nRESIDUOS REUTILIZABLES U ORGÁNICOS")

for residuo in coleccion_residuos.find(
    {
        "$or": [
            {"categoria": "Reutilizable"},
            {"categoria": "Organico"}
        ]
    },
    {
        "_id": 0,
        "nombre": 1,
        "categoria": 1
    }
):
    print(
        f"• {residuo['nombre']} "
        f"({residuo['categoria']})"
    )

#===========================================================
# CREACIÓN (CREATE)
#===========================================================
# las operaciones de creación nos permiten agregar nuevos puntos verdes o tipos de residuos a la base de datos
# esto se considera una operación de escritura (write) y es fundamental para mantener la base de datos actualizada con nuevos centros de reciclaje o nuevos tipos de residuos que puedan surgir

# CREATE 1: Registrar un nuevo Punto Verde

print("\nREGISTRO DE NUEVO PUNTO VERDE")

nuevo_punto_verde = {
    "id": 46,
    "nombre": "Punto Verde Puerto Madero",
    "residuos_aceptados": ["R1", "R2", "R3", "R8", "R16"],
    "horario": {
        "dias": ["Lunes", "Miercoles", "Viernes"],
        "apertura": "09:00",
        "cierre": "18:00"
    },
    "direccion": "Av. Alicia Moreau de Justo 500",
    "barrio": "Puerto Madero",
    "comuna": "Comuna 1"
}

if coleccion_puntos.count_documents({"id": 46}) == 0:
    coleccion_puntos.insert_one(nuevo_punto_verde)
    print("Nuevo punto verde registrado correctamente")
else:
    print("El punto verde ya existía (no se duplicó)")

# verificación: 

print("\nVERIFICACIÓN DE LA CARGA DEL PUNTO VERDE")

punto = coleccion_puntos.find_one(
    {"id": 46},
    {
        "_id": 0
    }
)

if punto:
    print(f"• {punto['nombre']}")
    print(f"  Barrio: {punto['barrio']}")
    print(f"  Dirección: {punto['direccion']}")
    print(
        f"  Horario: "
        f"{punto['horario']['apertura']} - "
        f"{punto['horario']['cierre']}"
    )
    print(f"  Residuos aceptados: {', '.join(punto['residuos_aceptados'])}")
else:
    print("No se encontró el punto verde.")

#CREATE 2: Incorporar nuevos tipos de residuos (para probar el insert_many)
print("\nREGISTRO DE NUEVOS TIPOS DE RESIDUOS")

nuevos_residuos = [
    {
        "id_residuo": "R17",
        "nombre": "Medicamentos Vencidos",
        "color_contenedor": "Rojo",
        "categoria": "Residuo Especial"
    },
    {
        "id_residuo": "R18",
        "nombre": "Radiografias",
        "color_contenedor": "Negro",
        "categoria": "Residuo Especial"
    }
]

if coleccion_residuos.count_documents(
    {"id_residuo": {"$in": ["R17", "R18"]}}
) == 0:
    coleccion_residuos.insert_many(nuevos_residuos)
    print("Nuevos tipos de residuos registrados correctamente")
else:
    print("Los residuos ya existían (no se duplicaron)")

#verificación:
print("\nVERIFICACIÓN DE LA CARGA DE LOS NUEVOS RESIDUOS")

for residuo in coleccion_residuos.find(
    {
        "id_residuo": {
            "$in": ["R17", "R18"]
        }
    },
    {
        "_id": 0
    }
):
    print(f"• {residuo['nombre']}")
    print(f"  ID: {residuo['id_residuo']}")
    print(f"  Categoría: {residuo['categoria']}")
    print(f"  Color de contenedor: {residuo['color_contenedor']}")
    print()

#===========================================================
# ACTUALIZACIONES (UPDATE)
#===========================================================
# buscamos hacer actualizaciones que representarian casos reales en nuestro negocio 

#UPDATE 1: Ampliar los residuos aceptados por un Punto Verde
#Supongamos que el Punto Verde id 45 comienza a recibir Botellas de Amor.
print("\nACTUALIZACIÓN DE RESIDUOS ACEPTADOS")

coleccion_puntos.update_one(
    {"id": 45},
    {
        "$push": {
            "residuos_aceptados": "R13"
        }
    }
)
print("Se agregó R13 a los residuos aceptados")

#verificacion de los cambios: 
punto = coleccion_puntos.find_one(
    {"id": 45},
    {
        "_id": 0,
        "nombre": 1,
        "residuos_aceptados": 1
    }
)

print(f"\n{punto['nombre']}")
print("Residuos aceptados:")
print(punto["residuos_aceptados"])

#UPDATE 2: Modificar el horario de atención de un Punto Verde
print("\nACTUALIZACIÓN DE HORARIO")

coleccion_puntos.update_one(
    {"nombre": "Estacion Lugano"},
    {
        "$set": {
            "horario.cierre": "20:00"
        }
    }
)

print("Horario actualizado correctamente")

#verificacion de los cambios:
punto = coleccion_puntos.find_one(
    {"nombre": "Estacion Lugano"},
    {
        "_id": 0,
        "nombre": 1,
        "horario": 1
    }
)

print(f"• {punto['nombre']}")
print(
    f"  Horario: "
    f"{punto['horario']['apertura']} - "
    f"{punto['horario']['cierre']}"
)

#UPDATE 3: Incorporar un nuevo atributo a todos los puntos verdes
# Supongamos que queremos agregar un campo "activo" para indicar si el punto verde está operativo o no. Por defecto, lo estableceremos en True para todos los puntos verdes existentes.
print("\nINCORPORACIÓN DEL CAMPO ACTIVO")

coleccion_puntos.update_many(
    {},
    {
        "$set": {
            "activo": True
        }
    }
)

print("Campo 'activo' agregado a todos los puntos verdes")

#UPDATE 4: Modificar la categoría de un tipo de residuo
#Suponemos que cambia la clasificación.
print("\nACTUALIZACIÓN DE CATEGORÍA DE RESIDUO")

coleccion_residuos.update_one(
    {"id_residuo": "R14"},
    {
        "$set": {
            "categoria": "Reciclable Premium"
        }
    }
)

print("Categoría actualizada correctamente")

#verificamos
residuo = coleccion_residuos.find_one(
    {"id_residuo": "R14"},
    {
        "_id": 0
    }
)

print(f"• {residuo['nombre']}")
print(f"  Categoría: {residuo['categoria']}")

#===========================================================
# ELIMINAR (DELETE)
#===========================================================
# probamos algunos deletes con datos que habias corrido recientemente.
 
#DELETE 1: Eliminar un punto verde dado de baja
#Supongamos que el punto verde que creamos para pruebas ya no forma parte de la red.
print("\nELIMINACIÓN DE PUNTO VERDE")

coleccion_puntos.delete_one(
    {"id": 46}
)

print("Punto verde eliminado correctamente")

#verificamos
punto = coleccion_puntos.find_one({"id": 46})

if punto is None:
    print("Verificación exitosa: el punto verde ya no existe.")
else:
    print("El punto verde sigue existiendo.")


#DELETE 2: Eliminar varios residuos de prueba
#Permite eliminar registros de prueba o residuos discontinuados.
print("\nELIMINACIÓN DE RESIDUOS DE PRUEBA")

resultado = coleccion_residuos.delete_many(
    {
        "id_residuo": {
            "$in": ["R17", "R18"]
        }
    }
)

print(f"Se eliminaron {resultado.deleted_count} residuos.")

#DELETE 3: Eliminar el campo "activo"
#Supongamos que decidimos no usar más el campo "activo" y queremos eliminarlo de todos los documentos.

print("\nELIMINACIÓN DEL CAMPO ACTIVO")

resultado = coleccion_puntos.update_many(
    {},
    {
        "$unset": {
            "activo": ""
        }
    }
)

print(
    f"Campo eliminado en "
    f"{resultado.modified_count} documentos."
)

"""
# Verificación final después de updates y deletes
print("\n# VERIFICACIÓN FINAL")
print("Puntos verdes:", coleccion_puntos.count_documents({}))
print("Tipos de residuos:", coleccion_residuos.count_documents({}))

# interaccion basica
def buscar_puntos_por_barrio(barrio):
    # Devuelve puntos verdes según el barrio
    return coleccion_puntos.find({"barrio": barrio})



# prueba de la app???

print("\n# APP: PUNTOS EN VILLA LUGANO")
for p in buscar_puntos_por_barrio("Villa Lugano"):
    print(p)

print("\n# APP: RESIDUOS RECICLABLES")
for r in obtener_residuos_reciclables():
    print(r)
"""