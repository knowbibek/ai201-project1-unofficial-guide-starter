import os
from sentence_transformers import SentenceTransformer
import chromadb

# 1. Initialize our AI and Database tools
model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./chroma_db")

# Delete the collection if it exists so we start fresh each run, then create it
try:
    client.delete_collection(name="document_chunks")
except Exception:
    pass
collection = client.create_collection(name="document_chunks", metadata={"hnsw:space": "cosine"})

# 2. Process the text files into chunks and capture metadata
folder_path = "documents"
files = os.listdir(folder_path)

all_chunks = []
all_metadata = []

for filename in files:
    if filename.endswith('.txt'):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
            
            chunk_position = 0
            for i in range(0, len(text), 450):
                # Save the text
                chunk = text[i : i + 500]
                all_chunks.append(chunk)
                
                # Save the metadata (filename and position)
                all_metadata.append({"source": filename, "position": chunk_position})
                chunk_position += 1

# 3. Generate mathematical coordinates and unique IDs
embeddings = model.encode(all_chunks).tolist()
ids = [f"id_{i}" for i in range(len(all_chunks))]

# 4. Load everything into the vector database
collection.add(
    documents=all_chunks,
    embeddings=embeddings,
    metadatas=all_metadata,
    ids=ids
)
print(f"Successfully loaded {len(all_chunks)} chunks into ChromaDB!\n")


# ==========================================
# MILESTONE 4: RETRIEVAL TESTING
# ==========================================

# 5. Build the retrieval function
def retrieve_chunks(query, k=4):
    # Turn the user's text question into an embedding
    query_embedding = model.encode([query]).tolist()
    
    # Search the database for the closest matches
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k
    )
    return results

# 6. Test with 3 sample queries
test_queries = [
    "Where is a good place to study quietly?",
    "I want some good BBQ or smoked wings",
    "Where can I take my family out for dinner?"
]

for query in test_queries:
    print(f"--- QUERY: {query} ---")
    results = retrieve_chunks(query)
    
    # Extract the data from ChromaDB's output
    documents = results['documents'][0]
    distances = results['distances'][0]
    metadatas = results['metadatas'][0]
    
    # Loop through the top results and print them
    for i in range(len(documents)):
        print(f"Result {i+1} (Distance Score: {distances[i]:.4f})")
        print(f"Source: {metadatas[i]['source']} | Position: {metadatas[i]['position']}")
        print(f"Text: {documents[i]}\n")
    print("-" * 40 + "\n")