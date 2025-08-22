# Hello World Tool (CLI)

Create and use a simple custom tool with the AIP CLI.

## Commands

### Create Tool Script
Create `hello_tool.py`:
```python
def hello_world(name: str = "World") -> str:
    return f"Hello, {name}! Welcome to the AI Agent Platform!"
```

### Create Tool
```bash
aip tools create hello_tool.py \
  --name "hello-world-tool" \
  --description "A simple tool that says hello to users"
```

### Create Agent with Tool
```bash
aip agents create \
  --name "hello-agent" \
  --instruction "You are a friendly AI assistant. Use the hello world tool to greet users." \
  --tools "hello-world-tool"
```

### Test Tool
```bash
aip agents run <AGENT_ID> --input "Please greet me using your hello world tool!"
```

### Clean Up
```bash
aip agents delete <AGENT_ID>
aip tools delete <TOOL_ID>
```

### Verify
```bash
aip tools list
aip tools get <TOOL_ID>
```
