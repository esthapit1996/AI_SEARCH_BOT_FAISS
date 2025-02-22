# AI_SEARCH_BOT_FAISS
A python application to help search with your documentations with the power of AI.

This Project uses [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) with [Faiss](https://ai.meta.com/tools/faiss/) from Meta.

- `all-MiniLM-L6-v2` converts text into numerical vectors (embeddings).
- `FAISS` indexes and searches these embeddings efficiently, allowing fast semantic search in large datasets.

## Usage
***First***, create a `.env` file:

1. STK_PAT [PAT for Stack Overflow Teams]
2. CONFLUENCE_API_TOKEN [API TOKEN for Confluence]
3. CONFLUENCE_URL [API URL for Confluence (e.g. "https://{your-company}.atlassian.net/wiki/rest/api/content")]
4. CONFLUENCE_USERNAME [Username associated with the Token (e.g. "foo.bar@helloworld.com")]
   
***Second***, create a `spaces.txt` file.
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

***Third***, Install the dependencies from `requirements.txt`, then run the script `platform-ai-searchbot.py` and see the magic! :D

NOTE: Make sure that the script, .env and spaces.txt file are all in the same folder!