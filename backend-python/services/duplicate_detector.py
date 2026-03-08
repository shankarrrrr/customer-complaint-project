from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# FAISS index path
INDEX_PATH = "faiss_index.bin"
EMBEDDINGS_PATH = "embeddings.pkl"

class DuplicateDetector:
    def __init__(self):
        self.dimension = 384  # all-MiniLM-L6-v2 embedding dimension
        self.index = None
        self.complaint_ids = []
        self.load_or_create_index()
    
    def load_or_create_index(self):
        """Load existing FAISS index or create new one"""
        if os.path.exists(INDEX_PATH) and os.path.exists(EMBEDDINGS_PATH):
            try:
                self.index = faiss.read_index(INDEX_PATH)
                with open(EMBEDDINGS_PATH, 'rb') as f:
                    self.complaint_ids = pickle.load(f)
                print(f"✅ Loaded FAISS index with {len(self.complaint_ids)} complaints")
            except Exception as e:
                print(f"Error loading index: {e}")
                self.create_new_index()
        else:
            self.create_new_index()
    
    def create_new_index(self):
        """Create new FAISS index"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.complaint_ids = []
        print("✅ Created new FAISS index")
    
    def add_complaint(self, complaint_id: int, text: str):
        """Add complaint to FAISS index"""
        try:
            embedding = model.encode([text])[0]
            embedding = np.array([embedding]).astype('float32')
            self.index.add(embedding)
            self.complaint_ids.append(complaint_id)
            self.save_index()
        except Exception as e:
            print(f"Error adding complaint to index: {e}")
    
    def find_duplicates(self, text: str, threshold: float = 0.85, top_k: int = 5) -> list:
        """
        Find similar complaints using cosine similarity
        Returns list of (complaint_id, similarity_score) tuples
        """
        if self.index.ntotal == 0:
            return []
        
        try:
            # Generate embedding for query text
            query_embedding = model.encode([text])[0]
            query_embedding = np.array([query_embedding]).astype('float32')
            
            # Search in FAISS index
            k = min(top_k, self.index.ntotal)
            distances, indices = self.index.search(query_embedding, k)
            
            # Convert L2 distance to cosine similarity
            # For normalized vectors: cosine_sim = 1 - (L2_distance^2 / 2)
            similarities = 1 - (distances[0] / 2)
            
            # Filter by threshold
            results = []
            for idx, sim in zip(indices[0], similarities):
                if sim >= threshold and idx < len(self.complaint_ids):
                    results.append({
                        "complaint_id": self.complaint_ids[idx],
                        "similarity": float(sim)
                    })
            
            return results
            
        except Exception as e:
            print(f"Error finding duplicates: {e}")
            return []
    
    def save_index(self):
        """Save FAISS index and complaint IDs to disk"""
        try:
            faiss.write_index(self.index, INDEX_PATH)
            with open(EMBEDDINGS_PATH, 'wb') as f:
                pickle.dump(self.complaint_ids, f)
        except Exception as e:
            print(f"Error saving index: {e}")

# Global instance
duplicate_detector = DuplicateDetector()
