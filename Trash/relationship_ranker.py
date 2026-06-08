from river import facto
from river import linear_model
import model_manager
import models
from neo4j import GraphDatabase

# Pre Processing and Feature Engineering functions would go here, such as encoding categorical variables, normalizing numerical features, etc.
model = facto.FMClassifier()

try:
    loadmodel = model_manager.load_model(models.relationship_model)
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Model file not found. Initializing new model.")
    loadmodel = model_manager.init_model(model, models.relationship_model)

def predict_relation_value(context_parameters, relationship_properties):
    # This function would take in the features of the relationship and return a prediction using the loaded model.
    # For example, it might take in a dictionary of features, preprocess them, and then call model_manager.predict() to get the prediction.
    # This model predicts each individual relationship value, so it would be called for each relationship in the graph to rank them accordingly.
    # This model will take in context parameters a.k.a. the reason for the data call, i.e. question, reasoning or what. 


    pass

def get_relationship_score(elementID):
    # This function will rank the value of relationship value of each node. 
    relationships = get_relations(elementID)
    relationship_scores = {}
    
    pass

def train_relationship_model(X_train, y_train):
    # This function would take in training data for the relationships, preprocess it, and then call model_manager.train_model() to update the model with the new training data.
    pass

def get_relations(elementID):
    # This function would query the Neo4j graph database to retrieve the relationships for a given node ID, and then call predict_relation_value() for each relationship to get their predicted values.
    with models.driver.session(database="cskg") as session:
        result = session.run(
            "MATCH (n)-[r]->(m) WHERE elementId(n) = $elementID RETURN type(r) AS relationship_type, properties(r) AS relationship_properties",
            elementID=elementID
        )
        relationships = []
        for record in result:
            relationship_type = record["relationship_type"]
            relationship_properties = record["relationship_properties"]
            relationships.append((relationship_type, relationship_properties))

    return relationships

id = "4:503106f2-a350-450c-945d-070fca915f43:47643"

relationships = get_relations(id)
for relationship in relationships:
    print(relationship)
