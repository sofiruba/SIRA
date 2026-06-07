# =====================================================
# CONEXIÓN Y CARGA DE DATOS
# =====================================================

import json
import os
from pymongo import MongoClient
import SIRA_mongodb_funciones as mongo


def inicializar_datos():

    print("\nVerificando datos iniciales...")

    # -----------------------------
    # CARGA DE PUNTOS VERDES
    # -----------------------------
    if coleccion_puntos.count_documents({}) == 0:

        with open(
            "puntos_verdes.json",
            "r",
            encoding="utf-8"
        ) as archivo:

            puntos = json.load(archivo)

        coleccion_puntos.insert_many(puntos)

        print("Colección puntos_verdes cargada")

    else:

        print("puntos_verdes ya contiene datos")


    # -----------------------------
    # CARGA DE TIPOS DE RESIDUOS
    # -----------------------------
    if coleccion_residuos.count_documents({}) == 0:

        with open(
            "tipos_residuos.json",
            "r",
            encoding="utf-8"
        ) as archivo:

            residuos = json.load(archivo)

        coleccion_residuos.insert_many(residuos)

        print("Colección tipos_residuos cargada")

    else:

        print("tipos_residuos ya contiene datos")


    # -----------------------------
    # VERIFICACIÓN FINAL
    # -----------------------------
    print("\nEstado actual de la base:")

    print(f"Puntos verdes: "
        f"{coleccion_puntos.count_documents({})}")

    print(f"Tipos de residuos: "
        f"{coleccion_residuos.count_documents({})}")


# =====================================================
# CONEXIÓN A MONGODB
# =====================================================

print("===================================")
print(" SISTEMA SIRA - MONGODB ")
print("===================================")

print("\nDirectorio actual:")
print(os.getcwd())

client = MongoClient("mongodb://localhost:27017/")

db = client["sira"]

coleccion_puntos = db["puntos_verdes"]
coleccion_residuos = db["tipos_residuos"]

print("\nConexión establecida con MongoDB")

# Cargar datos iniciales si es necesario
inicializar_datos()

# =====================================================
# MENÚ CONSULTAS
# =====================================================

def menu_consultas():

    while True:

        print("\n===================================")
        print(" CONSULTAS ")
        print("===================================")

        print("1. Puntos verdes que aceptan RAEEs")
        print("2. Puntos verdes abiertos los sábados")
        print("3. Centros que reciben R13 y R14")
        print("4. Puntos verdes en Villa Lugano")
        print("5. Puntos verdes en Comunas 7 y 8")

        print("6. Residuos reciclables")
        print("7. Residuos de tratamiento especial")
        print("8. Residuos del contenedor amarillo")
        print("9. Residuos reutilizables u orgánicos")

        print("0. Volver")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            mongo.consulta1(coleccion_puntos)

        elif opcion == "2":
            mongo.consulta2(coleccion_puntos)

        elif opcion == "3":
            mongo.consulta3(coleccion_puntos)

        elif opcion == "4":
            mongo.consulta4(coleccion_puntos)

        elif opcion == "5":
            mongo.consulta5(coleccion_puntos)

        elif opcion == "6":
            mongo.consulta6(coleccion_residuos)

        elif opcion == "7":
            mongo.consulta7(coleccion_residuos)

        elif opcion == "8":
            mongo.consulta8(coleccion_residuos)

        elif opcion == "9":
            mongo.consulta9(coleccion_residuos)

        elif opcion == "0":
            break

        else:
            print("Opción inválida")

# =====================================================
# MENÚ CREATE
# =====================================================

def menu_crear():

    while True:

        print("\n===================================")
        print(" CREAR ")
        print("===================================")

        print("1. Registrar Punto Verde")
        print("2. Registrar varios Puntos Verdes")

        print("3. Registrar Tipo de Residuo")
        print("4. Registrar varios Tipos de Residuos")

        print("0. Volver")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":

            mongo.crear_punto_verde(coleccion_puntos,coleccion_residuos)

        elif opcion == "2":

            mongo.crear_muchos_puntos_verdes(coleccion_puntos,coleccion_residuos)

        elif opcion == "3":

            mongo.crear_residuo(coleccion_residuos)

        elif opcion == "4":

            mongo.crear_muchos_residuos(coleccion_residuos)

        elif opcion == "0":

            break

        else:

            print("Opción inválida")

# =====================================================
# MENÚ ACTUALIZACIONES
# =====================================================

def menu_actualizar():

    while True:

        print("\n===================================")
        print(" ACTUALIZAR ")
        print("===================================")

        print("1. Actualizar Punto Verde")
        print("2. Actualizar Tipo de Residuo")

        print("3. Agregar campo activo a todos los puntos verdes")

        print("0. Volver")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":

            mongo.actualizar_punto_verde(coleccion_puntos,coleccion_residuos)

        elif opcion == "2":

            mongo.actualizar_residuo(coleccion_residuos)

        elif opcion == "3":

            mongo.agregar_campo_activo(coleccion_puntos)

        elif opcion == "0":

            break

        else:

            print("Opción inválida")

# =====================================================
# MENÚ ELIMINAR
# =====================================================

def menu_eliminar():

    while True:

        print("\n===================================")
        print(" ELIMINAR ")
        print("===================================")

        print("1. Eliminar Punto Verde")
        print("2. Eliminar varios Puntos Verdes")

        print("3. Eliminar Tipo de Residuo")
        print("4. Eliminar varios Tipos de Residuos")

        print("5. Eliminar campo activo")

        print("0. Volver")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":

            mongo.eliminar_punto_verde(coleccion_puntos)

        elif opcion == "2":

            mongo.eliminar_muchos_puntos_verdes(coleccion_puntos, coleccion_residuos)

        elif opcion == "3":

            mongo.eliminar_residuo(coleccion_residuos, coleccion_puntos)

        elif opcion == "4":

            mongo.eliminar_muchos_residuos( coleccion_residuos, coleccion_puntos)

        elif opcion == "5":

            mongo.eliminar_campo_activo(coleccion_puntos)

        elif opcion == "0":

            break

        else:

            print("Opción inválida")

# =====================================================
# MENÚ BUSACAR
# =====================================================
def menu_buscar():

    while True:

        print("\n===================================")
        print(" BUSCAR ")
        print("===================================")

        print("1. Buscar Punto Verde")
        print("2. Buscar Tipo de Residuo")

        print("0. Volver")

        opcion = input(
            "\nSeleccione una opcion: "
        )

        if opcion == "1":

            mongo.buscar_punto_verde(coleccion_puntos)

        elif opcion == "2":

            mongo.buscar_residuo(coleccion_residuos)

        elif opcion == "0":

            break

        else:

            print("Opción inválida")
# =====================================================
# MENÚ PRINCIPAL
# =====================================================

while True:

    print("\n===================================")
    print(" SISTEMA SIRA ")
    print("===================================")

    print("1. Consultas")
    print("2. Buscar")
    print("3. Crear")
    print("4. Actualizar")
    print("5. Eliminar")
    print("0. Salir")

    opcion = input("\nSeleccione una opción: ")

    if opcion == "1":

        menu_consultas()

    elif opcion == "2":

        menu_buscar()

    elif opcion == "3":

        menu_crear()

    elif opcion == "4":

        menu_actualizar()

    elif opcion == "5":

        menu_eliminar()

    elif opcion == "0":

        print("\nGracias por utilizar SIRA")
        client.close()
        break

    else:

        print("Opción inválida")
    