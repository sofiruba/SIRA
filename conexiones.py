from pymongo import MongoClient
from neo4j import GraphDatabase
from cassandra.cluster import Cluster

MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "sira"

NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Homero1234"
NEO4J_DATABASE = "neo4j"

CASSANDRA_HOST = "127.0.0.1"
CASSANDRA_PORT = 9042
CASSANDRA_KEYSPACE = "sira"

def obtener_colecciones_mongo():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]

    coleccion_puntos = db["puntos_verdes"]
    coleccion_residuos = db["tipos_residuos"]

    return coleccion_puntos, coleccion_residuos


def obtener_driver_neo4j():
    return GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )

def obtener_cassandra_session():
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
    session = cluster.connect(CASSANDRA_KEYSPACE)
    return session

