# AI_SEARCH_BOT_FAISS
A python application to help search with your documentations from `Confluence` and `Stack Overflow for Teams` with the power of AI.

This Project uses [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) with [Faiss](https://ai.meta.com/tools/faiss/) from Meta.

- `all-MiniLM-L6-v2` converts text into numerical vectors (embeddings).
- `FAISS` indexes and searches these embeddings efficiently, allowing fast semantic search in large datasets.

## Usage
### First Step
Create a `.env` file:

1. (required) STK_PAT [PAT for Stack Overflow Teams]
2. (required) TEAM_SLUG [Team Slug for Stack Overflow for Teams]
3. (required) CONFLUENCE_API_TOKEN [API TOKEN for Confluence]
4. (required) CONFLUENCE_URL [API URL for Confluence (e.g. "https://{your-company}.atlassian.net/wiki/rest/api/content")]
5. (required) CONFLUENCE_USERNAME [Username associated with the Token (e.g. "foo.bar@helloworld.com")]
6. (required) COMPANY_NAME [Input for {your-company} in `CONFLUENCE_URL` ]
7. (optional, defaults to 5) NUMBER_OF_QUERIES (Number of Answers returned)
8. (optional, defaults to -0.3) MAX_RELEVANCE_SCORE (Relevance Score in Search)
   
### Second Step
Create a `spaces.txt` with the names of the spaces you would like to add from Confluence.
E.g.:
```
foo
bar
hello
world
~69420
abunchofhooplas
```
If an invalid string exists, the script does not crash and continues.

### Third Step
Install the dependencies from `requirements.txt`, then run the script `platform-ai-searchbot.py` and see the magic! :D

NOTE: Make sure that the script, .env and spaces.txt file are all in the same folder!

I have also broken down the script for a fetch function and search function:

`fetch_data.py`: Fetches the data and stores them in a json-file.

`semantic_search.py`: Starts the search to give the User an answer from the json-file. This starts a while-loop which can be broken with `q` as a value passed or Keyboard-Interupt.

Both these files use the same Global Values as the `platform-ai-searchbot.py`, so nothing extra is required.
