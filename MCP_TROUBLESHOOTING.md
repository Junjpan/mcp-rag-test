# MCP Server Troubleshooting Guide

## Current Status
- ✅ MCP server is running at `http://localhost:8000/mcp`
- ✅ Server responds correctly (expects SSE/event-stream)
- ⚠️ Tools may not be visible/working in Cursor

## Troubleshooting Steps

### 1. Verify Server is Running
Check if the server is running:
```powershell
Test-NetConnection -ComputerName localhost -Port 8000
```

Or start it if not running:
```powershell
python mcp_server.py
```

### 2. Check Cursor MCP Settings
1. Open Cursor Settings: `Ctrl+,` (or `File` → `Preferences` → `Settings`)
2. Navigate to `Features` → `MCP`
3. Verify that `mcp-rag-app` appears in the list of servers
4. Check if tools are listed:
   - `python_faq_retrieval_tool`
   - `firecrawl_web_search_tool`

### 3. Configuration Location Options

**Workspace config (current):** `.cursor/mcp.json`
- Only applies to this workspace
- Good for project-specific servers

**Global config:** `%USERPROFILE%\.cursor\mcp.json` (Windows)
- Applies to all Cursor workspaces
- Better for system-wide servers

If workspace config doesn't work, try global config.

### 4. Configuration Format Variations

Current config uses `"type": "http"`. Try these alternatives:

**Option A: SSE type** (since FastMCP uses Server-Sent Events)
```json
{
  "mcpServers": {
    "mcp-rag-app": {
      "type": "sse",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Option B: Streamable HTTP**
```json
{
  "mcpServers": {
    "mcp-rag-app": {
      "type": "streamable-http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Option C: With explicit command (if Cursor supports it)**
```json
{
  "mcpServers": {
    "mcp-rag-app": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### 5. Restart Cursor
After changing configuration:
1. Save the `mcp.json` file
2. Completely close and restart Cursor
3. Check Settings → Features → MCP again

### 6. Check Cursor Version
- Known bug in Cursor 0.47.8 with tool name prefixing
- Update to latest Cursor version if possible
- Check version: `Help` → `About`

### 7. Verify Tool Registration
The tools are defined as:
- `python_faq_retrieval_tool` ✅ (snake_case - correct)
- `firecrawl_web_search_tool` ✅ (snake_case - correct)

Both follow the expected naming convention.

### 8. Test Server Directly
Use the simple client to test:
```powershell
python simpleMCPClient.py
```

This verifies the server works independently of Cursor.

### 9. Check Logs
- Cursor logs might show MCP connection errors
- Server console output might show connection attempts
- Look for errors in both places

### 10. Alternative: Use stdio Transport
If HTTP/SSE doesn't work, FastMCP also supports stdio:
```python
mcp_server.run('stdio')
```

Then configure in Cursor as:
```json
{
  "mcpServers": {
    "mcp-rag-app": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

## Current Configuration
File: `.cursor/mcp.json`
```json
{
  "mcpServers": {
    "mcp-rag-app": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Next Steps
1. Restart Cursor
2. Check Settings → Features → MCP
3. Try the different configuration formats if needed
4. Check Cursor version and update if old

