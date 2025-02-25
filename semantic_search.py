import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Constants
NUMBER_OF_QUERIES = 5
AI_MODEL = "all-MiniLM-L6-v2"
MAX_RELEVANCE_SCORE = -0.3
DATA_FILE = "data.json"

class SemanticSearch:
    def __init__(self, model_name=AI_MODEL):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.data = []
        self.embeddings = None

    def load_data(self, filename=DATA_FILE):
        try:
            with open(filename, "r") as f:
                self.data = json.load(f)
            print(f"Loaded {len(self.data)} documents.")
            self.add_data()
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
            exit()

    def add_data(self):
        texts = [d["title"] + " " + d["body"] for d in self.data]
        self.embeddings = self.model.encode(texts)
        self.create_index()

    def create_index(self):
        if self.embeddings is None or len(self.embeddings) == 0:
            print("No embeddings found. Ensure data is loaded correctly.")
            return
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(self.embeddings, dtype="float32"))

    def search(self, query, k=NUMBER_OF_QUERIES):
        if self.index is None or self.index.ntotal == 0:
            print("Error: FAISS index is empty. Please check data loading.")
            return []
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector, dtype="float32"), k)
        results = [(self.data[idx], distances[0][i]) for i, idx in enumerate(indices[0])]
        return results

def main():
    print("Initializing semantic search...")
    searcher = SemanticSearch()
    searcher.load_data()
    
    while True:
        query = input("\nPlease type your question or quit using 'q': ")
        if query.lower() == "q":
            print("\nOff to the next adventure! Gotta catch 'em all!\n")
            break

        print(f"\nSearching for: '{query}'")
        results = searcher.search(query, k=NUMBER_OF_QUERIES)

        if results:
            relevance_score = 1 - results[0][1]

            if relevance_score >= MAX_RELEVANCE_SCORE:
                print(f"\nHere are the top {NUMBER_OF_QUERIES} relevant results:\n")

                for best_match, distance in results:
                    print("-" * (len(best_match["link"]) + 6))
                    print(f"Title: {best_match['title']}")
                    print(f"Link: {best_match['link']}")
                    print(f"Relevance score: {1 - distance:.4f}")
                    print("-" * (len(best_match["link"]) + 6))
            else:
                print("No relevant results found.\n")
        else:
            print("No relevant results found.")

if __name__ == "__main__":
    main()
