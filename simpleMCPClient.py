import asyncio
import json
from fastmcp import Client

client = Client("http://localhost:8000/mcp")

async def call_tool(tool: str, args: dict):
    async with client:
        # list available tools for MCP server
        if hasattr(client, 'list_tools'):
            tools = await client.list_tools()
            tool_info=[{'name': tool.name, 'description': tool.description} for tool in tools]
        
        result = await client.call_tool(tool, args)
        print(f"Raw result type: {type(result)}")
        print(f"Raw result: {result}")
        # Show type for debugging

        # Helper to attempt to pretty-print a text/JSON payload
    
        def _print_payload_text(text: str):
            try:
                parsed = json.loads(text)
                print('result in json format',json.dumps(parsed, indent=2, ensure_ascii=False))
                return parsed
            except Exception:
                # Not JSON, print as-is
                # print(text)
                return text

        # 1) If it's a bytes object, decode it
        if isinstance(result, (bytes, bytearray)):
            try:
                result = result.decode("utf-8")
            except Exception:
                print(result)
                return result

        # 2) If it's an object with a .content attribute (e.g., CallToolResult), try to unwrap
        # normally the result is wrapped in CallToolResult object and has 3 most important attributes: content, structured_content, data
        # Data is a convenience attribute that gives you the deserialized Python object from the tool's structured output.
        # If your tool returns {"user_id": 123, "status": "active"}, then result.data will be a Python dict: {'user_id': 123, 'status': 'active'}.
        # If your tool returns ["item1", "item2"], then result.data will be a Python list: ['item1', 'item2'].
        # If your tool returns just a string "Success", then result.data will be the Python str: 'Success'.
        # 2. content (For the LLM)
        # This is a list of content blocks. This is the "traditional" output meant to be read by the Language Model. It can contain text, images, or other rich media. In your specific example from the previous question, this list contained one TextContent block, and its text attribute held the raw JSON string.
        # 3. structured_content (The Raw Data)
        # This is the raw, machine-readable JSON object (as a Python dict) that the tool returned. The data attribute is simply the client's deserialized version of what's in structured_content.
        

        if hasattr(result, "content"):
            # print('result',result)
            # when it return the result, it usually has content, structured_content and data attributes
            content = getattr(result, "content")
            structured_content = getattr(result, "structured_content", None)
            data=getattr(result, "data", None)

            # print('data',data)
            # print('structured_content',structured_content)
            # If content is a list (e.g., [TextContent,...])
            if isinstance(content, (list, tuple)) and len(content) > 0:
                parts = []
                for item in content:
                    if hasattr(item, "text"):
                        parts.append(getattr(item, "text"))
                    elif isinstance(item, str):
                        parts.append(item)
                    else:
                        # Fallback to str()
                        parts.append(str(item))
                joined = "\n".join(parts)
                return _print_payload_text(joined)

            # If content is a single string/dict
            if isinstance(content, str):
                return _print_payload_text(content)
            if isinstance(content, (dict, list)):
                try:
                    print(json.dumps(content, indent=2, ensure_ascii=False))
                except Exception:
                    print(content)
                return content

            # If nothing matched, fall back to printing the repr
            print(content)
            return content

        # 3) If it has a .text attribute directly (some wrappers), use that
        if hasattr(result, "text") and isinstance(getattr(result, "text"), str):
            return _print_payload_text(getattr(result, "text"))

        # 4) If it's a plain string
        if isinstance(result, str):
            print('testing')
            return _print_payload_text(result)

        # 5) If it's already a Python mapping / sequence, pretty-print it
        if isinstance(result, dict) or isinstance(result, list):
            # If it's a list of dicts (e.g., web search results), pretty-print as JSON
            try:
                pretty = json.dumps(result, indent=2, ensure_ascii=False)
                print(pretty)
                # Many validators expect a string payload; return the JSON string
                return pretty
            except Exception:
                print(result)
                return result

        return result

if __name__ == "__main__":
    toolName = input("Press Enter to call tool name, add, greet,rag or firecrawl: ")
    try:
        toolName = toolName.strip()
        if toolName == "add":
            a = int(input("Enter a: "))
            b = int(input("Enter b: "))
            asyncio.run(call_tool("add", {"a": a, "b": b}))
        elif toolName == "greet":
            name = input("Enter name: ")
            asyncio.run(call_tool("greet", {"name": name}))
        elif toolName == "rag":
            query = input("Enter your Python FAQ question: ")
            asyncio.run(call_tool("python_faq_retrieval_tool", {"query": query}))
        elif toolName == "firecrawl":
            query = input("Enter your web search query: ")
            asyncio.run(call_tool("firecrawl_web_search_tool", {"query": query}))
        else:
            print("Unknown tool name")
    except Exception as e:
        print("Error:", e)