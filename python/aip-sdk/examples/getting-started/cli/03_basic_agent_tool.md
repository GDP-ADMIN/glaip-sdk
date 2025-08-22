# Basic Agent with Tool (CLI)

Create an agent that uses a custom tool to demonstrate basic tool integration.

## Commands

### Create Calculator Tool
Create `calculator_tool.py`:
```python
def calculator(operation: str, a: float, b: float) -> str:
    if operation == "add":
        return f"{a} + {b} = {a + b}"
    elif operation == "multiply":
        return f"{a} × {b} = {a * b}"
    elif operation == "divide":
        return f"{a} ÷ {b} = {a / b}" if b != 0 else "Error: Cannot divide by zero"
    return f"Error: Unknown operation '{operation}'"
```

### Create Tool
```bash
aip tools create calculator_tool.py \
  --name "calculator-tool" \
  --framework "langchain"
```

### Create Agent with Tool
```bash
aip agents create \
  --name "calculator-agent" \
  --instruction "You are a helpful AI assistant with access to a calculator tool. Use the calculator for math problems." \
  --tools "calculator-tool"
```

### Test Agent
```bash
aip agents run <AGENT_ID> --input "What is 15 + 27?"
```

### Clean Up
```bash
aip agents delete <AGENT_ID>
aip tools delete <TOOL_ID>
```

### Verify
```bash
aip tools list
aip agents list
```
