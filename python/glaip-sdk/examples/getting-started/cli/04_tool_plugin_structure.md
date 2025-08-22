# Tool Plugin Structure (CLI)

Create tools with the correct plugin structure required for CLI tool creation.

## Important: Tool Plugin Structure

CLI tool creation requires tools to use the proper plugin structure:

```python
from gllm_plugin.tools import tool_plugin
from langchain_core.tools import BaseTool

@tool_plugin(version="1.0.0")
class HelloWorldTool(BaseTool):
    name: str = "hello_world"
    description: str = "A simple tool that says hello to users"

    def _run(self, name: str = "World") -> str:
        return f"Hello, {name}! Welcome to the AI Agent Platform!"
```

## Commands

### Create Tool with Plugin Structure
```bash
aip tools create --file examples/getting-started/sdk/05_test_tool.py \
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
