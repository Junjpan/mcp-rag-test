from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    mcp.run('http')  # Starts server at http://localhost:8000/mcp
