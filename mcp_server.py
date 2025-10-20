import os
from typing import List, Dict, Any
import requests

from dotenv import load_dotenv  # install python-dotenv
# from mcp.server.fastmcp import FastMCP  # install mcp-server
from fastmcp import FastMCP
from newRag import FAQEngine
from loader import load_allFiles

load_dotenv()

QDRANT_URL = "http://localhost:6333"
# Using a new collection for the Python data
COLLECTION_NAME = "python_faq_collection"
HOST = "127.0.0.1"
PORT = 8000

# create an MCP server instance
mcp_server = FastMCP('MCP-RAG-app', host=HOST, port=PORT)

# A docstring in Python is a string literal that occurs as the first statement in a module, function, class, or method definition. It serves as a form of documentation, providing a concise summary of the object's purpose and how to use it.


@mcp_server.tool()
def python_faq_retrieval_tool(query: str) -> str:
    """
    Retrieve the most relevant documents from the Python FAQ collection. 
    Use this tool when the user asks about general Python programming concepts.

    Args:
        query (str): The user query to retrieve the most relevant documents.

    Returns:
        str: The most relevant documents retrieved from the vector DB.
    """
    print("Received query for python_faq_retrieval_tool:", query)
    if not isinstance(query, str):
        raise TypeError("Query must be a string.")

    # Use the single, pre-initialized faq_engine instance for efficiency
    return faq_engine.answer_question(query)


@mcp_server.tool()
def firecrawl_web_search_tool(query: str) -> List[Dict[str, Any]]:
    """
    Search for information on a given topic using Firecrawl.
    Use this tool when the user asks a specific question not related to the Python FAQ.

    Args:
        query (str): The user query to search for information.

    Returns:
        List[Dict[str, Any]]: A list of the most relevant web search results. Each
        result is a mapping (dict) containing fields such as 'url', 'title', and
        'description'. Error cases are returned as a single-item list with an
        'error' field.
    """
    if not isinstance(query, str):
        raise TypeError("Query must be a string.")

    url = "https://api.firecrawl.dev/v1/search"
    api_key = os.getenv('FIRECRAWL_API_KEY')

    if not api_key:
        return [{"error": "FIRECRAWL_API_KEY environment variable is not set."}]

    payload = {"query": query, "timeout": 60000}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Prefer the 'data' key but fall back to other shapes.
        raw = response.json()
        data = None
        if isinstance(raw, dict):
            # common pattern: { "data": [...] }
            data = raw.get("data", raw.get("results", None))
        else:
            data = raw
        
        print("Firecrawl API response data:", data)

        # Normalize different response shapes into List[dict]
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            # Ensure each item is a dict; if not, wrap it.
            normalized: List[Dict[str, Any]] = []
            for item in data:
                if isinstance(item, dict):
                    normalized.append(item)
                else:
                    normalized.append({"result": item})
            return normalized

        # Fallback: wrap whatever we got as a single-item dict
        return [{"result": data}]
    except requests.exceptions.RequestException as e:
        return [{"error": f"Error connecting to Firecrawl API: {e}"}]


if __name__ == "__main__":
    # Initialize the FAQEngine once to avoid repeated setup
    faq_engine = FAQEngine(
        qdrant_url=QDRANT_URL,
        collection_name=COLLECTION_NAME
    )

    # Setup the collection and ingest data if not already done
    # faq_engine.setup_collection(FAQEngine.parse_faq(PYTHON_FAQ_TEXT)) // an example to deal  with raw text
    faq_contexts=load_allFiles("./knowledgebase")
    faq_engine.setup_collection(faq_contexts)

    # # Start the MCP server to listen for requests
    print(f"Starting MCP server at http://{HOST}:{PORT}")
    try:

        mcp_server.run('http')  # Starts server at http://localhost:8000/mcp
    except Exception as e:
        print(f"Server failed to start: {e}")
