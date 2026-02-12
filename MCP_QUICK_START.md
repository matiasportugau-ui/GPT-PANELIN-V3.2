# MCP Server Quick Start Guide

**Panelin MCP Server** - Get your Model Context Protocol server running in under 5 minutes.

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Dependencies

```bash
cd mcp
pip install -r requirements.txt
```

This installs:
- `mcp>=1.0.0` - Model Context Protocol SDK
- `uvicorn>=0.30.0` - ASGI server (for remote hosting)
- `starlette>=0.40.0` - Web framework
- `httpx>=0.27.0` - HTTP client
- `pydantic>=2.0.0` - Data validation

### Step 2: Start the Server

**For local testing (stdio transport):**
```bash
python -m mcp.server
```

**For remote hosting (SSE transport):**
```bash
python -m mcp.server --transport sse --port 8000
```

### Step 3: Test the Connection

**With stdio transport:**
The server communicates via standard input/output. Use an MCP client like Claude Desktop to connect.

**With SSE transport:**
```bash
# Test health endpoint
curl http://localhost:8000/sse

# The server is ready when it responds without errors
```

---

## 🔧 Available Tools

Your MCP server exposes 4 tools:

| Tool | Purpose | Example Query |
|------|---------|---------------|
| `price_check` | Look up product pricing | "What's the price of ISODEC-100-1000?" |
| `catalog_search` | Search product catalog | "Find panels for industrial roofs" |
| `bom_calculate` | Calculate Bill of Materials | Generate complete BOM for 12m x 6m roof installation |
| `report_error` | Log KB errors | Report incorrect pricing in knowledge base |

---

## 💡 Integration Examples

### OpenAI Custom GPT

1. Import tool schemas from `mcp/tools/*.json`
2. Configure GPT Actions in OpenAI GPT Builder
3. Map each tool to a GPT Action
4. Test with sample queries

### Claude Desktop

1. Start server with stdio transport: `python -m mcp.server`
2. Configure Claude Desktop MCP settings
3. Point to the server executable
4. Tools will appear in Claude's interface

### Other MCP Clients

The server follows the [MCP specification](https://modelcontextprotocol.io) and works with any compliant client.

---

## 📊 Benefits

| Benefit | Impact |
|---------|--------|
| **Token Savings** | 77% reduction (149K → 34K tokens/session) |
| **Real-time Data** | Dynamic queries instead of static KB files |
| **Error Tracking** | Persistent KB error logging |
| **Standard Protocol** | Works with any MCP client |
| **Scalability** | External data doesn't consume context window |

---

## 🆘 Troubleshooting

**Issue: "Module 'mcp' not found"**
- Solution: Run `pip install -r requirements.txt` from the `mcp/` directory

**Issue: "Port 8000 already in use"**
- Solution: Use a different port: `python -m mcp.server --transport sse --port 8001`

**Issue: "Cannot connect to stdio server"**
- Solution: Ensure your MCP client is configured for stdio transport, not SSE

**Issue: "Tool handler error"**
- Solution: Check that all KB files exist in the parent directory (bromyros_pricing_master.json, etc.)

---

## 📚 Next Steps

- Read the full [MCP Server Documentation](README.md#-mcp-server)
- Review [Tool Schemas](mcp/tools/)
- Check [MCP Comparative Analysis](MCP_SERVER_COMPARATIVE_ANALYSIS.md)
- See [KB Architecture Audit](KB_ARCHITECTURE_AUDIT.md) for optimization details

---

**Status:** ✅ Production Ready | **Version:** 1.0.0  
**Support:** See [README.md](README.md) for detailed documentation
