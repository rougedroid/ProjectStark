import pickle
import river
import neo4j

URI = "neo4j://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "password"
driver = neo4j.GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

def save_model(model, filename):
    with open(filename, 'wb') as f:
        pickle.dump(model, f)   

def load_model(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)       

def init_model(model_type, filename):
    model = model_type
    save_model(model, filename)
    return model

def train_model(model, X_train, y_train):
    model.learn_one(X_train, y_train)
    return model

def predict(model, X_test):
    return model.predict_one(X_test)

def predict_proba(model, X_test):
    return model.predict_proba_one(X_test)

"""
def string_vectorizer(dict_input):
    
    for key in dict_input:
        if isinstance(dict_input[key], str):
            dict_input[key] = hash(dict_input[key])
    return dict_input
"""