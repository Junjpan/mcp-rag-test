from typing import List, Dict, Any, Generator
import hashlib
import uuid

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from tqdm import tqdm
from qdrant_client import models, QdrantClient

# Helper function for batching,the batch size here refer to the array size, not the actually string length
def batch_generator(data: List[Any], batch_size: int) -> Generator[List[Any], None, None]:
    """Yields successive n-sized chunks from a list."""
    for i in range(0, len(data), batch_size):
        yield data[i : i + batch_size]

class FAQEngine:
    """
    An engine for setting up and querying a FAQ database using Qdrant and HuggingFace embeddings.
    """
    def __init__(self,
                 qdrant_url: str = "http://localhost:6333",
                 collection_name: str = "python-faq",
                 embed_model_name: str = "nomic-ai/nomic-embed-text-v1.5"): # this model is comingfrom nomic-ai, it is a good general purpose embedding model
        
        self.collection_name = collection_name
        
        # Initialize the embedding model
        print("Loading embedding model...")
        # HuggingFaceEmbedding  is a wrapping class like a loader, it doesn't provide model-it knows how to talk to Hugging Face Hub and download the model if not present locally
        # Only when you pretty sure the custom model is safe, set trust_remote_code=True, otherwise it can be a security risk
        self.embed_model = HuggingFaceEmbedding(
            model_name=embed_model_name,
            trust_remote_code=True,
            revision="e5cf08aadaa33385f5990def41f7a23405aec398" # <-- Pin to a specific commit revision to avoid future breaking changes, without this it will always get the latest version, using "main" is to get the latest version (can be unstable
        )
        
        # Dynamically get the vector dimension from the model
        self.vector_dim = len(self.embed_model.get_text_embedding("test"))
        print(f"Embedding model loaded. Vector dimension: {self.vector_dim}")

        # Initialize the Qdrant client
        self.client = QdrantClient(url=qdrant_url, prefer_grpc=True)
        print("Connected to Qdrant.")

    def setup_collection(self, faq_contexts: List[Dict], batch_size: int = 64):
        """
        Creates a Qdrant collection (if it doesn't exist) and ingests the FAQ data.
        """
        # Check if collection exists, create if not
        try:
            self.client.get_collection(collection_name=self.collection_name)
            print(f"Collection '{self.collection_name}' already exists. Skipping creation.")
        except Exception:
            print(f"Creating collection '{self.collection_name}'...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_dim,
                    distance=models.Distance.DOT
                ),
            )
        
        print("Updating collection indexing threshold...")
        # Set a indexing threshold for faster indexing during ingestion.
        self.client.update_collection(
            collection_name=self.collection_name,
            optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000)
        )

        print(f"Embedding and ingesting {len(faq_contexts)} documents...")
        points = []
        for batch in tqdm(batch_generator(faq_contexts, batch_size), total=(len(faq_contexts)//batch_size)+1, desc="Processing batches"):
            # Extract 'content' from each object in the batch
            contents = [entry["content"] for entry in batch]
            embeddings = self.embed_model.get_text_embedding_batch(contents, show_progress_bar=False)
            print(f"Generated {len(embeddings)} embeddings for current batch.")

            for entry, vector in zip(batch, embeddings):
                # Use a stable hash of the content as ID
                entry_id = entry.get("id") or hashlib.md5(entry["content"].encode("utf-8")).hexdigest()
                # entry_id = str(uuid.UUID(entry_id[:32]))  # Ensure it conforms to UUID format, otherwise Qdrant will create its own ID
                print(f"Processing entry ID: {entry_id}")
                # Use the rest of the entry as payload (excluding id)
                payload = {k: v for k, v in entry.items() if k != "id"}
                point = models.PointStruct(
                    id=entry_id,
                    vector=vector,
                    payload=payload
                )
                points.append(point)

        if points:
            self.client.upload_points(
                collection_name=self.collection_name,
                points=points,
                wait=False # Asynchronous upload for speed
            )

        print("Data ingestion complete.")


    def answer_question(self, query: str, top_k: int = 3) -> str:
        """
        Searches the vector database for a given query and returns the most relevant contexts.
        """
        # 1. Create an embedding for the user's query
        query_embedding = self.embed_model.get_query_embedding(query)

        # 2. Search Qdrant for the most similar vectors
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=0.5 # Optional: filter out less relevant results
        )

        # 3. Format the results into a single string
        if not search_result:
            return "I couldn't find a relevant answer in my knowledge base."

        relevant_contexts = [
            hit.payload["content"] for hit in search_result
        ]
        
        # Combine the contexts into a final, readable output
        formatted_output = "Here are the most relevant pieces of information I found:"+"\n\n---\n\n".join(relevant_contexts)
        return formatted_output#
    
