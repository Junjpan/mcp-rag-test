Run Docker to interact with vector database:
## How batching and embeddings work in this project

When ingesting FAQ data into Qdrant:

- The FAQ text is split into a list of Q&A entries (each entry is a question and its answer).
- The data is processed in batches for efficiency. For example, if `batch_size=2`, the first batch will be `["Q1 A1", "Q2 A2"]`.
- For each batch, the embedding model generates a list of vectors (embeddings), one for each Q&A entry in the batch. For example, `[[v1_1, v1_2, ...], [v2_1, v2_2, ...]]`.
- Each Q&A entry and its corresponding embedding are paired using `zip(batch, embeddings)`, and a Qdrant point is created for each pair.
    - The `vector` (embedding) is a 1D array of floats representing the Q&A's meaning.
    - The `payload` contains the Q&A text (context).

**Summary:**
- Each Qdrant point = 1 Q&A entry + its embedding vector.
- Batching is just for efficiency; each entry is still stored and retrieved individually.

**Example:**
If `batch = ["Q1 A1", "Q2 A2"]`, then `embeddings = [[...], [...]]` and two points are created:
1. `{vector: embeddings[0], payload: {context: "Q1 A1"}}`
2. `{vector: embeddings[1], payload: {context: "Q2 A2"}}`

1. Run docker desktop and play the container that is related to this app
2. Run below command if you don't have a container that is already set up for this app.
For window bash
```
docker run -p 6333:6333 -p 6334:6334 \
    -v /$(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```
For mac or linux terminal, or if using Git Bash
```
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```
**Port 6333** → Qdrant’s main REST API endpoint. Human-readable JSON over HTTP.
***Go to Qdrant dashboard***
http://localhost:6333/dashboard
***Go to Qdrant collection***
http://localhost:6333/collections

**Port 6334** → Qdrant’s gRPC API endpoint. gRPC is a binary protocol from Google. Faster, more efficient than REST. You don't directly use it directly in a browser - instead, you connect to if from a client library (like Python, Node.js or Go).


Resources:
https://levelup.gitconnected.com/building-mcp-powered-agentic-rag-application-step-by-step-guide-1-2-efea9fb6f250

https://levelup.gitconnected.com/building-mcp-powered-agentic-rag-application-step-by-step-guide-2-2-2afd5254ab4e