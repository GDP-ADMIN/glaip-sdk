# Hello World MCP (CLI)

Create and manage a simple MCP (Model Context Protocol) server using the AIP CLI.

## Commands

### Create MCP Server
```bash
aip mcps create \
  --name "hello-world-mcp" \
  --description "A simple MCP server for demonstration" \
  --transport "http" \
  --config '{"url": "http://localhost:8080", "tools": ["hello", "time"]}'
```

### Get MCP Details
```bash
aip mcps get <MCP_ID>
```

### List MCP Tools
```bash
aip mcps tools <MCP_ID>
```

### Clean Up
```bash
aip mcps delete <MCP_ID>
```

### Verify
```bash
aip mcps list
aip mcps status <MCP_ID>
```
