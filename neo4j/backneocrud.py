from neo4j import GraphDatabase
import os

# ══════════════════════════════════════════════════════════════════════════════
#  CONEXIÓN
# ══════════════════════════════════════════════════════════════════════════════

URI      = "neo4j://127.0.0.1:7687"
USER     = "neo4j"
PASSWORD = "Homero1234"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# ══════════════════════════════════════════════════════════════════════════════
#  UTILIDADES DE INTERFAZ
# ══════════════════════════════════════════════════════════════════════════════

VERDE  = "\033[92m"
CYAN   = "\033[96m"
AMARILLO = "\033[93m"
ROJO   = "\033[91m"
BLANCO = "\033[97m"
GRIS   = "\033[90m"
RESET  = "\033[0m"
NEGRITA = "\033[1m"


def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def titulo(texto):
    ancho = 54
    print(f"\n{VERDE}{'═' * ancho}{RESET}")
    print(f"{VERDE}  {NEGRITA}{texto.upper()}{RESET}")
    print(f"{VERDE}{'═' * ancho}{RESET}\n")


def separador():
    print(f"{GRIS}{'─' * 54}{RESET}")


def opcion(num, texto, icono=""):
    num_str = f"{num:>2}"
    print(f"  {CYAN}{num_str}{RESET}  {icono}  {texto}")


def ok(msg):
    print(f"\n  {VERDE}✔  {msg}{RESET}")


def error(msg):
    print(f"\n  {ROJO}✘  {msg}{RESET}")


def pedir(campo):
    return input(f"  {AMARILLO}▶ {campo}:{RESET} ")


def esperar():
    input(f"\n  {GRIS}[ Presioná Enter para continuar... ]{RESET}")


# ══════════════════════════════════════════════════════════════════════════════
#  ID AUTOMÁTICO
# ══════════════════════════════════════════════════════════════════════════════

def siguiente_id(session, etiqueta, campo):
    resultado = session.run(
        f"MATCH (n:{etiqueta}) RETURN coalesce(max(n.{campo}), 0) AS ultimo"
    )
    return resultado.single()["ultimo"] + 1


# ══════════════════════════════════════════════════════════════════════════════
#  CRUD  ·  USUARIO
# ══════════════════════════════════════════════════════════════════════════════

def crear_usuario(session):
    titulo("Nuevo Usuario")
    nuevo_id = siguiente_id(session, "Usuario", "id_usuario")
    nombre   = pedir("Nombre")
    email    = pedir("Email")
    barrio   = pedir("Barrio")
    comuna   = pedir("Comuna")

    session.run("""
        CREATE (u:Usuario {
            id_usuario: $id,
            nombre: $nombre,
            email: $email,
            barrio: $barrio,
            comuna: $comuna,
            puntos_ecologicos: 0,
            nivel_usuario: 'Novato'
        })
    """, id=nuevo_id, nombre=nombre, email=email, barrio=barrio, comuna=comuna)

    ok(f"Usuario creado con ID {nuevo_id}")


def listar_usuarios(session):
    titulo("Listado de Usuarios")
    filas = list(session.run("""
        MATCH (u:Usuario)
        RETURN u.id_usuario AS id, u.nombre AS nombre,
               u.email AS email, u.puntos_ecologicos AS puntos,
               u.nivel_usuario AS nivel
        ORDER BY id
    """))
    if not filas:
        print("  Sin registros.")
        return
    print(f"  {NEGRITA}{'ID':<5} {'Nombre':<20} {'Email':<25} {'Pts':>6} {'Nivel'}{RESET}")
    separador()
    for f in filas:
        print(f"  {f['id']:<5} {f['nombre']:<20} {f['email']:<25} {f['puntos']:>6} {f['nivel']}")


def modificar_usuario(session):
    titulo("Modificar Usuario")
    id_usuario = int(pedir("ID Usuario"))
    puntos     = int(pedir("Nuevos puntos ecológicos"))

    session.run("""
        MATCH (u:Usuario {id_usuario: $id})
        SET u.puntos_ecologicos = $puntos
    """, id=id_usuario, puntos=puntos)

    ok("Usuario actualizado")


def eliminar_usuario(session):
    titulo("Eliminar Usuario")
    id_usuario = int(pedir("ID Usuario"))

    session.run("""
        MATCH (u:Usuario {id_usuario: $id})
        DETACH DELETE u
    """, id=id_usuario)

    ok("Usuario eliminado")


# ══════════════════════════════════════════════════════════════════════════════
#  CRUD  ·  TIPO RESIDUO
# ══════════════════════════════════════════════════════════════════════════════

def crear_tipo_residuo(session):
    titulo("Nuevo Tipo de Residuo")
    nuevo_id  = siguiente_id(session, "TipoResiduo", "id_residuo")
    nombre    = pedir("Nombre")
    categoria = pedir("Categoría")
    color     = pedir("Color contenedor")

    session.run("""
        CREATE (r:TipoResiduo {
            id_residuo: $id,
            nombre: $nombre,
            categoria: $categoria,
            color_contenedor: $color
        })
    """, id=nuevo_id, nombre=nombre, categoria=categoria, color=color)

    ok(f"Tipo de Residuo creado con ID {nuevo_id}")


def listar_tipos_residuo(session):
    titulo("Listado de Tipos de Residuo")
    filas = list(session.run("""
        MATCH (r:TipoResiduo)
        RETURN r.id_residuo AS id, r.nombre AS nombre,
               r.categoria AS categoria, r.color_contenedor AS color
        ORDER BY id
    """))
    if not filas:
        print("  Sin registros.")
        return
    print(f"  {NEGRITA}{'ID':<5} {'Nombre':<20} {'Categoría':<20} {'Color'}{RESET}")
    separador()
    for f in filas:
        print(f"  {f['id']:<5} {f['nombre']:<20} {f['categoria']:<20} {f['color']}")


def modificar_tipo_residuo(session):
    titulo("Modificar Tipo de Residuo")
    id_residuo = int(pedir("ID Residuo"))
    nombre     = pedir("Nuevo nombre")
    categoria  = pedir("Nueva categoría")
    color      = pedir("Nuevo color")

    session.run("""
        MATCH (r:TipoResiduo {id_residuo: $id})
        SET r.nombre = $nombre,
            r.categoria = $categoria,
            r.color_contenedor = $color
    """, id=id_residuo, nombre=nombre, categoria=categoria, color=color)

    ok("Tipo de Residuo actualizado")


def eliminar_tipo_residuo(session):
    titulo("Eliminar Tipo de Residuo")
    id_residuo = int(pedir("ID Residuo"))

    session.run("""
        MATCH (r:TipoResiduo {id_residuo: $id})
        DETACH DELETE r
    """, id=id_residuo)

    ok("Tipo de Residuo eliminado")


# ══════════════════════════════════════════════════════════════════════════════
#  CRUD  ·  PUNTO VERDE
# ══════════════════════════════════════════════════════════════════════════════

def crear_punto_verde(session):
    titulo("Nuevo Punto Verde")
    nuevo_id  = siguiente_id(session, "PuntoVerde", "id")
    nombre    = pedir("Nombre")
    direccion = pedir("Dirección")
    barrio    = pedir("Barrio")
    comuna    = pedir("Comuna")

    session.run("""
        CREATE (p:PuntoVerde {
            id: $id,
            nombre: $nombre,
            direccion: $direccion,
            barrio: $barrio,
            comuna: $comuna
        })
    """, id=nuevo_id, nombre=nombre, direccion=direccion, barrio=barrio, comuna=comuna)

    ok(f"Punto Verde creado con ID {nuevo_id}")


def listar_puntos_verdes(session):
    titulo("Listado de Puntos Verdes")
    filas = list(session.run("""
        MATCH (p:PuntoVerde)
        RETURN p.id AS id, p.nombre AS nombre,
               p.direccion AS direccion, p.barrio AS barrio, p.comuna AS comuna
        ORDER BY id
    """))
    if not filas:
        print("  Sin registros.")
        return
    print(f"  {NEGRITA}{'ID':<5} {'Nombre':<20} {'Dirección':<25} {'Barrio':<18} {'Comuna'}{RESET}")
    separador()
    for f in filas:
        print(f"  {f['id']:<5} {f['nombre']:<20} {f['direccion']:<25} {f['barrio']:<18} {f['comuna']}")


def modificar_punto_verde(session):
    titulo("Modificar Punto Verde")
    id_punto  = int(pedir("ID Punto Verde"))
    nombre    = pedir("Nuevo nombre")
    direccion = pedir("Nueva dirección")

    session.run("""
        MATCH (p:PuntoVerde {id: $id})
        SET p.nombre = $nombre,
            p.direccion = $direccion
    """, id=id_punto, nombre=nombre, direccion=direccion)

    ok("Punto Verde actualizado")


def eliminar_punto_verde(session):
    titulo("Eliminar Punto Verde")
    id_punto = int(pedir("ID Punto Verde"))

    session.run("""
        MATCH (p:PuntoVerde {id: $id})
        DETACH DELETE p
    """, id=id_punto)

    ok("Punto Verde eliminado")


# ══════════════════════════════════════════════════════════════════════════════
#  CRUD  ·  RECICLADOR
# ══════════════════════════════════════════════════════════════════════════════

def crear_reciclador(session):
    titulo("Nuevo Reciclador")
    nuevo_id  = siguiente_id(session, "Reciclador", "id")
    nombre    = pedir("Nombre")
    tipo      = pedir("Tipo  (Empresa / Cooperativa / Independiente)")
    direccion = pedir("Dirección")
    barrio    = pedir("Barrio")
    comuna    = pedir("Comuna")

    session.run("""
        CREATE (r:Reciclador {
            id: $id,
            nombre: $nombre,
            tipo: $tipo,
            direccion: $direccion,
            barrio: $barrio,
            comuna: $comuna
        })
    """, id=nuevo_id, nombre=nombre, tipo=tipo, direccion=direccion, barrio=barrio, comuna=comuna)

    ok(f"Reciclador creado con ID {nuevo_id}")


def listar_recicladores(session):
    titulo("Listado de Recicladores")
    filas = list(session.run("""
        MATCH (r:Reciclador)
        RETURN r.id AS id, r.nombre AS nombre,
               r.tipo AS tipo, r.barrio AS barrio, r.comuna AS comuna
        ORDER BY id
    """))
    if not filas:
        print("  Sin registros.")
        return
    print(f"  {NEGRITA}{'ID':<5} {'Nombre':<22} {'Tipo':<18} {'Barrio':<18} {'Comuna'}{RESET}")
    separador()
    for f in filas:
        print(f"  {f['id']:<5} {f['nombre']:<22} {f['tipo']:<18} {f['barrio']:<18} {f['comuna']}")


def modificar_reciclador(session):
    titulo("Modificar Reciclador")
    id_reciclador = int(pedir("ID Reciclador"))
    nombre        = pedir("Nuevo nombre")
    tipo          = pedir("Nuevo tipo")

    session.run("""
        MATCH (r:Reciclador {id: $id})
        SET r.nombre = $nombre,
            r.tipo   = $tipo
    """, id=id_reciclador, nombre=nombre, tipo=tipo)

    ok("Reciclador actualizado")


def eliminar_reciclador(session):
    titulo("Eliminar Reciclador")
    id_reciclador = int(pedir("ID Reciclador"))

    session.run("""
        MATCH (r:Reciclador {id: $id})
        DETACH DELETE r
    """, id=id_reciclador)

    ok("Reciclador eliminado")


# ══════════════════════════════════════════════════════════════════════════════
#  RELACIONES
# ══════════════════════════════════════════════════════════════════════════════

# ── RECICLA ──────────────────────────────────────────────────────────────────

def crear_recicla(session):
    titulo("Crear: RECICLA")
    usuario = int(pedir("ID Usuario"))
    residuo = int(pedir("ID Tipo Residuo"))
    session.run("""
        MATCH (u:Usuario {id_usuario: $u})
        MATCH (r:TipoResiduo {id_residuo: $r})
        MERGE (u)-[:RECICLA]->(r)
    """, u=usuario, r=residuo)
    ok("Relación RECICLA creada")


def listar_recicla(session):
    titulo("Listado: RECICLA")
    filas = list(session.run("""
        MATCH (u:Usuario)-[:RECICLA]->(r:TipoResiduo)
        RETURN u.id_usuario AS id_u, u.nombre AS usuario,
               r.id_residuo AS id_r, r.nombre AS residuo
        ORDER BY usuario
    """))
    if not filas:
        print("  Sin relaciones registradas.")
        return
    print(f"  {NEGRITA}{'ID U':<6} {'Usuario':<22} {'ID R':<6} {'Residuo'}{RESET}")
    separador()
    for f in filas:
        print(f"  {f['id_u']:<6} {f['usuario']:<22} {f['id_r']:<6} {f['residuo']}")


def eliminar_recicla(session):
    titulo("Eliminar: RECICLA")
    id_usuario = int(pedir("ID Usuario"))
    id_residuo = int(pedir("ID Tipo Residuo"))
    session.run("""
        MATCH (u:Usuario {id_usuario: $id_u})-[r:RECICLA]->(t:TipoResiduo {id_residuo: $id_r})
        DELETE r
    """, id_u=id_usuario, id_r=id_residuo)
    ok("Relación RECICLA eliminada")


# ── ENTREGA_EN ────────────────────────────────────────────────────────────────

def crear_entrega_en(session):
    titulo("Crear: ENTREGA_EN")
    usuario = int(pedir("ID Usuario"))
    punto   = int(pedir("ID Punto Verde"))
    session.run("""
        MATCH (u:Usuario {id_usuario: $u})
        MATCH (p:PuntoVerde {id: $p})
        MERGE (u)-[:ENTREGA_EN]->(p)
    """, u=usuario, p=punto)
    ok("Relación ENTREGA_EN creada")


def listar_entrega_en(session):
    titulo("Listado: ENTREGA_EN")
    filas = list(session.run("""
        MATCH (u:Usuario)-[:ENTREGA_EN]->(p:PuntoVerde)
        RETURN u.id_usuario AS id_u, u.nombre AS usuario,
               p.id AS id_p, p.nombre AS punto
        ORDER BY usuario
    """))
    if not filas:
        print("  Sin relaciones registradas.")
        return
    print(f"  {NEGRITA}{'ID U':<6} {'Usuario':<22} {'ID P':<6} {'Punto Verde'}{RESET}")
    separador()
    for f in filas:
        print(f"  {f['id_u']:<6} {f['usuario']:<22} {f['id_p']:<6} {f['punto']}")


def eliminar_entrega_en(session):
    titulo("Eliminar: ENTREGA_EN")
    id_usuario = int(pedir("ID Usuario"))
    id_punto   = int(pedir("ID Punto Verde"))
    session.run("""
        MATCH (u:Usuario {id_usuario: $id_u})-[r:ENTREGA_EN]->(p:PuntoVerde {id: $id_p})
        DELETE r
    """, id_u=id_usuario, id_p=id_punto)
    ok("Relación ENTREGA_EN eliminada")


# ── ACEPTA ────────────────────────────────────────────────────────────────────

def crear_acepta(session):
    titulo("Crear: ACEPTA")
    punto   = int(pedir("ID Punto Verde"))
    residuo = int(pedir("ID Tipo Residuo"))
    session.run("""
        MATCH (p:PuntoVerde {id: $p})
        MATCH (r:TipoResiduo {id_residuo: $r})
        MERGE (p)-[:ACEPTA]->(r)
    """, p=punto, r=residuo)
    ok("Relación ACEPTA creada")


def listar_acepta(session):
    titulo("Listado: ACEPTA")
    filas = list(session.run("""
        MATCH (p:PuntoVerde)-[:ACEPTA]->(r:TipoResiduo)
        RETURN p.id AS id_p, p.nombre AS punto,
               r.id_residuo AS id_r, r.nombre AS residuo
        ORDER BY punto
    """))
    if not filas:
        print("  Sin relaciones registradas.")
        return
    print(f"  {NEGRITA}{'ID P':<6} {'Punto Verde':<25} {'ID R':<6} {'Residuo'}{RESET}")
    separador()
    for f in filas:
        print(f"  {f['id_p']:<6} {f['punto']:<25} {f['id_r']:<6} {f['residuo']}")


def eliminar_acepta(session):
    titulo("Eliminar: ACEPTA")
    id_punto   = int(pedir("ID Punto Verde"))
    id_residuo = int(pedir("ID Tipo Residuo"))
    session.run("""
        MATCH (p:PuntoVerde {id: $id_p})-[r:ACEPTA]->(t:TipoResiduo {id_residuo: $id_r})
        DELETE r
    """, id_p=id_punto, id_r=id_residuo)
    ok("Relación ACEPTA eliminada")


# ── RECOLECTA ─────────────────────────────────────────────────────────────────

def crear_recolecta(session):
    titulo("Crear: RECOLECTA")
    reciclador = int(pedir("ID Reciclador"))
    residuo    = int(pedir("ID Tipo Residuo"))
    session.run("""
        MATCH (r1:Reciclador {id: $rc})
        MATCH (r2:TipoResiduo {id_residuo: $rs})
        MERGE (r1)-[:RECOLECTA]->(r2)
    """, rc=reciclador, rs=residuo)
    ok("Relación RECOLECTA creada")


def listar_recolecta(session):
    titulo("Listado: RECOLECTA")
    filas = list(session.run("""
        MATCH (rec:Reciclador)-[:RECOLECTA]->(r:TipoResiduo)
        RETURN rec.id AS id_rc, rec.nombre AS reciclador,
               r.id_residuo AS id_r, r.nombre AS residuo
        ORDER BY reciclador
    """))
    if not filas:
        print("  Sin relaciones registradas.")
        return
    print(f"  {NEGRITA}{'ID RC':<6} {'Reciclador':<25} {'ID R':<6} {'Residuo'}{RESET}")
    separador()
    for f in filas:
        print(f"  {f['id_rc']:<6} {f['reciclador']:<25} {f['id_r']:<6} {f['residuo']}")


def eliminar_recolecta(session):
    titulo("Eliminar: RECOLECTA")
    id_reciclador = int(pedir("ID Reciclador"))
    id_residuo    = int(pedir("ID Tipo Residuo"))
    session.run("""
        MATCH (rec:Reciclador {id: $id_rc})-[r:RECOLECTA]->(t:TipoResiduo {id_residuo: $id_r})
        DELETE r
    """, id_rc=id_reciclador, id_r=id_residuo)
    ok("Relación RECOLECTA eliminada")


# ── RETIRA_DE ─────────────────────────────────────────────────────────────────

def crear_retira_de(session):
    titulo("Crear: RETIRA_DE")
    reciclador = int(pedir("ID Reciclador"))
    punto      = int(pedir("ID Punto Verde"))
    session.run("""
        MATCH (r:Reciclador {id: $rc})
        MATCH (p:PuntoVerde {id: $p})
        MERGE (r)-[:RETIRA_DE]->(p)
    """, rc=reciclador, p=punto)
    ok("Relación RETIRA_DE creada")


def listar_retira_de(session):
    titulo("Listado: RETIRA_DE")
    filas = list(session.run("""
        MATCH (rec:Reciclador)-[:RETIRA_DE]->(p:PuntoVerde)
        RETURN rec.id AS id_rc, rec.nombre AS reciclador,
               p.id AS id_p, p.nombre AS punto
        ORDER BY reciclador
    """))
    if not filas:
        print("  Sin relaciones registradas.")
        return
    print(f"  {NEGRITA}{'ID RC':<6} {'Reciclador':<25} {'ID P':<6} {'Punto Verde'}{RESET}")
    separador()
    for f in filas:
        print(f"  {f['id_rc']:<6} {f['reciclador']:<25} {f['id_p']:<6} {f['punto']}")


def eliminar_retira_de(session):
    titulo("Eliminar: RETIRA_DE")
    id_reciclador = int(pedir("ID Reciclador"))
    id_punto      = int(pedir("ID Punto Verde"))
    session.run("""
        MATCH (rec:Reciclador {id: $id_rc})-[r:RETIRA_DE]->(p:PuntoVerde {id: $id_p})
        DELETE r
    """, id_rc=id_reciclador, id_p=id_punto)
    ok("Relación RETIRA_DE eliminada")


# ── TIENE_PUNTO_CERCANO ───────────────────────────────────────────────────────

def crear_punto_cercano(session):
    titulo("Crear: TIENE_PUNTO_CERCANO")
    usuario = int(pedir("ID Usuario"))
    punto   = int(pedir("ID Punto Verde"))
    session.run("""
        MATCH (u:Usuario {id_usuario: $u})
        MATCH (p:PuntoVerde {id: $p})
        MERGE (u)-[:TIENE_PUNTO_CERCANO]->(p)
    """, u=usuario, p=punto)
    ok("Relación TIENE_PUNTO_CERCANO creada")


def listar_puntos_cercanos(session):
    titulo("Listado: TIENE_PUNTO_CERCANO")
    filas = list(session.run("""
        MATCH (u:Usuario)-[:TIENE_PUNTO_CERCANO]->(p:PuntoVerde)
        RETURN u.id_usuario AS id_u, u.nombre AS usuario,
               p.id AS id_p, p.nombre AS punto
        ORDER BY usuario
    """))
    if not filas:
        print("  Sin relaciones registradas.")
        return
    print(f"  {NEGRITA}{'ID U':<6} {'Usuario':<25} {'ID P':<6} {'Punto Verde'}{RESET}")
    separador()
    for f in filas:
        print(f"  {f['id_u']:<6} {f['usuario']:<25} {f['id_p']:<6} {f['punto']}")


def eliminar_punto_cercano(session):
    titulo("Eliminar: TIENE_PUNTO_CERCANO")
    id_usuario = int(pedir("ID Usuario"))
    id_punto   = int(pedir("ID Punto Verde"))
    session.run("""
        MATCH (u:Usuario {id_usuario: $id_u})-[r:TIENE_PUNTO_CERCANO]->(p:PuntoVerde {id: $id_p})
        DELETE r
    """, id_u=id_usuario, id_p=id_punto)
    ok("Relación TIENE_PUNTO_CERCANO eliminada")


# ══════════════════════════════════════════════════════════════════════════════
#  CONSULTAS
# ══════════════════════════════════════════════════════════════════════════════

def consultas(session):
    titulo("Top 10 Usuarios por Puntos Ecológicos")
    filas = list(session.run("""
        MATCH (u:Usuario)
        RETURN u.nombre AS nombre, u.puntos_ecologicos AS puntos,
               u.nivel_usuario AS nivel
        ORDER BY puntos DESC
        LIMIT 10
    """))
    if not filas:
        print("  Sin datos.")
        return
    print(f"  {NEGRITA}{'#':<4} {'Nombre':<25} {'Puntos':>8} {'Nivel'}{RESET}")
    separador()
    for i, f in enumerate(filas, 1):
        medalla = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:>2}."
        print(f"  {medalla:<4} {f['nombre']:<25} {f['puntos']:>8} {f['nivel']}")


# ══════════════════════════════════════════════════════════════════════════════
#  SUBMENÚS POR NODO
# ══════════════════════════════════════════════════════════════════════════════

def menu_usuario(session):
    while True:
        limpiar()
        titulo("👤  Gestión de Usuarios")
        opcion(1, "Crear usuario",    "➕")
        opcion(2, "Listar usuarios",  "📋")
        opcion(3, "Modificar usuario","✏️ ")
        opcion(4, "Eliminar usuario", "🗑️ ")
        separador()
        opcion(0, "Volver al menú principal", "↩️ ")

        op = pedir("Opción")
        if   op == "1": limpiar(); crear_usuario(session);    esperar()
        elif op == "2": limpiar(); listar_usuarios(session);  esperar()
        elif op == "3": limpiar(); modificar_usuario(session);esperar()
        elif op == "4": limpiar(); eliminar_usuario(session); esperar()
        elif op == "0": break
        else: error("Opción inválida"); esperar()


def menu_residuo(session):
    while True:
        limpiar()
        titulo("♻️   Gestión de Tipos de Residuo")
        opcion(1, "Crear tipo de residuo",    "➕")
        opcion(2, "Listar tipos de residuo",  "📋")
        opcion(3, "Modificar tipo de residuo","✏️ ")
        opcion(4, "Eliminar tipo de residuo", "🗑️ ")
        separador()
        opcion(0, "Volver al menú principal", "↩️ ")

        op = pedir("Opción")
        if   op == "1": limpiar(); crear_tipo_residuo(session);    esperar()
        elif op == "2": limpiar(); listar_tipos_residuo(session);  esperar()
        elif op == "3": limpiar(); modificar_tipo_residuo(session);esperar()
        elif op == "4": limpiar(); eliminar_tipo_residuo(session); esperar()
        elif op == "0": break
        else: error("Opción inválida"); esperar()


def menu_punto_verde(session):
    while True:
        limpiar()
        titulo("🌿  Gestión de Puntos Verdes")
        opcion(1, "Crear punto verde",    "➕")
        opcion(2, "Listar puntos verdes", "📋")
        opcion(3, "Modificar punto verde","✏️ ")
        opcion(4, "Eliminar punto verde", "🗑️ ")
        separador()
        opcion(0, "Volver al menú principal", "↩️ ")

        op = pedir("Opción")
        if   op == "1": limpiar(); crear_punto_verde(session);    esperar()
        elif op == "2": limpiar(); listar_puntos_verdes(session);  esperar()
        elif op == "3": limpiar(); modificar_punto_verde(session); esperar()
        elif op == "4": limpiar(); eliminar_punto_verde(session);  esperar()
        elif op == "0": break
        else: error("Opción inválida"); esperar()


def menu_reciclador(session):
    while True:
        limpiar()
        titulo("🚛  Gestión de Recicladores")
        opcion(1, "Crear reciclador",    "➕")
        opcion(2, "Listar recicladores", "📋")
        opcion(3, "Modificar reciclador","✏️ ")
        opcion(4, "Eliminar reciclador", "🗑️ ")
        separador()
        opcion(0, "Volver al menú principal", "↩️ ")

        op = pedir("Opción")
        if   op == "1": limpiar(); crear_reciclador(session);    esperar()
        elif op == "2": limpiar(); listar_recicladores(session);  esperar()
        elif op == "3": limpiar(); modificar_reciclador(session); esperar()
        elif op == "4": limpiar(); eliminar_reciclador(session);  esperar()
        elif op == "0": break
        else: error("Opción inválida"); esperar()


def _submenu_rel(session, titulo_txt, fn_crear, fn_listar, fn_eliminar):
    """Submenú genérico para una relación: crear / listar / eliminar."""
    while True:
        limpiar()
        titulo(f"🔗  {titulo_txt}")
        opcion(1, "Crear relación",   "➕")
        opcion(2, "Listar relaciones","📋")
        opcion(3, "Eliminar relación","🗑️ ")
        separador()
        opcion(0, "Volver", "↩️ ")

        op = pedir("Opción")
        if   op == "1": limpiar(); fn_crear(session);   esperar()
        elif op == "2": limpiar(); fn_listar(session);  esperar()
        elif op == "3": limpiar(); fn_eliminar(session);esperar()
        elif op == "0": break
        else: error("Opción inválida"); esperar()


def menu_relaciones(session):
    while True:
        limpiar()
        titulo("🔗  Gestión de Relaciones")
        opcion(1, "RECICLA          Usuario ──► Residuo",           "")
        opcion(2, "ENTREGA_EN       Usuario ──► Punto Verde",       "")
        opcion(3, "ACEPTA           Punto Verde ──► Residuo",       "")
        opcion(4, "RECOLECTA        Reciclador ──► Residuo",        "")
        opcion(5, "RETIRA_DE        Reciclador ──► Punto Verde",    "")
        opcion(6, "TIENE_PTO_CERCANO  Usuario ──► Punto Verde",     "")
        separador()
        opcion(0, "Volver al menú principal", "↩️ ")

        op = pedir("Opción")
        if   op == "1":
            _submenu_rel(session, "RECICLA",
                         crear_recicla, listar_recicla, eliminar_recicla)
        elif op == "2":
            _submenu_rel(session, "ENTREGA_EN",
                         crear_entrega_en, listar_entrega_en, eliminar_entrega_en)
        elif op == "3":
            _submenu_rel(session, "ACEPTA",
                         crear_acepta, listar_acepta, eliminar_acepta)
        elif op == "4":
            _submenu_rel(session, "RECOLECTA",
                         crear_recolecta, listar_recolecta, eliminar_recolecta)
        elif op == "5":
            _submenu_rel(session, "RETIRA_DE",
                         crear_retira_de, listar_retira_de, eliminar_retira_de)
        elif op == "6":
            _submenu_rel(session, "TIENE_PUNTO_CERCANO",
                         crear_punto_cercano, listar_puntos_cercanos, eliminar_punto_cercano)
        elif op == "0": break
        else: error("Opción inválida"); esperar()


# ══════════════════════════════════════════════════════════════════════════════
#  MENÚ PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def menu_principal(session):
    while True:
        limpiar()
        print(f"\n{VERDE}{NEGRITA}")
        print("  ███████╗██╗██████╗  █████╗ ")
        print("  ██╔════╝██║██╔══██╗██╔══██╗")
        print("  ███████╗██║██████╔╝███████║")
        print("  ╚════██║██║██╔══██╗██╔══██║")
        print("  ███████║██║██║  ██║██║  ██║")
        print("  ╚══════╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝")
        print(f"{RESET}")
        print(f"  {GRIS}Sistema Inteligente de Reciclaje y Ambiente{RESET}\n")
        separador()

        opcion(1, "Usuarios",        "👤")
        opcion(2, "Tipos de Residuo","♻️ ")
        opcion(3, "Puntos Verdes",   "🌿")
        opcion(4, "Recicladores",    "🚛")
        separador()
        opcion(5, "Relaciones entre nodos", "🔗")
        separador()
        opcion(6, "Consultas / Rankings",   "📊")
        separador()
        opcion(0, "Salir", "🚪")

        op = pedir("Opción")
        if   op == "1": menu_usuario(session)
        elif op == "2": menu_residuo(session)
        elif op == "3": menu_punto_verde(session)
        elif op == "4": menu_reciclador(session)
        elif op == "5": menu_relaciones(session)
        elif op == "6": limpiar(); consultas(session); esperar()
        elif op == "0":
            limpiar()
            print(f"\n  {VERDE}¡Hasta luego! 🌱{RESET}\n")
            break
        else:
            error("Opción inválida")
            esperar()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

with driver.session() as session:
    menu_principal(session)

driver.close()