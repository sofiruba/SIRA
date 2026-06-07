# SIRA - Sistema Inteligente de Reciclaje Ambiental

SIRA es un proyecto de Ingeniería de Datos II orientado a la gestión inteligente de residuos reciclables. La solución integra distintas bases de datos NoSQL, utilizando cada tecnología según el tipo de información que mejor resuelve.

El sistema cuenta con una interfaz visual desarrollada en Python con Streamlit, desde donde se pueden consultar y operar datos almacenados en MongoDB, Neo4j, Redis y Cassandra.

---

## Tecnologías utilizadas

* Python 3
* Streamlit
* Pandas
* MongoDB
* Neo4j
* Redis
* Cassandra
* Docker
* PyMongo
* Neo4j Python Driver
* redis-py
* cassandra-driver

---

## Rol de cada base de datos

### MongoDB

MongoDB almacena datos descriptivos y flexibles del sistema, como:

* puntos verdes;
* tipos de residuos;
* horarios;
* barrios;
* comunas;
* residuos aceptados por cada punto verde.

### Neo4j

Neo4j almacena y consulta relaciones entre entidades, como:

* usuarios;
* puntos verdes;
* tipos de residuos;
* recicladores.

Relaciones principales:

* `RECICLA`
* `ENTREGA_EN`
* `ACEPTA`
* `RECOLECTA`
* `RETIRA_DE`
* `TIENE_PUNTO_CERCANO`

### Redis

Redis se utiliza para información temporal y de acceso rápido:

* estado actual de puntos verdes;
* capacidad actual;
* puntos verdes disponibles;
* puntos verdes saturados;
* ranking de uso;
* alertas recientes.

### Cassandra

Cassandra se utiliza para datos históricos y consultas orientadas a grandes volúmenes:

* recolecciones por usuario;
* recolecciones por punto verde;
* recolecciones por ID;
* retiros por reciclador;
* actividad por zona;
* residuos por mes.

---

# Instalación y ejecución del proyecto

## 1. Clonar el repositorio

```bash
git clone https://github.com/sofiruba/SIRA.git
cd SIRA
```

---

## 2. Crear entorno virtual

En macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Instalar dependencias de Python

Con el entorno virtual activado:

```bash
python -m pip install --upgrade pip
python -m pip install streamlit pandas pymongo neo4j redis cassandra-driver
```

Opcionalmente, si existe un `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

Para generar `requirements.txt`:

```bash
python -m pip freeze > requirements.txt
```

---

# Inicialización de bases de datos

Antes de ejecutar la app, se deben prender las bases de datos.

---

## 4. Iniciar MongoDB

En macOS con Homebrew:

```bash
brew services start mongodb/brew/mongodb-community@7.0
```

Verificar que MongoDB esté funcionando:

```bash
mongosh
```

Dentro de `mongosh`:

```javascript
show dbs
use sira
show collections
```

La base utilizada por el proyecto es:

```text
sira
```

Para salir de `mongosh`:

```javascript
exit
```

---

## 5. Cargar datos en MongoDB

Desde la raíz del proyecto:

```bash
python mongodb_app/SIRA_mongodb.py
```

Si el archivo principal de carga está en otra ubicación, ejecutar el script correspondiente dentro de `mongodb_app`.

También puede utilizarse el módulo interactivo si se desea probar operaciones desde consola:

```bash
python mongodb_app/SIRA_mongodb_interactivo.py
```

---

## 6. Iniciar Neo4j

Abrir **Neo4j Desktop** y hacer clic en **Start** sobre la base de datos del proyecto.

La app se conecta con la siguiente configuración:

```text
URI: bolt://127.0.0.1:7687
Usuario: neo4j
Contraseña: Homero1234
Base de datos: sira
```

Para verificar desde Neo4j Browser:

```cypher
MATCH (n) RETURN n LIMIT 10;
```

También se puede verificar cantidad de nodos:

```cypher
MATCH (n) RETURN count(n);
```

Y cantidad de relaciones:

```cypher
MATCH ()-[r]->() RETURN count(r);
```

---

## 7. Iniciar Redis

En macOS con Homebrew:

```bash
brew services start redis
```

Verificar que Redis esté funcionando:

```bash
redis-cli ping
```

Debe responder:

```text
PONG
```

---

## 8. Cargar datos en Redis

Desde la raíz del proyecto:

```bash
python redis_app/carga_Redis.py
```

El script carga los datos desde:

```text
redis_data.json
```

Para verificar las claves cargadas:

```bash
redis-cli
```

Dentro de Redis:

```bash
KEYS *
```

Deberían aparecer claves similares a:

```text
puntoverde:1:estado
puntosverdes:disponibles
puntosverdes:saturados
ranking:puntosverdes:uso
alertas:recientes
```

Para salir de Redis CLI:

```bash
exit
```

---

## 9. Iniciar Docker

Cassandra se ejecuta mediante Docker. Primero abrir **Docker Desktop** y esperar a que esté activo.

Verificar Docker:

```bash
docker ps
```

Si Docker está funcionando, se mostrará una tabla de contenedores.

---

## 10. Iniciar Cassandra

El contenedor de Cassandra utilizado por el proyecto se llama:

```text
sira
```

Prender el contenedor:

```bash
docker start sira
```

Verificar que esté corriendo:

```bash
docker ps
```

Debe aparecer un contenedor con imagen `cassandra:4.1` y puerto:

```text
0.0.0.0:9042->9042/tcp
```

Entrar a Cassandra:

```bash
docker exec -it sira cqlsh
```

---

## 11. Crear keyspace de Cassandra

Dentro de `cqlsh`, crear el keyspace si no existe:

```sql
CREATE KEYSPACE IF NOT EXISTS sira
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
```

Verificar que exista:

```sql
DESCRIBE KEYSPACES;
```

Entrar al keyspace:

```sql
USE sira;
```

Para ver tablas:

```sql
DESCRIBE TABLES;
```

Salir:

```sql
exit;
```

---

## 12. Cargar datos en Cassandra

Desde la raíz del proyecto:

```bash
python cassandra_app/carga_cassandra.py
```

Este script crea las tablas necesarias y carga los datos desde los archivos CSV ubicados en `cassandra_app`, como:

```text
cassandra_app/recolecciones.csv
cassandra_app/retiros.csv
```

---

## 13. Probar consultas de Cassandra

```bash
python cassandra_app/consultas_cassandra.py
```

También se puede verificar manualmente desde `cqlsh`:

```bash
docker exec -it sira cqlsh
```

Dentro de Cassandra:

```sql
USE sira;
DESCRIBE TABLES;
SELECT * FROM recolecciones_por_id LIMIT 10;
SELECT * FROM recolecciones_por_usuario LIMIT 10;
```

Para buscar una recolección por ID:

```sql
SELECT * FROM recolecciones_por_id WHERE recoleccion_id = '30';
```

---

# Ejecutar la aplicación visual

Con todas las bases iniciadas, ejecutar Streamlit desde la raíz del proyecto:

```bash
python -m streamlit run app.py
```

Luego abrir en el navegador la URL indicada por Streamlit, normalmente:

```text
http://localhost:8501
```

---

# Orden recomendado para levantar todo

## Paso 1: Activar entorno virtual

```bash
source .venv/bin/activate
```

## Paso 2: Prender MongoDB

```bash
brew services start mongodb/brew/mongodb-community@7.0
```

## Paso 3: Prender Redis

```bash
brew services start redis
```

## Paso 4: Prender Docker Desktop

Abrir Docker Desktop manualmente y verificar:

```bash
docker ps
```

## Paso 5: Prender Cassandra

```bash
docker start sira
```

## Paso 6: Prender Neo4j

Abrir Neo4j Desktop y hacer clic en **Start** sobre la base `sira`.

## Paso 7: Correr la app

```bash
python -m streamlit run app.py
```

---

# Comandos útiles para verificar cada base

## MongoDB

```bash
mongosh
```

```javascript
use sira
show collections
```

---

## Redis

```bash
redis-cli ping
```

```bash
redis-cli
KEYS *
```

---

## Cassandra

```bash
docker exec -it sira cqlsh
```

```sql
USE sira;
DESCRIBE TABLES;
```

---

## Neo4j

Desde Neo4j Browser:

```cypher
MATCH (n) RETURN count(n);
MATCH ()-[r]->() RETURN count(r);
```

---

# Apagar servicios

## Apagar MongoDB

```bash
brew services stop mongodb/brew/mongodb-community@7.0
```

## Apagar Redis

```bash
brew services stop redis
```

## Apagar Cassandra

```bash
docker stop sira
```

## Apagar Neo4j

Desde Neo4j Desktop, hacer clic en **Stop** sobre la base de datos.

---

# Estructura general del proyecto

```text
SIRA/
│
├── app.py
├── conexiones.py
├── README.md
│
├── mongodb_app/
│   ├── SIRA_mongodb.py
│   ├── SIRA_mongodb_funciones.py
│   └── SIRA_mongodb_interactivo.py
│
├── neo4j_app/
│   ├── consultas_neo.py
│   ├── consultas_terminal_neo.py
│   ├── crud_terminal_neo.py
│   ├── neo_crud_app.py
│   ├── puntos_verdes.csv
│   ├── recicladores.csv
│   ├── tipos_residuos.csv
│   └── usuarios_sira.csv
│
├── redis_app/
│   ├── carga_Redis.py
│   └── redis_data.json
│
├── cassandra_app/
│   ├── carga_cassandra.py
│   ├── consultas_cassandra.py
│   ├── cassandra_crud_app.py
│   ├── recolecciones.csv
│   └── retiros.csv
│
└── .venv/
```

---

# Funcionalidades de la app

## MongoDB

Desde la interfaz se puede:

* consultar puntos verdes;
* consultar tipos de residuos;
* buscar punto verde por ID;
* crear residuos;
* crear puntos verdes;
* actualizar horarios;
* actualizar residuos;
* eliminar puntos verdes;
* eliminar residuos.

## Neo4j

Desde la interfaz se puede:

* consultar puntos verdes cercanos;
* consultar usuarios por barrio;
* consultar puntos verdes por comuna;
* ver top de usuarios;
* consultar usuarios y residuos reciclados;
* consultar puntos verdes y residuos aceptados;
* consultar recicladores y residuos;
* consultar residuos más reciclados;
* crear usuarios;
* crear relaciones;
* actualizar puntos ecológicos;
* eliminar usuarios;
* eliminar relaciones.

## Redis

Desde la interfaz se puede:

* cargar datos desde JSON;
* consultar estado de un punto verde;
* consultar puntos disponibles;
* consultar puntos saturados;
* consultar ranking de uso;
* consultar alertas recientes;
* actualizar estado y capacidad;
* eliminar estado temporal de un punto verde;
* eliminar alertas.

## Cassandra

Desde la interfaz se puede:

* cargar datos históricos;
* consultar recolecciones por usuario;
* consultar recolecciones por punto verde;
* consultar recolecciones por ID;
* consultar retiros por reciclador;
* consultar actividad por zona;
* crear nuevas recolecciones;
* consultar datos históricos modelados por query.

---

# Notas importantes

* La base de datos principal se llama `sira`.
* El contenedor de Cassandra se llama `sira`.
* Cassandra puede tardar algunos minutos en iniciar.
* Redis y MongoDB deben estar prendidos antes de ejecutar la app.
* Neo4j debe estar iniciado desde Neo4j Desktop.
* La app utiliza Streamlit como interfaz visual.
* El sistema no implementa consistencia transaccional estricta entre bases, ya que el objetivo es demostrar el uso de cada motor NoSQL según su propósito.
* Cada base se modela de acuerdo con el tipo de consulta que debe resolver.
