# SIRA - Sistema Inteligente de Reciclaje Ambiental

SIRA es una plataforma orientada a la gestión inteligente de residuos reciclables. El proyecto integra distintas bases de datos NoSQL según el tipo de información que se necesita almacenar o consultar.

## Tecnologías utilizadas

* Python
* Streamlit
* MongoDB
* Neo4j
* Redis
* Cassandra
* Pandas
* PyMongo
* Neo4j Python Driver
* redis-py

## Rol de cada base de datos

### MongoDB

MongoDB se utiliza para almacenar datos flexibles y descriptivos, como:

* puntos verdes;
* tipos de residuos;
* residuos aceptados;
* horarios;
* barrios;
* comunas.

### Neo4j

Neo4j se utiliza para representar relaciones entre entidades del sistema, como:

* usuarios;
* puntos verdes;
* tipos de residuos;
* recicladores.

Ejemplos de relaciones:

* `RECICLA`
* `ENTREGA_EN`
* `ACEPTA`
* `RECOLECTA`
* `RETIRA_DE`
* `TIENE_PUNTO_CERCANO`

### Redis

Redis se utiliza para información temporal y de acceso rápido, como:

* estado actual de puntos verdes;
* puntos disponibles;
* puntos saturados;
* ranking de uso;
* alertas recientes.

### Cassandra

Cassandra se utiliza para modelar datos históricos y de gran volumen, como registros de recolecciones, entregas y actividad por zona.

---

# Cómo correr el proyecto

## 1. Clonar el repositorio

```bash
git clone https://github.com/sofiruba/SIRA.git
cd SIRA
```

---

## 2. Crear y activar entorno virtual

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

## 3. Instalar dependencias

```bash
python -m pip install streamlit pandas pymongo neo4j redis cassandra-driver
```

También se puede generar un archivo `requirements.txt` con:

```bash
python -m pip freeze > requirements.txt
```

Y luego instalarlo con:

```bash
python -m pip install -r requirements.txt
```

---

# Bases de datos necesarias

Antes de ejecutar la aplicación, deben estar iniciadas las bases de datos usadas por el proyecto.

---

## 4. Iniciar MongoDB

En macOS con Homebrew:

```bash
brew services start mongodb/brew/mongodb-community@7.0
```

Verificar que esté funcionando:

```bash
mongosh
```

Dentro de `mongosh`:

```javascript
show dbs
use sira
show collections
```

La base de datos utilizada por el proyecto se llama:

```text
sira
```

---

## 5. Cargar datos en MongoDB

El proyecto utiliza archivos JSON como:

* `puntos_verdes.json`
* `tipos_residuos.json`

Para cargar los datos, ejecutar:

```bash
python SIRA_mongodb.py
```

También puede utilizarse el archivo interactivo de MongoDB si se quiere probar operaciones desde consola:

```bash
cd mongodb
```
```bash
python SIRA_mongodb_interactivo.py
```

---

## 6. Iniciar Neo4j

Abrir Neo4j Desktop y hacer clic en **Start** sobre la base de datos del proyecto.

La aplicación se conecta con los siguientes datos:

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

Para ejecutar consultas de Neo4j desde consola:

```bash
python neo4j/consultas_neo.py
```

Para ejecutar el CRUD de Neo4j por consola:

```bash
python neo4j/backneocrud.py
```

---

## 7. Iniciar Redis

En macOS con Homebrew:

```bash
brew services start redis
```

Verificar conexión:

```bash
redis-cli ping
```

Debe responder:

```text
PONG
```

---

## 8. Cargar datos en Redis

El proyecto utiliza el archivo:

```text
redis_data.json
```

Para cargar los datos en Redis:

```bash
python carga_Redis.py
```

Para verificar que se cargaron las claves:

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

---

## 9. Iniciar Cassandra

Si se utiliza Docker:

```bash
docker run --name cassandra-sira -p 9042:9042 -d cassandra:4.1
```

Si el contenedor ya existe:

```bash
docker start cassandra-sira
```

Verificar que Cassandra esté corriendo:

```bash
docker ps
```

Entrar a Cassandra:

```bash
docker exec -it cassandra-sira cqlsh
```

```bash
CREATE KEYSPACE sira
WITH replication = {
'class':'SimpleStrategy',
'replication_factor':1
};
```


```bash
USE sira;
```
---

# Ejecutar la interfaz visual

La interfaz principal está desarrollada con Streamlit.

Para correr la aplicación:

```bash
python -m streamlit run app.py
```

Luego abrir en el navegador la URL que indique Streamlit, normalmente:

```text
http://localhost:8501
```

---

# Estructura del proyecto

```text
SIRA/
│
├── app.py
├── conexiones.py
│
├── SIRA_mongodb.py
├── SIRA_mongodb_funciones.py
├── SIRA_mongodb_interactivo.py
│
├── consultasNeo.py
├── backneo.py
├── backneocrud.py
│
├── carga_Redis.py
├── redis_crud_app.py
│
├── mongo_crud_app.py
├── neo4j_crud_app.py
│
├── puntos_verdes.json
├── tipos_residuos.json
├── redis_data.json
├── usuarios-sira.csv
├── recicladores.csv
│
└── README.md
```

---

# Funcionalidades actuales de la app

## MongoDB

Desde la interfaz se pueden realizar:

* consultas sobre puntos verdes;
* consultas sobre tipos de residuos;
* búsqueda de punto verde por ID;
* creación de residuos;
* creación de puntos verdes;
* actualización de horarios;
* actualización de tipos de residuos;
* eliminación de puntos verdes;
* eliminación de residuos.

## Neo4j

Desde la interfaz se pueden realizar:

* consultas sobre relaciones;
* ranking de usuarios;
* usuarios por barrio;
* puntos verdes por comuna;
* residuos más reciclados;
* tipos de residuos por punto verde;
* creación de usuarios;
* creación de relaciones;
* actualización de puntos ecológicos;
* eliminación de usuarios;
* eliminación de relaciones.

## Redis

Desde la interfaz se pueden realizar:

* carga de datos desde `redis_data.json`;
* consulta de estado de punto verde por ID;
* consulta de puntos disponibles;
* consulta de puntos saturados;
* ranking de puntos verdes por uso;
* consulta de alertas recientes;
* actualización de estado y capacidad de un punto verde;
* eliminación de estado temporal de un punto verde;
* eliminación de alertas recientes.

---

# Orden recomendado para correr la demo

1. Iniciar MongoDB.
2. Cargar datos de MongoDB.
3. Iniciar Neo4j desde Neo4j Desktop.
4. Iniciar Redis.
5. Cargar datos de Redis.
6. Iniciar Cassandra si se va a mostrar esa parte.
7. Ejecutar la app con Streamlit.

Comandos principales:

```bash
brew services start mongodb/brew/mongodb-community@7.0
brew services start redis
docker start cassandra-sira
python -m streamlit run app.py
```

Neo4j debe iniciarse manualmente desde Neo4j Desktop.

---

# Notas importantes

* La base de MongoDB utilizada se llama `sira`.
* La base de Neo4j utilizada se llama `sira`.
* Redis debe estar iniciado antes de usar la sección Redis de la app.
* Cassandra puede tardar algunos minutos en iniciar dentro de Docker.
* La interfaz `app.py` reutiliza módulos ya desarrollados para MongoDB, Neo4j y Redis, evitando repetir toda la lógica de base de datos dentro de la app.
* Los datos utilizados son de prueba y sirven para demostrar el funcionamiento de la arquitectura NoSQL del proyecto.
