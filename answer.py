import master
import neo4j
import requests
from neo4j import GraphDatabase
import utilities as utils
import json
# Update neo4j graphs to have a score for each relationship type. since they are limited, we can hardcode a specific relation for each kind of search task. 






def fetch_seed_node(keyword, phrase):
    response = requests.post("http://localhost:11434/api/embeddings",
    json={"model": "all-minilm", "prompt": phrase})
    
    phrase_embedding = response.json()["embedding"]
    
    #print("Embedding:", phrase_embedding)
    with utils.driver.session(database="cskg") as session:
        result = session.run(
            """
            MATCH (n:Node)
            SEARCH n IN (VECTOR INDEX cskg_concept_embeddings FOR $phrase_embedding LIMIT 10)
            SCORE AS similarity
            RETURN elementId(n) AS nodeid, similarity
            ORDER BY similarity DESC
            """,
            phrase_embedding=phrase_embedding
        )
        output = [(record["nodeid"], record["similarity"]) for record in result]
        # for record in result:
        #     print(record["n"], record["similarity"])       
    
    formatted_output = {
        "nodeid": output[0][0],
        "similarity": output[0][1]
    }

    # Using the search to give top one node directly. 
    return output if output else None



def answer(input_dict):
    question_type = input_dict.get("intent")
    if question_type == "question-general":
        # process general question
        # use key-word search for seeding. Then, explore 1 branch laterally upto 5 nodes. Then, explore 2 highest topology scoring neighbours from those 5 nodes. Then, use that information to answer the question.
        find_seed_node = fetch_seed_node(input_dict.get("keyword"), input_dict.get("phrase"))
        search_space(find_seed_node, depth=2, breadth=5)
        pass
    elif question_type == "question-specific":
        # process specific question
        pass
    elif question_type == "question-general-changing":
        # process general changing question
        pass
    pass

print(fetch_seed_node("quantum computing"),"")
