# SIRA - Sistema Inteligente de Reciclaje Ambiental

SIRA es una plataforma para la gestión inteligente de residuos reciclables en la Ciudad de Buenos Aires. Permite consultar puntos verdes, ver disponibilidad en tiempo real, administrar residuos, analizar relaciones entre entidades y registrar históricos de recolección.

El proyecto integra distintas bases de datos NoSQL, usando cada una según el tipo de información que mejor resuelve.

---

## Objetivo del proyecto

El objetivo es demostrar una arquitectura NoSQL aplicada a un caso de economía circular y gestión ambiental urbana.

La aplicación permite:

* consultar puntos verdes y residuos aceptados;
* visualizar disponibilidad y saturación;
* registrar y consultar recolecciones;
* analizar relaciones entre usuarios, residuos, puntos verdes y recicladores;
* administrar datos desde una interfaz visual en Streamlit.

---

## Rol de cada base de datos

### MongoDB

MongoDB almacena datos descriptivos y flexibles:

* puntos verdes;
* direcciones;
* barrios;
* comunas;
* horarios;
* tipos de residuos;
* residuos aceptados.

Se usa porque permite trabajar con documentos flexibles.

### Neo4j

Neo4j almacena relaciones entre entidades:

* usuarios;
* puntos verdes;
* residuos;
* recicladores.

Relaciones principales:

* `RECICLA`
* `ENTREGA_EN`
* `ACEPTA`
* `RECOLECTA`
* `RETIRA_DE`
* `TIENE_PUNTO_CERCANO`

Se usa porque permite consultar conexiones entre entidades de forma simple.

### Redis

Redis almacena información temporal y de acceso rápido:

* estado actual de puntos verdes;
* capacidad actual;
* puntos disponibles;
* puntos saturados;
* ranking;
* alertas recientes.

Las alertas son avisos operativos recientes. No necesariamente todos los puntos saturados tienen una alerta activa.

### Cassandra

Cassandra almacena datos históricos de recolecciones y retiros.

Se modela por consulta, por eso una misma recolección puede guardarse en varias tablas:

* `recolecciones_por_id`
* `recolecciones_por_usuario`
* `recolecciones_por_punto_verde`
* `retiros_por_reciclador`
* `actividad_por_zona`
* `residuos_por_mes`

Esto permite consultas rápidas, aunque implique duplicación controlada.

---

## Consistencia entre bases

El sistema no busca consistencia transaccional estricta entre todas las bases.

Cada base cumple una función distinta:

* MongoDB guarda datos descriptivos.
* Neo4j guarda relaciones.
* Redis guarda estados temporales.
* Cassandra guarda históricos.

Por eso no es necesario que todas las bases tengan exactamente los mismos datos.

Sí se mantiene coherencia interna dentro de cada motor. Por ejemplo, en Redis, si un punto pasa a `saturado`, se actualizan los sets correspondientes y puede generarse una alerta. En Cassandra, si se actualiza una recolección, el cambio se replica en las tablas principales donde esa recolección fue almacenada.

---

## Estructura del proyecto

```text
TPO-INGENIERIA DE DATOS II/
│
├── app.py
├── conexiones.py
├── README.md
├── .gitignore
├── .gitattributes
│
├── imagen/
│   ├── logo_sira.png
│   └── nombre_sira.png
│
├── vistas/
│   ├── vista_ciudadano.py
│   ├── vista_administrador.py
│   ├── seccion_mongo.py
│   ├── seccion_neo.py
│   ├── seccion_redis.py
│   └── seccion_cassandra.py
│
├── mongodb_app/
│   ├── consultas_mongo.py
│   ├── mongo_crud_app.py
│   ├── puntos_verdes.json
│   └── tipos_residuos.json
│
├── neo4j_app/
│   ├── consultas_neo.py
│   ├── neo_crud_app.py
│   ├── consultas_terminal_neo.py
│   ├── crud_terminal_neo.py
│   ├── puntos_verdes.csv
│   ├── recicladores.csv
│   ├── tipos_residuos.csv
│   └── usuarios_sira.csv
│
├── redis_app/
│   ├── carga_redis.py
│   ├── consultas_redis.py
│   ├── redis_crud_app.py
│   └── redis_data.json
│
└── cassandra_app/
    ├── carga_cassandra.py
    ├── consultas_cassandra.py
    ├── cassandra_crud_app.py
    ├── recolecciones.csv
    └── retiros.csv
```

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/sofiruba/SIRA.git
cd SIRA
```

## 2. Crear entorno virtual

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3. Instalar librerías necesarias

```bash
python -m pip install streamlit pandas pymongo neo4j redis cassandra-driver pillow
```

---

# Inicialización de bases de datos

## MongoDB

Iniciar MongoDB:

```bash
brew services start mongodb/brew/mongodb-community@7.0
```

Verificar:

```bash
mongosh
```

Dentro de `mongosh`:

```javascript
use sira
show collections
```

Salir:

```javascript
exit
```

Los datos base se encuentran en:

```text
mongodb_app/puntos_verdes.json
mongodb_app/tipos_residuos.json
```

---

## Neo4j

Abrir **Neo4j Desktop** y hacer clic en **Start** sobre la base del proyecto.

Configuración utilizada:

```text
URI: bolt://127.0.0.1:7687
Usuario: neo4j
Contraseña: Homero1234
Base de datos: sira
```

Verificar desde Neo4j Browser:

```cypher
MATCH (n) RETURN n LIMIT 10;
```

Los archivos base se encuentran en:

```text
neo4j_app/puntos_verdes.csv
neo4j_app/recicladores.csv
neo4j_app/tipos_residuos.csv
neo4j_app/usuarios_sira.csv
```

---

## Redis

Iniciar Redis:

```bash
brew services start redis
```

Verificar:

```bash
redis-cli ping
```

Debe responder:

```text
PONG
```

Cargar datos:

```bash
python redis_app/carga_redis.py
```

Ver claves cargadas:

```bash
redis-cli
KEYS *
```

Salir:

```bash
exit
```

---

## Cassandra

Cassandra se ejecuta con Docker. Primero abrir **Docker Desktop**.

Verificar Docker:

```bash
docker ps
```

Iniciar el contenedor:

```bash
docker start sira
```

Entrar a Cassandra:

```bash
docker exec -it sira cqlsh
```

Crear el keyspace si no existe:

```sql
CREATE KEYSPACE IF NOT EXISTS sira
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
```

Entrar al keyspace:

```sql
USE sira;
```

Ver tablas:

```sql
DESCRIBE TABLES;
```

Salir:

```sql
exit;
```

Cargar datos:

```bash
python cassandra_app/carga_cassandra.py
```

Verificar:

```bash
docker exec -it sira cqlsh
```

```sql
USE sira;
SELECT * FROM recolecciones_por_id LIMIT 10;
```

---

# Ejecutar la aplicación

Con las bases iniciadas, ejecutar:

```bash
python -m streamlit run app.py
```

Abrir la URL indicada por Streamlit, normalmente:

```text
http://localhost:8501
```

---

# Orden recomendado para correr la demo

```bash
source .venv/bin/activate
brew services start mongodb/brew/mongodb-community@7.0
brew services start redis
docker start sira
python redis_app/carga_redis.py
python cassandra_app/carga_cassandra.py
python -m streamlit run app.py
```

Además, iniciar Neo4j manualmente desde **Neo4j Desktop**.

---

# Funcionalidades principales

## Inicio

Muestra una presentación general del sistema y métricas principales:

* puntos verdes;
* tipos de residuos;
* puntos disponibles;
* puntos saturados.

## Portal del ciudadano

Permite:

* buscar puntos verdes y residuos con MongoDB;
* consultar estados en tiempo real con Redis;
* visualizar comunidad y relaciones con Neo4j.

## Panel del administrador

Permite:

* gestionar puntos verdes y residuos con MongoDB;
* gestionar nodos y relaciones con Neo4j;
* monitorear estados y alertas con Redis;
* registrar y consultar recolecciones históricas con Cassandra.

---

# Apagar servicios

## MongoDB

```bash
brew services stop mongodb/brew/mongodb-community@7.0
```

## Redis

```bash
brew services stop redis
```

## Cassandra

```bash
docker stop sira
```

## Neo4j

Desde **Neo4j Desktop**, hacer clic en **Stop**.

## Streamlit

En la terminal donde está corriendo la app:

```bash
CTRL + C
```

---

# Explicación técnica para la defensa

SIRA utiliza una arquitectura NoSQL distribuida por responsabilidades.

MongoDB se usa para documentos flexibles, Neo4j para relaciones, Redis para estados temporales y Cassandra para históricos modelados por consulta.

En Cassandra, las tablas se diseñan según las consultas. Por eso una misma recolección puede estar duplicada en distintas tablas. Esto permite consultar rápido por ID, usuario o punto verde, aunque requiere actualizar o eliminar el dato en las tablas principales donde fue almacenado.

En Redis, los datos representan estados temporales. Las alertas recientes son avisos operativos para el administrador y no necesariamente coinciden uno a uno con todos los puntos saturados.

---

# Notas importantes

* La base principal se llama `sira`.
* El contenedor Docker de Cassandra se llama `sira`.
* Neo4j debe iniciarse desde Neo4j Desktop.
* Redis, MongoDB y Cassandra deben estar activos antes de ejecutar la app.
* Cassandra puede tardar algunos minutos en iniciar.
* La aplicación principal se ejecuta con `app.py`.
* Los datos son simulados y se utilizan para demostrar el funcionamiento de la arquitectura NoSQL.
