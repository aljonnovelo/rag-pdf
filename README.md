# Sample Usage
- Upload the files that you want to use.

<img src="docs/Screenshot%20%2825%29.png" width="75%">

- Type your question 
- Indicate the number of chunks (number of relevant sections of the documents to be used to answer the question)
- Click "Ask"

<img src="docs/Screenshot%20%2826%29.png" width="75%">
<img src="docs/Screenshot%20%2827%29.png" width="75%">

# Development Setup

1. Run the app in terminal.

`uv run uvicorn main:app`

2. On a separate terminal, run the Inngest development server.

`npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery`

3. Setup the docker container for the Qdrant storage.

`docker run -d --name qdrantRagDb -p 6333:6333 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant`

4. On a separate terminal, run the frontend.

`uv run streamlit run .\streamlit_app.py`
