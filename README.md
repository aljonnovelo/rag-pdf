Run the app in terminal

`uv run uvicorn main:app`

Run the Inngest development server

`npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery`

Run Docker for the Qdrant storage

`docker run -d --name qdrantRagDb -p 6333:6333 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant`
