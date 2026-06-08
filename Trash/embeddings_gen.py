from neo4j import GraphDatabase
import ollama
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import sys
import time

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")
DATABASE_NAME = "cskg"
MODEL_NAME = "all-minilm"
TOTAL_NODES = 22_000_000
DEFAULT_UPDATE_INTERVAL = 1.0

# TUNING PARAMETERS
BATCH_SIZE = 200       # How many nodes to fetch from Neo4j at once
CONCURRENT_WORKERS = 10  # Number of parallel threads hitting Ollama. Adjust based on your CPU/GPU cores.

def format_duration(seconds):
    seconds = int(seconds)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def display_progress(total_indexed, start_time):
    elapsed = time.time() - start_time
    rate = total_indexed / max(elapsed, 1e-6)
    remaining = max(TOTAL_NODES - total_indexed, 0)
    eta = remaining / max(rate, 1e-6)
    percent = min(total_indexed / TOTAL_NODES * 100, 100.0)
    status = (
        f"Processed {total_indexed}/{TOTAL_NODES} nodes ({percent:.2f}%), "
        f"elapsed {format_duration(elapsed)}, eta {format_duration(eta)}, "
        f"{rate:,.2f} nodes/s"
    )
    sys.stdout.write("\r" + status + "   ")
    sys.stdout.flush()

def get_embedding(item):
    """Worker function to fetch embedding for a single text item."""
    try:
        response = ollama.embeddings(model=MODEL_NAME, prompt=item['text'])
        return {"node_id": item['node_id'], "vector": response['embedding']}
    except Exception as e:
        # Return None if it fails so it doesn't crash the whole batch
        print(f"⚠️ Error getting embedding for text: {e}")
        return None

def update_embeddings(update_interval=DEFAULT_UPDATE_INTERVAL):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        
        # Optimized query using an index hint (ensure you created the index first!)
        query_fetch = f"""
        MATCH (n:Node) 
        WHERE n.embedding IS NULL AND n.name IS NOT NULL
        LIMIT {BATCH_SIZE} 
        RETURN elementId(n) AS node_id, n.name AS text
        """
        
        query_update = """
        UNWIND $batch AS item
        MATCH (n) WHERE elementId(n) = item.node_id
        SET n.embedding = item.vector
        """
        
        with driver.session(database=DATABASE_NAME) as session:
            total_indexed = 0
            start_time = time.time()
            last_status = start_time - update_interval
            
            while True:
                result = session.run(query_fetch)
                records = [dict(r) for r in result]
                
                if not records:
                    sys.stdout.write("\n")
                    print("🎉 All 22 Million nodes successfully processed!")
                    display_progress(total_indexed, start_time)
                    print("\n")
                    break
                
                batch_data = []
                
                # Multi-threading Ollama requests
                with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
                    futures = {executor.submit(get_embedding, record): record for record in records}
                    
                    for future in as_completed(futures):
                        res = future.result()
                        if res is not None:
                            batch_data.append(res)
                
                if batch_data:
                    session.run(query_update, batch=batch_data)
                    total_indexed += len(batch_data)
                else:
                    print("\n⚠️ No valid embeddings retrieved in this batch. Retrying...")
                
                now = time.time()
                if now - last_status >= update_interval:
                    display_progress(total_indexed, start_time)
                    last_status = now

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Neo4j embedding updater with live progress reporting.")
    parser.add_argument("--time", type=float, default=DEFAULT_UPDATE_INTERVAL,
                        help="Seconds between live progress updates (default: 5)")
    args = parser.parse_args()

    print("🔥 Starting High-Performance Vector Embedding Pipeline 🔥")
    update_embeddings(update_interval=args.time)