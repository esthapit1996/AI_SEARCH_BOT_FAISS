import requests
import base64
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Confluence details
CONFLUENCE_URL = os.environ.get("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.environ.get("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.environ.get("CONFLUENCE_API_TOKEN")

# Stack Overflow for Teams details
STK_PAT = os.environ.get("STK_PAT")
TEAM_SLUG = "onefootball"

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
    limit = 1000
    total_results = None
    
    space_param = f"&spaceKey={space_key}" if space_key else ""

    while total_results is None or start < total_results:
        response = requests.get(
            f"{CONFLUENCE_URL}?start={start}&limit={limit}{space_param}",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            pages = data.get("results", [])
            total_results = data.get("size", 0)

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
            print(f"Fetched {len(confluence_data)} pages... Getting more...")
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
            "pagesize": 100
        }

        url = "https://api.stackoverflowteams.com/2.3/questions"
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            questions = data.get('items', [])
            all_questions.extend(questions)
            
            has_more = data.get('has_more', False)
            page += 1
            
            time.sleep(1)
        else:
            print(f"Error fetching Stack Overflow questions: {response.status_code}")
            break

    return all_questions

def save_data(data, filename="data.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")

def main():
    print("Fetching Stack Overflow questions...")
    questions = fetch_stackoverflow_teams()
    
    print("Fetching Confluence pages...")
    confluence_pages = []
    with open("spaces.txt", "r") as f:
        spaces = {line.strip() for line in f}
    
    for space in spaces:
        confluence_pages += fetch_confluence_pages(space_key=space)

    combined_data = questions + confluence_pages
    save_data(combined_data)

if __name__ == "__main__":
    main()
