import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
import gradio as gr

# Load environment variables from your local .env file
load_dotenv()

# ==========================================
# 1. INITIALIZE AI MODELS & VECTOR DATABASE
# ==========================================
print("Initializing embedding model and vector database...")
model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./chroma_db")

# Delete the collection if it exists so we start fresh and avoid duplicate data
try:
    client.delete_collection(name="document_chunks")
except Exception:
    pass

# Create the collection using cosine distance for accurate scoring
collection = client.create_collection(
    name="document_chunks", 
    metadata={"hnsw:space": "cosine"}
)

# Initialize the Groq client using your API key
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ==========================================
# 2. INGESTION & CHUNKING PIPELINE
# ==========================================
folder_path = "documents"
all_chunks = []
all_metadata = []

if os.path.exists(folder_path):
    files = os.listdir(folder_path)
    print(f"Reading and chunking files from ./{folder_path}...")
    for filename in files:
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
                
                chunk_position = 0
                for i in range(0, len(text), 450):
                    chunk = text[i : i + 500]
                    all_chunks.append(chunk)
                    
                    # Store source metadata for programmatically guaranteed attribution
                    all_metadata.append({
                        "source": filename, 
                        "position": chunk_position
                    })
                    chunk_position += 1

    # Load everything into ChromaDB
    if all_chunks:
        embeddings = model.encode(all_chunks).tolist()
        ids = [f"id_{i}" for i in range(len(all_chunks))]
        collection.add(
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=all_metadata,
            ids=ids
        )
        print(f"Successfully loaded {len(all_chunks)} chunks into ChromaDB!\n")
else:
    print(f"Warning: '{folder_path}' directory not found. Starting with an empty database.")

# ==========================================
# 3. RETRIEVAL & GROUNDED GENERATION LOGIC
# ==========================================
def ask_rag_system(question):
    """
    Retrieves the top 4 relevant chunks from ChromaDB, builds a context block,
    and prompts Groq with strict grounding rules to eliminate hallucinations.
    """
    # 1. Retrieve top 4 matches from the vector database
    query_embedding = model.encode([question]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=4)
    
    retrieved_docs = results['documents'][0] if results['documents'] else []
    retrieved_metadatas = Antiquated_meta = results['metadatas'][0] if results['metadatas'] else []
    
    if not retrieved_docs:
        return "I do not have any documents loaded to answer this question.", []
    
    # 2. Build a single text block for the context and track unique sources
    context_block = ""
    unique_sources = set()
    for idx, doc in enumerate(retrieved_docs):
        meta = retrieved_metadatas[idx]
        context_block += f"--- Source: {meta['source']} (Position: {meta['position']}) ---\n{doc}\n\n"
        unique_sources.add(f"{meta['source']} (Position {meta['position']})")
        
    # 3. Define the strict grounding rules required by the assignment milestone
    system_prompt = (
        "You are a factual, strictly grounded assistant. Answer the user's question using ONLY the provided "
        "document context below. Do not use your own general external knowledge, assumptions, or extrapolation. "
        "If the provided documents do not contain enough specific facts to fully answer the question, "
        "you must respond EXACTLY with: 'I don't have enough information on that.'\n\n"
        f"--- PROVIDED DOCUMENT CONTEXT ---\n{context_block}"
    )
    
    # 4. Request generation from Llama 3 on Groq
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.0  # Set temperature to 0.0 to keep the model completely deterministic
        )
        answer = completion.choices[0].message.content
    except Exception as e:
        answer = f"Error communicating with Groq API: {str(e)}"
        
    return answer, sorted(list(unique_sources))

# ==========================================
# 4. GRADIO GRAPHICAL WEB INTERFACE
# ==========================================
def handle_interface_query(question):
    if not question.strip():
        return "Please type a question before submitting.", ""
    
    answer, sources = ask_rag_system(question)
    
    # Format the sources as a clear bulleted list
    formatted_sources = "\n".join(f"• {s}" for s in sources) if sources else "None"
    return answer, formatted_sources

# Construct Layout via Gradio Blocks
with gr.Blocks(title="Local Document RAG Explorer") as demo:
    gr.Markdown("# 🤖 Local Document RAG Explorer")
    gr.Markdown("Ask questions based on your text files. The AI is structurally grounded to prevent general knowledge leaks.")
    
    with gr.Row():
        inp = gr.Textbox(label="Your Question", placeholder="Type your query here...", scale=4)
        btn = gr.Button("Ask AI", variant="primary", scale=1)
        
    answer_box = gr.Textbox(label="Answer", lines=8, interactive=False)
    sources_box = gr.Textbox(label="Retrieved From (Source Attribution)", lines=4, interactive=False)
    
    # Bind interface triggers (both click actions and hitting Enter key)
    btn.click(handle_interface_query, inputs=inp, outputs=[answer_box, sources_box])
    inp.submit(handle_interface_query, inputs=inp, outputs=[answer_box, sources_box])

if __name__ == "__main__":
    # Launch the local web server
    demo.launch()