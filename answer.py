import master
import neo4j
import requests
from neo4j import GraphDatabase
import utilities as utils
import json
import listener
import ollama
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
            // Step 1: Locate nearest entry anchors using Vector Search
            MATCH (keywordAnchor:Node)
            SEARCH keywordAnchor IN (VECTOR INDEX cskg_concept_embeddings FOR $keyword_embedding LIMIT 1)

            MATCH (phraseAnchor:Node)
            SEARCH phraseAnchor IN (VECTOR INDEX cskg_concept_embeddings FOR $phrase_embedding LIMIT 1)

            // Ensure they aren't the exact same node; if they are, expand the search to find the next nearest neighbor
            WITH keywordAnchor, phraseAnchor
            // FIXED: Explicitly passing variables into the subquery scope to eliminate deprecation warning
            CALL (keywordAnchor, phraseAnchor) {
                // Branch A: Anchors collide. Fetch alternative 2nd nearest neighbor
                WITH keywordAnchor, phraseAnchor
                WHERE keywordAnchor = phraseAnchor
                MATCH (altPhraseAnchor:Node)
                SEARCH altPhraseAnchor IN (VECTOR INDEX cskg_concept_embeddings FOR $phrase_embedding LIMIT 2)
                WHERE altPhraseAnchor <> keywordAnchor
                RETURN altPhraseAnchor AS finalPhraseAnchor
                
                UNION
                
                // Branch B: Anchors are distinct. Use original phrase anchor
                WITH keywordAnchor, phraseAnchor
                WHERE keywordAnchor <> phraseAnchor
                RETURN phraseAnchor AS finalPhraseAnchor
            }
            WITH keywordAnchor, finalPhraseAnchor AS phraseAnchor

            // Step 2: Find the connecting backbone path
            MATCH path = shortestPath((keywordAnchor)-[*..4]-(phraseAnchor))
            WITH keywordAnchor, phraseAnchor, nodes(path) AS pathNodes

            // Create a unified pool of all core nodes
            WITH pathNodes + [keywordAnchor, phraseAnchor] AS coreNodes, pathNodes, [keywordAnchor, phraseAnchor] AS anchors
            UNWIND coreNodes AS coreNode
            WITH DISTINCT coreNode, pathNodes, anchors

            // Step 3 & 4: Extract relationships with conditional filtering via Subquery
            CALL (coreNode, anchors) {
                MATCH (coreNode)-[r]->(neighbor:Node)
                
                // If it's one of the two anchor nodes, return ALL neighbors
                WITH coreNode, r, neighbor, anchors
                WHERE coreNode IN anchors
                RETURN r, neighbor

                UNION

                // For the rest of the path nodes, return only top 3 by topologyScore
                MATCH (coreNode)-[r]->(neighbor:Node)
                WHERE NOT coreNode IN anchors
                WITH r, neighbor
                ORDER BY neighbor.topologyScore DESC
                LIMIT 3
                RETURN r, neighbor
            }

            // Step 5: Format and return results
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
    """
    for i in range(len(sorted_triples)):
        group = sorted_triples[i]
        group.sort(key=lambda x: max(x["source"]["topo_score"], x["target"]["topo_score"]), reverse=True)
        length = len(group)
        rel_type = group[0]["relationship"]       
        if ((rel_type=="/r/LocatedNear") or (rel_type == "/r/RelatedTo")):
            sorted_triples[i] = group[:max(1, length//2)]
    """     
        
    

    output = sorted_triples
    # Format output a little properly. or just format when passing into llm at last step. 
        
        
    # Now, we will look 

    # Using the search to give top one node directly. 
    return output if output else None



def answer(input_dict):
    question_type = input_dict.get("intent")
    if question_type == "question-general":
        # process general question
        # use key-word search for seeding. Then, explore 1 branch laterally upto 5 nodes. Then, explore 2 highest topology scoring neighbours from those 5 nodes. Then, use that information to answer the question.
        output_nodes = fetch_seed_node(input_dict.get("keyword"), input_dict.get("phrase"))
        response = ollama.chat(
            model="gemma3n:e4b",
            messages=[
                {
                    "role": "user",
                    "content": f"Establish semantic meaning from the data provided below. I do not care about the numbers, you are a natural language agent so speak normally and answer the question using data. Data: {output_nodes} Question: {input_dict.get("phrase")}"
                }
            ],
            keep_alive=0
        )
        text = response['message']['content']
        listener.talk(text)
        return None
    elif question_type == "question-specific":
        # process specific question
        pass
    elif question_type == "question-general-changing":
        # process general changing question
        pass
    pass


