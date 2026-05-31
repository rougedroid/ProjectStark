import master
import neo4j
import requests
from neo4j import GraphDatabase
import utilities as utils
import json
# Update neo4j graphs to have a score for each relationship type. since they are limited, we can hardcode a specific relation for each kind of search task. 






def fetch_nodes_by_label(phrase):
    response = requests.post("http://localhost:11434/api/embeddings",
    json={"model": "all-minilm", "prompt": phrase})
    
    phrase_embedding = response.json()["embedding"]
    

    with utils.driver.session(database="cskg") as session:
        result = session.run(
            """
            MATCH (n:Node)
            SEARCH n IN (VECTOR INDEX fullTextEmbedding FOR $phrase_embedding LIMIT 1)
            SCORE AS similarity
            RETURN n, similarity
            """,
            phrase_embedding=phrase_embedding
        )
        print([record for record in result])
        for record in result:
            print(record["n"], record["similarity"])       
        output = [(record["n"], record["similarity"]) for record in result]
    # Using the search to give top one node directly. 
    return output[0] if output else None

    

def answer(input_dict):
    pass

print(fetch_nodes_by_label("What is quantum computing?"))
