import master
import neo4j
import requests
from neo4j import GraphDatabase
import utilities as utils
import json
# Update neo4j graphs to have a score for each relationship type. since they are limited, we can hardcode a specific relation for each kind of search task. 






def fetch_seed_node(keyword, phrase):
    response_keyword = requests.post("http://localhost:11434/api/embeddings",
    json={"model": "all-minilm", "prompt": keyword})
    response_phrase = requests.post("http://localhost:11434/api/embeddings",
    json={"model": "all-minilm", "prompt": phrase})

    keyword_embedding = response_keyword.json()["embedding"]
    phrase_embedding = response_phrase.json()["embedding"]
    
    #print("Embedding:", phrase_embedding)
    with utils.driver.session(database="cskg") as session:
        query = """
            // Step 1: Locate entry anchors
            MATCH (keywordAnchor:Node)
            SEARCH keywordAnchor IN (VECTOR INDEX cskg_concept_embeddings FOR $keyword_embedding LIMIT 1)
            
            MATCH (phraseAnchor:Node)
            SEARCH phraseAnchor IN (VECTOR INDEX cskg_concept_embeddings FOR $phrase_embedding LIMIT 1)
            WHERE keywordAnchor <> phraseAnchor
            
            // Step 2: Find the connecting backbone path
            MATCH path = shortestPath((keywordAnchor)-[*..4]-(phraseAnchor))
            WITH keywordAnchor, phraseAnchor, nodes(path) AS pathNodes
            
            // Create a unified pool of all core nodes
            WITH pathNodes + [keywordAnchor, phraseAnchor] AS coreNodes, pathNodes
            UNWIND coreNodes AS coreNode
            
            // Step 3: Extract all directional relationships touching these core nodes
            // We pass pathNodes through the MATCH scope implicitly by carrying it in the WITH
            MATCH (coreNode)-[r]->(neighbor:Node)
            
            // Step 4: Collect everything into a distinct semantic triple format
            WITH DISTINCT coreNode, r, neighbor, pathNodes
            RETURN 
                coreNode.name AS source_name,
                coreNode.topologyScore AS source_topo_score,
                type(r) AS relationship_type,
                neighbor.name AS target_name,
                neighbor.topologyScore AS target_topo_score,
                (coreNode IN pathNodes AND neighbor IN pathNodes) AS is_backbone_edge   
        """
        result = session.run(query, keyword_embedding=keyword_embedding, phrase_embedding=phrase_embedding)
        out_result = result.data()
    
    #print("Raw Result:", out_result)
    semantic_triples = []
    for record in out_result:
        semantic_triples.append({
            "source": {
                "name": record["source_name"],
                "topo_score": record["source_topo_score"],
                #"text": record["source_text"] if record["source_text"] else ""
            },
            "relationship": record["relationship_type"].replace("_", " ").lower(), # Clean up syntax like IS_DEFINED_AS to "is defined as"
            "target": {
                "name": record["target_name"],
                "topo_score": record["target_topo_score"],
                #"text": record["target_text"] if record["target_text"] else ""
            },
            "is_backbone": record["is_backbone_edge"]
        })
    

    
    sorted_triples = []
    unique_relationships = []

    for triple in semantic_triples:
        if triple["relationship"] not in unique_relationships:
            unique_relationships.append(triple["relationship"])
            sorted_triples.append([triple])
        else:
            index = unique_relationships.index(triple["relationship"])
            sorted_triples[index].append(triple)
    
    for group in sorted_triples:
        group.sort(key=lambda x: max(x["source"]["topo_score"], x["target"]["topo_score"]), reverse=True)
        length = len(group)
        if group[0]["/r/locatedNear"] or group[0]["/r/relatedTo"]:
            group = group[:max(1, length//2)]
        
    
    for group in sorted_triples:
        for triple in group:
            print(f"{triple['source']['name']} ({triple['source']['topo_score']}) --[{triple['relationship']}]-> {triple['target']['name']} ({triple['target']['topo_score']}) | Backbone: {triple['is_backbone']}")


    output = []
        
        


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

print(fetch_seed_node("peacock", "describe the properties of a peacock"))
