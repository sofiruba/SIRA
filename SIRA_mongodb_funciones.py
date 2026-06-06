from datetime import datetime
# ===========================================================
# CONSULTAS (READ)
# ===========================================================
# nuestras consultas principales se centran en responder
# preguntas de negocio

# ==================== sobre puntos verdes ====================

# CONSULTA 1: ¿Dónde se pueden reciclar residuos electrónicos?

def consulta1(coleccion_puntos):

    print("\nPUNTOS VERDES QUE ACEPTAN RAEEs (R16)")

    for punto in coleccion_puntos.find(
        {"residuos_aceptados": "R16"},
        {"_id": 0, "nombre": 1, "barrio": 1, "direccion": 1}
    ):
        print(f"• {punto['nombre']}")
        print(f"  Barrio: {punto['barrio']}")
        print(f"  Dirección: {punto['direccion']}")
        print()


# CONSULTA 2: ¿Que puntos verdes estan abiertos los sabados?

def consulta2(coleccion_puntos):

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
        print(
            f"  Horario: "
            f"{punto['horario']['apertura']} - "
            f"{punto['horario']['cierre']}"
        )
        print(f"  Barrio: {punto['barrio']}")
        print(f"  Dirección: {punto['direccion']}")
        print()


# CONSULTA 3: ¿Que centros se especializan en botellas de amor (R13) y capsulas de cafe (R14)?

def consulta3(coleccion_puntos):

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


# CONSULTA 4: ¿Que puntos verde hay en Villa Lugano?

def consulta4(coleccion_puntos):

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


# CONSULTA 5: ¿Que puntos verdes hay en comunas 7 y 8?

def consulta5(coleccion_puntos):

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


# ================== sobre tipos de residuos ==================

# CONSULTA 6: ¿Qué residuos pueden depositarse en los contenedores de reciclaje?

def consulta6(coleccion_residuos):

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


# CONSULTA 7: ¿Qué residuos requieren un tratamiento especial?

def consulta7(coleccion_residuos):

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


# CONSULTA 8: ¿Qué residuos utilizan contenedores amarillos?

def consulta8(coleccion_residuos):

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


# CONSULTA 9: ¿Qué residuos son reutilizables u orgánicos?

def consulta9(coleccion_residuos):

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


# ============================================================
# CREACIÓN (CREATE)
# ============================================================

#fx auxiliar para el create (validar formato de hora)
def hora_valida(hora):

    try:
        datetime.strptime(hora, "%H:%M")
        return True

    except ValueError:
        return False
    
# CREATE 1: Registrar un nuevo Punto Verde

def crear_punto_verde(coleccion_puntos, coleccion_residuos):
    print("\nREGISTRO DE NUEVO PUNTO VERDE")

    #id autoincremental
    ultimo_punto = coleccion_puntos.find_one(
        {},
        sort=[("id", -1)]
    )

    if ultimo_punto:
        nuevo_id = ultimo_punto["id"] + 1
    else:
        nuevo_id = 1

    print(f"\nID asignado automáticamente: {nuevo_id}")

    # Nombre validado (no vacío y no repetido)

    while True:

        nombre = input(
            "Nombre: "
        ).strip()

        if not nombre:

            print(
                "El nombre no puede estar vacío."
            )

            continue

        existe = coleccion_puntos.find_one(
            {
                "nombre": {
                    "$regex": f"^{nombre}$",
                    "$options": "i"
                }
            }
        )

        if existe:

            print(
                f"Ya existe un Punto Verde llamado "
                f"'{existe['nombre']}'."
            )

            continue

        break

    direccion = input(
        "Dirección: "
    ).strip()

    barrio = input(
        "Barrio: "
    ).strip()

    #comuna (existen 15 comunas en caba)

    while True:

        comuna = input(
            "Comuna (1-15): "
        ).strip()

        if comuna.isdigit():

            numero = int(comuna)

            if 1 <= numero <= 15:

                comuna = f"Comuna {numero}"
                break

        print(
            "Comuna inválida. Debe estar entre 1 y 15."
        )

    #residuos aceptados (mostrando opciones de nuestra otra colección)

    print("\nRESIDUOS DISPONIBLES")

    ids_validos = []

    for residuo in coleccion_residuos.find(
        {},
        {
            "_id": 0,
            "id_residuo": 1,
            "nombre": 1
        }
    ):

        print(
            f"{residuo['id_residuo']} - "
            f"{residuo['nombre']}"
        )

        ids_validos.append(
            residuo["id_residuo"]
        )

    while True:

        residuos = input(
            "\nResiduos aceptados (ej: R1,R2,R3): "
        )

        lista_residuos = [
            r.strip().upper()
            for r in residuos.split(",")
        ]

        if all(
            r in ids_validos
            for r in lista_residuos
        ):
            break

        print(
            "Existen códigos de residuos inválidos."
        )

    #días de atención validados
    dias_validos = [
        "Lunes",
        "Martes",
        "Miercoles",
        "Jueves",
        "Viernes",
        "Sabado",
        "Domingo"
    ]
    while True:

        dias = input(
            "\nDias de atencion "
            "(ej: Lunes,Miercoles,Viernes): "
        )

        lista_dias = [
            d.strip()
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("Á", "A")
            .replace("É", "E")
            .replace("Í", "I")
            .replace("Ó", "O")
            .replace("Ú", "U")
            .capitalize()
            for d in dias.split(",")
        ]

        if all(
            d in dias_validos
            for d in lista_dias
        ):
            break

        print("Hay dias invalidos.")
    
    # hororario

    while True:

        apertura = input(
            "Hora apertura (HH:MM): "
        )

        if hora_valida(apertura):
            break

        print(
            "Hora inválida."
        )

    while True:

        cierre = input(
            "Hora cierre (HH:MM): "
        )

        if hora_valida(cierre):

            hora_apertura = datetime.strptime(
                apertura,
                "%H:%M"
            )

            hora_cierre = datetime.strptime(
                cierre,
                "%H:%M"
            )

            if hora_cierre > hora_apertura:
                break

        print(
            "La hora de cierre debe ser posterior."
        )

    # documentar al insertar

    nuevo_punto_verde = {

        "id": nuevo_id,

        "nombre": nombre,

        "residuos_aceptados": lista_residuos,

        "horario": {

            "dias": lista_dias,

            "apertura": apertura,

            "cierre": cierre
        },

        "direccion": direccion,

        "barrio": barrio,

        "comuna": comuna
    }

    coleccion_puntos.insert_one(
        nuevo_punto_verde
    )

    print(
        "\n Nuevo punto verde registrado correctamente"
    )

# CREATE 1B: Registrar varios Puntos Verdes

def crear_muchos_puntos_verdes(
    coleccion_puntos,
    coleccion_residuos
):

    while True:

        try:

            cantidad = int(
                input(
                    "\n¿Cuántos puntos verdes desea registrar?: "
                )
            )

            if cantidad > 0:
                break

            print(
                "La cantidad debe ser mayor a 0."
            )

        except ValueError:

            print(
                "Debe ingresar un número."
            )

    for i in range(cantidad):

        print(
            f"\n===== PUNTO VERDE {i + 1} DE {cantidad} ====="
        )

        crear_punto_verde(
            coleccion_puntos,
            coleccion_residuos
        )

    print(
        f"\n✓ Se registraron {cantidad} puntos verdes correctamente."
    )
# CREATE 2: Registrar un nuevo Tipo de Residuo

def crear_residuo(coleccion_residuos):

    print("\nREGISTRO DE NUEVO TIPO DE RESIDUO")
    #id autoincremetal
    ids = []

    for residuo in coleccion_residuos.find(
        {},
        {"id_residuo": 1}
    ):

        numero = int(
            residuo["id_residuo"].replace("R", "")
        )

        ids.append(numero)

    nuevo_codigo = f"R{max(ids) + 1}"

    print(
        f"\nID asignado automáticamente: "
        f"{nuevo_codigo}"
    )
    # Nombre validado (no vacío y no repetido)
    while True:

        nombre = input(
            "Nombre del residuo: "
        ).strip()

        if not nombre:

            print(
                "El nombre no puede estar vacío."
            )

            continue

        existe = coleccion_residuos.find_one(
            {
                "nombre": {
                    "$regex": f"^{nombre}$",
                    "$options": "i"
                }
            }
        )

        if existe:

            print(
                f"Ya existe un residuo llamado "
                f"'{existe['nombre']}'."
            )

            continue

        break

    #color contenedor validado (sugerir opciones)

    print(
        "\nColores sugeridos: Verde, Azul, Amarillo, Marron"
    )
    while True:

        color = input(
            "Color del contenedor: "
        ).strip().capitalize()

        if color:
            break

        print(
            "Debe ingresar un color."
        )

    # categoria
    while True:

        categoria = input(
            "Categoría: "
        ).strip()

        if categoria:
            break

        print(
            "Debe ingresar una categoría."
        )

    # documentar al insertar

    nuevo_residuo = {

        "id_residuo": nuevo_codigo,

        "nombre": nombre,

        "color_contenedor": color,

        "categoria": categoria
    }

    coleccion_residuos.insert_one(
        nuevo_residuo
    )

    print(
        "\n Nuevo tipo de residuo registrado correctamente"
    )

def crear_muchos_residuos( coleccion_residuos):

    cantidad = int(
        input(
            "\n¿Cuántos residuos desea registrar?: "
        )
    )

    for i in range(cantidad):

        print(
            f"\n===== RESIDUO {i+1} ====="
        )

        crear_residuo(
            coleccion_residuos
        )

#===========================================================
# ACTUALIZACIONES (UPDATE)
#===========================================================
# buscamos hacer actualizaciones que representarian casos reales en nuestro negocio 
def actualizar_punto_verde(
    coleccion_puntos,
    coleccion_residuos
):

    print("\nACTUALIZAR PUNTO VERDE")

    try:

        id_punto = int(
            input("ID del Punto Verde: ")
        )

    except ValueError:

        print("ID inválido")
        return

    punto = coleccion_puntos.find_one(
        {"id": id_punto}
    )

    if not punto:

        print("No existe un Punto Verde con ese ID")
        return

    print(f"\nPunto Verde seleccionado: {punto['nombre']}")

    print("\n¿Qué desea modificar?")

    print("1. Nombre")
    print("2. Direccion")
    print("3. Barrio")
    print("4. Comuna")
    print("5. Residuos aceptados")
    print("6. Horario")

    opcion = input("\nSeleccione una opcion: ")

    # ACTUALIZAR NOMBRE

    if opcion == "1":

        nuevo_nombre = input(
            "Nuevo nombre: "
        ).strip()

        coleccion_puntos.update_one(
            {"id": id_punto},
            {
                "$set": {
                    "nombre": nuevo_nombre
                }
            }
        )

        print(" Nombre actualizado correctamente")

    # ACTUALIZAR DIRECCION

    elif opcion == "2":

        nueva_direccion = input(
            "Nueva direccion: "
        ).strip()

        coleccion_puntos.update_one(
            {"id": id_punto},
            {
                "$set": {
                    "direccion": nueva_direccion
                }
            }
        )

        print(" Direccion actualizada correctamente")

    # ACTUALIZAR BARRIO

    elif opcion == "3":

        nuevo_barrio = input(
            "Nuevo barrio: "
        ).strip()

        coleccion_puntos.update_one(
            {"id": id_punto},
            {
                "$set": {
                    "barrio": nuevo_barrio
                }
            }
        )

        print(" Barrio actualizado correctamente")

    # ACTUALIZAR COMUNA

    elif opcion == "4":

        while True:

            comuna = input(
                "Comuna (1-15): "
            ).strip()

            if comuna.isdigit():

                numero = int(comuna)

                if 1 <= numero <= 15:

                    comuna = f"Comuna {numero}"
                    break

            print(
                "Comuna inválida."
            )

        coleccion_puntos.update_one(
            {"id": id_punto},
            {
                "$set": {
                    "comuna": comuna
                }
            }
        )

        print(" Comuna actualizada correctamente")

    # ACTUALIZAR RESIDUOS ACEPTADOS

    elif opcion == "5":

        print("\nRESIDUOS DISPONIBLES")

        ids_validos = []

        for residuo in coleccion_residuos.find(
            {},
            {
                "_id": 0,
                "id_residuo": 1,
                "nombre": 1
            }
        ):

            print(
                f"{residuo['id_residuo']} - "
                f"{residuo['nombre']}"
            )

            ids_validos.append(
                residuo["id_residuo"]
            )

        while True:

            residuos = input(
                "\nNuevos residuos aceptados "
                "(ej: R1,R2,R3): "
            )

            lista_residuos = [
                r.strip().upper()
                for r in residuos.split(",")
            ]

            if all(
                r in ids_validos
                for r in lista_residuos
            ):
                break

            print(
                "Hay códigos de residuos inválidos."
            )

        coleccion_puntos.update_one(
            {"id": id_punto},
            {
                "$set": {
                    "residuos_aceptados": lista_residuos
                }
            }
        )

        print(" Residuos actualizados correctamente")

    # ACTUALIZAR HORARIO

    elif opcion == "6":

        while True:

            apertura = input(
                "Hora apertura (HH:MM): "
            )

            if hora_valida(apertura):
                break

            print("Hora inválida.")

        while True:

            cierre = input(
                "Hora cierre (HH:MM): "
            )

            if hora_valida(cierre):

                hora_apertura = datetime.strptime(
                    apertura,
                    "%H:%M"
                )

                hora_cierre = datetime.strptime(
                    cierre,
                    "%H:%M"
                )

                if hora_cierre > hora_apertura:
                    break

            print(
                "La hora de cierre debe ser posterior."
            )

        coleccion_puntos.update_one(
            {"id": id_punto},
            {
                "$set": {
                    "horario.apertura": apertura,
                    "horario.cierre": cierre
                }
            }
        )

        print(" Horario actualizado correctamente")

    else:

        print("Opción inválida")

def actualizar_residuo(
    coleccion_residuos
):

    print("\nACTUALIZAR TIPO DE RESIDUO")

    codigo = input(
        "Código del residuo (ej: R14): "
    ).upper().strip()

    residuo = coleccion_residuos.find_one(
        {"id_residuo": codigo}
    )

    if not residuo:

        print(
            "No existe un residuo con ese código."
        )
        return

    print(
        f"\nResiduo seleccionado: "
        f"{residuo['nombre']}"
    )

    print("\n¿Qué desea modificar?")

    print("1. Nombre")
    print("2. Color de contenedor")
    print("3. Categoría")

    opcion = input(
        "\nSeleccione una opción: "
    )

    # ACTUALIZAR NOMBRE

    if opcion == "1":

        nuevo_nombre = input(
            "Nuevo nombre: "
        ).strip()

        coleccion_residuos.update_one(
            {"id_residuo": codigo},
            {
                "$set": {
                    "nombre": nuevo_nombre
                }
            }
        )

        print(
            " Nombre actualizado correctamente"
        )

    # ACTUALIZAR COLOR DE CONTENEDOR

    elif opcion == "2":

        nuevo_color = input(
            "\nNuevo color: "
        ).strip().capitalize()

        coleccion_residuos.update_one(
            {"id_residuo": codigo},
            {
                "$set": {
                    "color_contenedor":
                    nuevo_color
                }
            }
        )

        print(
            " Color actualizado correctamente"
        )

    # ACTUALIZAR CATEGORIA

    elif opcion == "3":

        nueva_categoria = input(
            "\nNueva categoría: "
        ).strip()

        coleccion_residuos.update_one(
            {"id_residuo": codigo},
            {
                "$set": {
                    "categoria":
                    nueva_categoria
                }
            }
        )

        print(
            " Categoría actualizada correctamente"
        )

    else:

        print("Opción inválida")
    
def agregar_campo_activo(
    coleccion_puntos
):

    resultado = coleccion_puntos.update_many(
        {},
        {
            "$set": {
                "activo": True
            }
        }
    )

    print(
        f"Campo activo agregado a "
        f"{resultado.modified_count} documentos."
    )

#===========================================================
# ELIMINAR (DELETE)
#===========================================================

def eliminar_punto_verde(coleccion_puntos):

    print("\nPUNTOS VERDES DISPONIBLES")

    for punto in coleccion_puntos.find(
        {},
        {
            "_id": 0,
            "id": 1,
            "nombre": 1
        }
    ):

        print(
            f"{punto['id']} - "
            f"{punto['nombre']}"
        )

    try:

        id_punto = int(
            input(
                "\nID del Punto Verde a eliminar: "
            )
        )

    except ValueError:

        print("ID inválido")
        return

    resultado = coleccion_puntos.delete_one(
        {"id": id_punto}
    )

    if resultado.deleted_count > 0:

        print(
            " Punto Verde eliminado correctamente"
        )

    else:

        print(
            "No existe un Punto Verde con ese ID"
        )

def eliminar_muchos_puntos_verdes( coleccion_puntos ):

    print("\nPUNTOS VERDES DISPONIBLES")

    for punto in coleccion_puntos.find(
        {},
        {
            "_id": 0,
            "id": 1,
            "nombre": 1
        }
    ):

        print(
            f"{punto['id']} - "
            f"{punto['nombre']}"
        )

    ids = input(
        "\nIDs a eliminar "
        "(ej: 45,46,47): "
    )

    lista_ids = [
        int(id_punto.strip())
        for id_punto in ids.split(",")
    ]

    resultado = coleccion_puntos.delete_many(
        {
            "id": {
                "$in": lista_ids
            }
        }
    )

    print(
        f" Se eliminaron "
        f"{resultado.deleted_count} "
        f"Puntos Verdes"
    )

def eliminar_residuo( coleccion_residuos, coleccion_puntos):
    print("\nTIPOS DE RESIDUOS DISPONIBLES")

    for residuo in coleccion_residuos.find(
        {},
        {
            "_id": 0,
            "id_residuo": 1,
            "nombre": 1
        }
    ):

        print(
            f"{residuo['id_residuo']} - "
            f"{residuo['nombre']}"
        )

    codigo = input(
        "\nCódigo a eliminar: "
    ).upper().strip()

    residuo = coleccion_residuos.find_one(
        {"id_residuo": codigo}
    )

    if not residuo:

        print(
            "No existe ese residuo"
        )
        return

    # Eliminar el residuo
    resultado = coleccion_residuos.delete_one(
        {"id_residuo": codigo}
    )

    # Eliminar referencias en puntos verdes
    resultado_puntos = coleccion_puntos.update_many(
        {},
        {
            "$pull": {
                "residuos_aceptados": codigo
            }
        }
    )

    print(
        f" Residuo {codigo} eliminado correctamente"
    )

    print(
        f"Se actualizó "
        f"{resultado_puntos.modified_count} "
        f"Puntos Verdes"
    )

def eliminar_muchos_residuos(coleccion_residuos,coleccion_puntos):

    print("\nTIPOS DE RESIDUOS DISPONIBLES")

    for residuo in coleccion_residuos.find(
        {},
        {
            "_id": 0,
            "id_residuo": 1,
            "nombre": 1
        }
    ):

        print(
            f"{residuo['id_residuo']} - "
            f"{residuo['nombre']}"
        )

    codigos = input(
        "\nCódigos a eliminar "
        "(ej: R17,R18): "
    )

    lista_codigos = [
        codigo.strip().upper()
        for codigo in codigos.split(",")
    ]

    # Eliminar residuos

    resultado = coleccion_residuos.delete_many(
        {
            "id_residuo": {
                "$in": lista_codigos
            }
        }
    )

    # Eliminar referencias en puntos verdes

    resultado_puntos = coleccion_puntos.update_many(
        {},
        {
            "$pull": {
                "residuos_aceptados": {
                    "$in": lista_codigos
                }
            }
        }
    )

    print(
        f"Se eliminaron "
        f"{resultado.deleted_count} "
        f"tipos de residuos"
    )

    print(
        f"Se actualizaron "
        f"{resultado_puntos.modified_count} "
        f"Puntos Verdes"
    )

def eliminar_campo_activo(
    coleccion_puntos
):

    resultado = coleccion_puntos.update_many(
        {},
        {
            "$unset": {
                "activo": ""
            }
        }
    )

    print(
        f"✓ Campo activo eliminado de "
        f"{resultado.modified_count} documentos"
    )

# ===========================================================
# CONSULTAS (READ) BUSQUEDAS ESPECÍFICAS
# ===========================================================
def buscar_punto_verde( coleccion_puntos):

    print("\nBUSCAR PUNTO VERDE")

    print("1. Buscar por ID")
    print("2. Buscar por nombre")

    opcion = input(
        "\nSeleccione una opcion: "
    )

    # BUSCAR POR ID

    if opcion == "1":

        try:

            id_punto = int(
                input(
                    "ID del Punto Verde: "
                )
            )

        except ValueError:

            print("ID inválido")
            return

        punto = coleccion_puntos.find_one(
            {"id": id_punto},
            {"_id": 0}
        )

    # BUSCAR POR NOMBRE

    elif opcion == "2":

        nombre = input(
            "Nombre del Punto Verde: "
        ).strip()

        punto = coleccion_puntos.find_one(
            {
                "nombre": {
                    "$regex": nombre,
                    "$options": "i"
                }
            },
            {"_id": 0}
        )

    else:

        print("Opción inválida")
        return

    if punto:

        print("\n===================================")
        print(" PUNTO VERDE ENCONTRADO ")
        print("===================================")

        print(f"ID: {punto['id']}")
        print(f"Nombre: {punto['nombre']}")
        print(f"Direccion: {punto['direccion']}")
        print(f"Barrio: {punto['barrio']}")
        print(f"Comuna: {punto['comuna']}")

        print("\nResiduos aceptados:")

        for residuo in punto["residuos_aceptados"]:

            print(f"• {residuo}")

        print("\nHorario:")

        print(
            f"Dias: "
            f"{', '.join(punto['horario']['dias'])}"
        )

        print(
            f"Apertura: "
            f"{punto['horario']['apertura']}"
        )

        print(
            f"Cierre: "
            f"{punto['horario']['cierre']}"
        )

        if "activo" in punto:

            print(
                f"Activo: "
                f"{punto['activo']}"
            ) #???????????????????????????????????

    else:

        print(
            "No se encontró el Punto Verde."
        )

def buscar_residuo(
    coleccion_residuos
):

    print("\nBUSCAR TIPO DE RESIDUO")

    print("1. Buscar por ID")
    print("2. Buscar por nombre")

    opcion = input(
        "\nSeleccione una opcion: "
    )

    # BUSCAR POR ID

    if opcion == "1":

        codigo = input(
            "Codigo (ej: R14): "
        ).upper().strip()

        residuo = coleccion_residuos.find_one(
            {"id_residuo": codigo},
            {"_id": 0}
        )

    # BUSCAR POR NOMBRE

    elif opcion == "2":

        nombre = input(
            "Nombre del residuo: "
        ).strip()

        residuo = coleccion_residuos.find_one(
            {
                "nombre": {
                    "$regex": nombre,
                    "$options": "i"
                }
            },
            {"_id": 0}
        )

    else:

        print("Opción inválida")
        return

    if residuo:

        print("\n===================================")
        print(" RESIDUO ENCONTRADO ")
        print("===================================")

        print(
            f"Codigo: "
            f"{residuo['id_residuo']}"
        )

        print(
            f"Nombre: "
            f"{residuo['nombre']}"
        )

        print(
            f"Color de contenedor: "
            f"{residuo['color_contenedor']}"
        )

        print(
            f"Categoria: "
            f"{residuo['categoria']}"
        )

    else:

        print(
            "No se encontró el residuo."
        )