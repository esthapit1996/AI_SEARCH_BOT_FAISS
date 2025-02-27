import requests
import base64
from sentence_transformers import SentenceTransformer
import faiss
import time
from dotenv import load_dotenv
import os
# import numpy as np

load_dotenv() 

# Confluence details
CONFLUENCE_URL = os.environ.get("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.environ.get("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.environ.get("CONFLUENCE_API_TOKEN")
# Stack Overflow for Teams details
STK_PAT = os.environ.get("STK_PAT")
TEAM_SLUG = "onefootball"

# Check for Tokens
if not CONFLUENCE_API_TOKEN:
    print("Please set the CONFLUENCE_API_TOKEN environment variable.")
    exit()
if not STK_PAT:
    print("Please set the STK_PAT(Token for Stack Overflow for Teams) environment variable.")
    exit()

# Rest Vars
NUMBER_OF_QUERIES = int(os.environ.get("NUMBER_OF_QUERIES", 5)) #set default value to 5
AI_MODEL='all-MiniLM-L6-v2'
MAX_RELEVANCE_SCORE = float(os.environ.get("MAX_RELEVANCE_SCORE", -0.3)) #set default value to -0.3

# Encode credentials
auth_header = base64.b64encode(f"{CONFLUENCE_USERNAME}:{CONFLUENCE_API_TOKEN}".encode()).decode()

# Set up request headers
headers = {
    "Authorization": f"Basic {auth_header}",
    "Accept": "application/json"
}

def fetch_confluence_pages(space_key=None):
    confluence_data = []
    start = 0
    limit = 1000 # Maximum limit allowed by Confluence API
    total_results = None # To keep track of the total number of pages
    
    space_param = f"&spaceKey={space_key}" if space_key else ""

    while total_results is None or start < total_results:
        response = requests.get(
            f"{CONFLUENCE_URL}?start={start}&limit={limit}{space_param}",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            pages = data.get("results", [])
            total_results = data.get("size", 0)  # Total available pages count

            for page in pages:
                title = page.get("title", "")
                body = page.get("body", {}).get("storage", {}).get("value", "")
                link = f"https://onefootball.atlassian.net/wiki{page.get('_links', {}).get('webui', '')}"

                confluence_data.append({
                    "title": title,
                    "body": body,
                    "link": link
                })

            start += len(pages)
            print(f"Fetched {len(confluence_data)} pages... Getting more...")  # Progress logging
        else:
            print(f"Error fetching Confluence pages: {response.status_code}")
            break

    return confluence_data

def fetch_stackoverflow_teams():
    headers = {
        "X-API-Access-Token": STK_PAT
    }
    
    all_questions = []
    page = 1
    has_more = True

    while has_more:
        params = {
            "order": "desc",
            "sort": "activity",
            "filter": "withbody",
            "site": "stackoverflow",
            "team": TEAM_SLUG,
            "page": page,
            "pagesize": 100  # Maximum allowed pagesize
        }

        url = "https://api.stackoverflowteams.com/2.3/questions"
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            questions = data.get('items', [])
            all_questions.extend(questions)
            
            has_more = data.get('has_more', False)
            page += 1
            
            # Respect API rate limits
            if has_more:
                time.sleep(1)  # Wait for 1 second between requests
        else:
            print(f"Error fetching data: {response.status_code}")
            break

    return all_questions

class SemanticSearch:
    def __init__(self, model_name=AI_MODEL):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.questions = []
        self.embeddings = None

    def add_data(self, documents):
        self.data = documents
        texts = [d['title'] + ' ' + d['body'] for d in documents]
        self.embeddings = self.model.encode(texts)
        self.create_index()

    def create_index(self):
        if self.embeddings is None or len(self.embeddings) == 0:
            print("No embeddings found. Ensure data is loaded correctly.")
            return
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))

    def search(self, query, k=NUMBER_OF_QUERIES):
        if self.index is None or self.index.ntotal == 0:
            print("Error: FAISS index is empty. Please check data loading.")
            return []
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(query_vector.astype('float32'), k)
        results = [(self.data[idx], distances[0][i]) for i, idx in enumerate(indices[0])]
        return results
    
def main():
    # Fetch Stack Overflow questions
    print("Fetching questions from Stack Overflow for Teams...")
    questions = fetch_stackoverflow_teams()
    if len(questions) == 0:
        print("No questions found./ Failed to fetch questions.")
    else:
        print(f"Fetched {len(questions)} questions.\n")
    
    # Fetch Confluence pages
    print("Fetching Confluence pages...")
    confluence_pages = []
    with open("spaces.txt", "r") as f:
        spaces = {line.strip() for line in f}
        print(spaces) 
    
    for space in spaces:
        confluence_pages += fetch_confluence_pages(space_key=space)

    if len(confluence_pages) == 0:
        print("No pages found. Failed to fetch Confluence pages.")
    else:
        print(f"Fetched {len(confluence_pages)} pages.\n")
    
    print("Initializing semantic search...")
    searcher = SemanticSearch()
    
    # Combine data from Confluence and Stack Overflow
    combined_data = questions + confluence_pages
    
    searcher.add_data(combined_data)
    print(f"Semantic Search Initialized with {len(combined_data)} documents.")
    
    relevance_max = MAX_RELEVANCE_SCORE

    while True:
        query = input("\nPlease type your question or quit using 'q': ")
        if query.lower() == 'q':
            print("\nOff to the next adventure! Gotta catch 'em all!\n")
            break

        print(f"\nSearching for: '{query}'")
        results = searcher.search(query, k=NUMBER_OF_QUERIES)

        if results:
            relevance_score = 1 - results[0][1]
                
            if relevance_score >= relevance_max:
                print(f"\nHere are the top {NUMBER_OF_QUERIES} relevant questions:\n")

            else:
                print("No relevant results found in Confluence and Stackoverflow Teams.\n")
                        
            for best_match, distance in results:
                if relevance_score >= relevance_max:
                    print("-" * (len(best_match['link'])+6))
                    print(f"Title: {best_match['title']}")
                    print(f"Link: {best_match['link']}")
                    print(f"Relevance score: {1 - distance:.4f}")
                    print("-" * (len(best_match['link'])+6))

                else:
                    break
        else:
            print("No relevant results found in Confluence and Stack Overflow Teams.")

if __name__ == "__main__":
    main()
