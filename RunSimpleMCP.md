## Running the simple MCP server and client

This document explains how to run the example `simpleMCPserver.py` and `simpleMCPClient.py` in this repository. The server exposes two small example tools (`greet` and `add`) via an HTTP MCP endpoint, and the client demonstrates how to call those tools.

Contents

- Prerequisites
- Create and activate a virtual environment
- Install dependencies
- Start the server (HTTP)
- Run the client (call `greet` and `add`)
- Troubleshooting & verification

## Prerequisites

- Python 3.10+ (the environment in this repo uses many recent packages; 3.10+ is recommended)
- git (optional)
- A terminal (bash on Windows is fine - e.g., Git Bash or WSL)

Files of interest

- `simpleMCPserver.py` — defines a `FastMCP` server with two tools: `greet(name: str)` and `add(a: int, b: int)` and starts an HTTP server at `/mcp`.
- `simpleMCPClient.py` — example async client using `fastmcp.Client` to call tools on the server.
 - `simpleMCPClient.py` — example async client using `fastmcp.Client` to call tools on the server.
	 Purpose: an interactive, developer-focused example client for debugging and
	 testing your MCP server. It lists available tools, allows you to call them
	 manually (greet, add, RAG, firecrawl), and prints the tool's returned
	 `content`, `structured_content`, and `data` fields so you can inspect what
	 the server (and ultimately the LLM) will receive. You do not need to run
	 this client if you connect an external app (like Cursor) to the MCP server;
	 the client is mainly useful for local testing and troubleshooting.

## 1) Create and activate a virtual environment

In your project directory (where these files live), run these commands in bash. They create and activate a venv named `.venv` and upgrade pip.

```bash
python -m venv .venv
source venv/bin/activate   # macOS/Linux
source venv/Scripts/activate    # Windows
python -m pip install --upgrade pip
```

## 2) Install dependencies

This repository includes a `requirements.txt` that lists the packages used. Install them with:

```bash
pip install -r requirements.txt
```

If you prefer to install only what's needed for the simple example, at minimum install the MCP package and an ASGI server:

```bash
pip install mcp fastmcp uvicorn
```

## 3) Start the server (HTTP)

The `simpleMCPserver.py` file creates an instance of `FastMCP` and calls `mcp.run('http')`. By default this starts an HTTP server bound to `http://localhost:8000/mcp`.

Start the server from the project root (with the venv active):

```bash
python simpleMCPserver.py
```

You should see server logs indicating an HTTP server has started. The MCP endpoint path is `/mcp` (for example `http://localhost:8000/mcp`).

If you prefer to run with `uvicorn` directly (more control over host/port):

```bash
# if FastMCP exposes an ASGI app name like `app`, run:
# uvicorn simpleMCPserver:app --host 0.0.0.0 --port 8000
```

Note: The simple server script already calls `mcp.run('http')`, so running the script directly is the easiest approach.

## 4) Run the client

The `simpleMCPClient.py` uses `fastmcp.Client` pointed at `http://localhost:8000/mcp` and then prompts for which tool to call.

Run it while the server is running in another terminal (venv active):

```bash
python simpleMCPClient.py
```

Follow the interactive prompts:

- To call `greet`, enter `greet` when asked, then provide a name. Expected printed result: "Hello, <name>!".
- To call `add`, enter `add` when asked, then provide integer values for `a` and `b`. Expected printed result: the numeric sum.

Example session (client side):

- Prompt: Press Enter to call tool name, add or greet:
- Type `greet` and press Enter
- Prompt: Enter name: Alice
- Client prints: Hello, Alice!

Another example for `add`:

- Type `add` then enter 3 and 5 when prompted
- Client prints: 8

## 5) Troubleshooting & verification

- If you see `ModuleNotFoundError` for `fastmcp` or `mcp`, confirm your venv is activated and that `pip install -r requirements.txt` completed successfully.
- If the server fails to bind to port 8000 (address in use), either stop the process using that port or change the port in the server run call (or with `uvicorn --port <port>`).
- To verify the server HTTP endpoint is reachable, use curl or a browser:

```bash
curl -v http://localhost:8000/mcp
```

This may return a small MCP server description or an HTTP 200/204 depending on the MCP framework behaviour. If you get a connection refused error, the server isn't running or is bound to a different host/port.

If the client reports unexpected errors when calling a tool, inspect the server logs for exceptions. Common causes:

- Tool name mismatch (client sends a tool name not registered by the server)
- Incorrect argument types (e.g., sending strings where ints are expected)

## Quick checklist

1. Activate venv
2. pip install -r requirements.txt
3. Start server: `python simpleMCPserver.py`
4. Run client in a separate terminal: `python simpleMCPClient.py`


