from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle
from .summarizer import extract_text_from_pdf

# Initialize model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Small, fast & decent accuracy
VECTOR_DIM = 384

# Paths
INDEX_FILE = "faiss_index.index"
ID_MAP_FILE = "id_map.pkl"

# In-memory mappings
id_map = {}  # index -> paper_id
reverse_map = {}  # paper_id -> index

# FAISS index
index = faiss.IndexFlatL2(VECTOR_DIM)

# Load if exists
def load_index():
    global index, id_map, reverse_map
    if os.path.exists(INDEX_FILE):
        index = faiss.read_index(INDEX_FILE)
        if os.path.exists(ID_MAP_FILE):
            with open(ID_MAP_FILE, "rb") as f:
                id_map = pickle.load(f)
                reverse_map = {v: k for k, v in id_map.items()}

def save_index():
    faiss.write_index(index, INDEX_FILE)
    with open(ID_MAP_FILE, "wb") as f:
        pickle.dump(id_map, f)

def add_paper_vector(paper_id, text):
    # text = extract_text_from_pdf(filepath)
    global id_map, reverse_map

    if paper_id in reverse_map:
        print(f"[!] Paper {paper_id} already in index")
        return

    embedding = model.encode([text])[0]
    index.add(np.array([embedding]).astype("float32"))

    idx = len(id_map)
    id_map[idx] = paper_id
    reverse_map[paper_id] = idx
    save_index()
    print(f"[+] Added paper {paper_id} to FAISS")

def search_similar_papers(query, top_k=5):
    embedding = model.encode([query])[0]
    D, I = index.search(np.array([embedding]).astype("float32"), top_k)

    results = []
    for idx in I[0]:
        if idx in id_map:
            results.append(id_map[idx])
    return results

# Load existing on import
load_index()


