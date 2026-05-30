
from neo4j import GraphDatabase
import model_manager

connection_uri = "neo4j://localhost:7687"
username = "neo4j"
password = "testpass"

driver = GraphDatabase.driver(connection_uri, auth=(username, password))

relationship_model = 'models/relationship_model.pkl'

