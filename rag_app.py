import uuid
from itertools import islice
from typing import List, Dict, Any, Generator
import hashlib

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from tqdm import tqdm
from qdrant_client import models, QdrantClient


PYTHON_FAQ_TEXT = """
Question: What is the difference between a list and a tuple in Python?
Answer: Lists are mutable, meaning their elements can be changed, while tuples are immutable. Lists use square brackets `[]` and tuples use parentheses `()`.

Question: What are Python decorators?
Answer: Decorators are a design pattern in Python that allows a user to add new functionality to an existing object without modifying its structure. They are often used for logging, timing, and access control.

Question: How does Python's Global Interpreter Lock (GIL) work?
Answer: The GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecode at the same time. This means that even on a multi-core processor, only one thread can execute Python code at once.

Question: What is the difference between `==` and `is` in Python?
Answer: `==` checks for equality of value (do two objects have the same content?), while `is` checks for identity (do two variables point to the same object in memory?).


Question: Explain list comprehensions and their benefits.
Answer: List comprehensions provide a concise way to create lists. They are often more readable and faster than using traditional `for` loops and `.append()` calls.

Question: What is `*args` and `**kwargs` in function definitions?
Answer: `*args` allows you to pass a variable number of non-keyword arguments to a function, which are received as a tuple. `**kwargs` allows you to pass a variable number of keyword arguments, received as a dictionary.

Question: What are Python's magic methods (e.g., `__init__`, `__str__`)?
Answer: Magic methods, or dunder methods, are special methods that you can define to add "magic" to your classes. They are invoked by Python for built-in operations, like `__init__` for object creation or `__add__` for the `+` operator.

Question: How does error handling work in Python?
Answer: Python uses `try...except` blocks to handle exceptions. Code that might raise an error is placed in the `try` block, and the code to handle the exception is placed in the `except` block.

Question: What is the purpose of the `if __name__ == "__main__":` block?
Answer: This block ensures that the code inside it only runs when the script is executed directly, not when it is imported as a module into another script.

Question: What are generators in Python?
Answer: Generators are a simple way to create iterators. They are functions that use the `yield` keyword to return a sequence of values one at a time, saving memory for large datasets.
"""

# Helper function for batching,the batch size here refer to the array size, not the actually string length
def batch_generator(data: List[Any], batch_size: int) -> Generator[List[Any], None, None]:
    """Yields successive n-sized chunks from a list."""
    for i in range(0, len(data), batch_size):
        yield data[i : i + batch_size]

def hash_content(content: str) -> str:
    """create a stable id based on the content"""
    # return hashlib.sha256(content.encode("utf-8")).hexdigest() #it doesn't work for Qdrant id, because it's too long
    return hashlib.md5(content.encode("utf-8")).hexdigest() #MD5 is faster but less secure; SHA-256 is more robust against collisions, but in Qdrant the id length is limited

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

    @staticmethod
    def parse_faq(text: str) -> List[str]:
        """Parses the raw FAQ text into a list of Q&A strings."""
        return [
            qa.replace("\n", " ").strip()
            for qa in text.strip().split("\n\n")
        ]
    
    @staticmethod
    def extract_question(qa_text: str) -> str:
        """
        Extracts the question part from a QA string.
        Assumes the format: "Question: ... Answer: ..."
        """
        if qa_text.startswith("Question:"):
            try:
                return qa_text.split("Answer:")[0].replace("Question:", "").strip()
            except IndexError:
                return qa_text  # fallback to the whole text
        return qa_text

    def setup_collection(self, faq_contexts: List[str], batch_size: int = 64):
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
        self.client.update_collection(
            collection_name=self.collection_name,
            optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000)
        )

        print(f"Embedding and ingesting {len(faq_contexts)} documents...")
        points = []
        for batch in tqdm(batch_generator(faq_contexts, batch_size),total=(len(faq_contexts)//batch_size)+1,desc="Processing batches"): 
            #batch is a list of strings
            embeddings = self.embed_model.get_text_embedding_batch(batch, show_progress_bar=False) #returns a list of vectors like [[0.1,0.2,...],[0.2,0.3,...],...]
            for context, vector in zip(batch, embeddings):
                question = self.extract_question(context)
                point = models.PointStruct(
                    id=hash_content(question), # Use stable hash of content as ID
                    vector=vector,
                    payload={"context": context,"question": question} # Store both question and full context in payload for richer responses
                )
                points.append(point)

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
            hit.payload["context"] for hit in search_result
        ]
        
        # Combine the contexts into a final, readable output
        formatted_output = "Here are the most relevant pieces of information I found:"+"\n\n---\n\n".join(relevant_contexts)
        return formatted_output
    



#todo: Think about how to handle if the faq is already in the db, and how we want to handle updates efficiently
# 1.instead of using uuid, we could use a hash of the content as the id, so if the content changes, we update the vector instaed of adding a new one
#2. Instead put the knowledge base in a single string, experience it import them with different files
#3. Can I run it in a docker container with qdrant and the model? , if so how to do it efficiently?





