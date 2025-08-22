# Hello World Agent (CLI)

Create and run a simple AI agent using the AIP CLI.

## Commands

### Create Agent
```bash
aip agents create \
  --name "hello-world-agent" \
  --instruction "You are a friendly AI assistant."
```

### Run Agent
```bash
aip agents run <AGENT_ID> --input "Hello! How are you today?"
```

### Clean Up
```bash
aip agents delete <AGENT_ID>
```

### Verify
```bash
aip agents list
aip agents get <AGENT_ID>
```
