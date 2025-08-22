# 04 Agent Tool Integration - CLI Example

## 🎯 Goal
Demonstrate how to use the AIP CLI to create and manage agents with comprehensive tool integration, including native tools, custom tools, and sub-agent delegation with tools.

## ⏱️ Estimated Time
10-15 minutes

## 📋 Prerequisites
- AIP CLI installed and configured (`aip init`)
- Backend services running
- Valid API credentials

## 🚀 Run

### Step 1: Test Native Tools Integration
```bash
# First, discover available native tools
aip tools list

# Create an agent with native tools only
aip agents create \
  --name "native-tools-agent" \
  --instructions "You are a utility assistant with access to native tools. Use your available tools to answer questions about time, dates, and other utilities. Always provide clear, formatted answers after using tools."

# Get the agent ID from the creation output
AGENT_ID=$(aip agents list | grep "native-tools-agent" | awk '{print $1}')

# Test native tool functionality
aip agents run $AGENT_ID \
  --input "What is the current time?"
```

### Step 2: Test Custom Tool Integration
```bash
# Create a custom weather tool from code
cat > weather_tool.py << 'EOF'
from typing import Any
from gllm_plugin.tools import tool_plugin
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class WeatherToolInput(BaseModel):
    location: str = Field(..., description="The city and state, e.g., San Francisco, CA")

@tool_plugin(version="1.0.0")
class WeatherTool(BaseTool):
    name: str = "weather_main"
    description: str = "Useful for when you need to know the weather in a specific location."
    args_schema: type[BaseModel] = WeatherToolInput

    def _run(self, location: str, **kwargs: Any) -> str:
        return f"The weather in {location} is sunny with a temperature of 22°C."
EOF

# Create the custom tool using the CLI
aip tools create \
  --name "custom_weather_tool" \
  --file weather_tool.py \
  --framework langchain

# Get the tool ID
TOOL_ID=$(aip tools list | grep "custom_weather_tool" | awk '{print $1}')

# Create an agent with the custom tool
aip agents create \
  --name "custom-tool-agent" \
  --instructions "You are a weather assistant with access to a custom weather tool. When asked about weather, ALWAYS use your weather tool and provide ONLY the information from the tool. Do not make up weather information." \
  --tools $TOOL_ID

# Get the agent ID
CUSTOM_AGENT_ID=$(aip agents list | grep "custom-tool-agent" | awk '{print $1}')

# Test custom tool functionality
aip agents run $CUSTOM_AGENT_ID \
  --input "What's the weather like in London?"
```

### Step 3: Test Sub-Agent Delegation with Tools
```bash
# Create a weather sub-agent with the custom tool
aip agents create \
  --name "weather-sub-agent" \
  --instructions "You are a weather expert. Always use your weather tool when asked about weather. Provide clear, helpful weather information." \
  --tools $TOOL_ID

# Get the weather sub-agent ID
WEATHER_AGENT_ID=$(aip agents list | grep "weather-sub-agent" | awk '{print $1}')

# Create a time sub-agent with native time tool (if available)
# First, find a time tool
TIME_TOOL_ID=$(aip tools list | grep -i "time" | head -1 | awk '{print $1}')

if [ ! -z "$TIME_TOOL_ID" ]; then
  aip agents create \
    --name "time-sub-agent" \
    --instructions "You are a time expert. Use your time tool to provide current time information." \
    --tools $TIME_TOOL_ID

  TIME_AGENT_ID=$(aip agents list | grep "time-sub-agent" | awk '{print $1}')

  # Create master agent with both sub-agents
  aip agents create \
    --name "master-agent-with-tools" \
    --instructions "You are a master agent that delegates tasks to specialized sub-agents. Delegate weather questions to your weather sub-agent and time questions to your time sub-agent if available. Always coordinate effectively between your sub-agents." \
    --agents $WEATHER_AGENT_ID $TIME_AGENT_ID

  MASTER_AGENT_ID=$(aip agents list | grep "master-agent-with-tools" | awk '{print $1}')

  # Test delegation with both tools
  aip agents run $MASTER_AGENT_ID \
    --input "What is the weather like in Paris and what is the current time?"
else
  # Create master agent with just weather sub-agent
  aip agents create \
    --name "master-agent-with-tools" \
    --instructions "You are a master agent that delegates tasks to specialized sub-agents. Delegate weather questions to your weather sub-agent. Always coordinate effectively between your sub-agents." \
    --agents $WEATHER_AGENT_ID

  MASTER_AGENT_ID=$(aip agents list | grep "master-agent-with-tools" | awk '{print $1}')

  # Test delegation with weather tool only
  aip agents run $MASTER_AGENT_ID \
    --input "What is the weather like in Paris?"
fi
```

## 📤 Expected Output

### Native Tools Test
```bash
✅ Agent created successfully: native-tools-agent (ID: 123e4567-e89b-12d3-a456-426614174000)

🤖 native-tools-agent is thinking...

The current time is: 08/21/25 21:45:00 (UTC or system default timezone). If you need the time in a specific timezone or format, please let me know!

⚙️ time_tool({"datetime_format": "%m/%d/%y %H:%M:%S"}) [0ms] ✓
```

### Custom Tool Test
```bash
✅ Tool created successfully: custom_weather_tool (ID: 456e7890-e89b-12d3-a456-426614174000)

✅ Agent created successfully: custom-tool-agent (ID: 789e0123-e89b-12d3-a456-426614174000)

🤖 custom-tool-agent is thinking...

The weather in London is sunny with a temperature of 22°C.

⚙️ weather_main({"location": "London"}) [0ms] ✓
```

### Sub-Agent Delegation Test
```bash
✅ Agent created successfully: weather-sub-agent (ID: abc12345-e89b-12d3-a456-426614174000)
✅ Agent created successfully: time-sub-agent (ID: def67890-e89b-12d3-a456-426614174000)
✅ Agent created successfully: master-agent-with-tools (ID: ghi11111-e89b-12d3-a456-426614174000)

🤖 master-agent-with-tools is thinking...

The weather in Paris is currently sunny with a temperature of 22°C. The current time in Paris is 21:45 (9:45 PM). If you need more details or updates, just let me know!

⚙️ delegate_to_weather-sub-agent({"query": "What is the weather like in Paris?"}) [2857ms] ✓
⚙️ delegate_to_time-sub-agent [3988ms] ✓
```

## 🔧 Troubleshooting

### Tool Creation Issues
- Verify the tool file syntax is correct
- Check that the tool uses the `@tool_plugin` decorator
- Ensure the tool class inherits from `BaseTool`
- Verify the backend supports the specified framework

### Agent Creation Issues
- Check that tool IDs are valid: `aip tools list`
- Verify agent instructions are clear and specific
- Ensure the backend is running: `aip status`

### Tool Usage Issues
- **Important**: Custom tools must be properly registered to be usable
- Verify the tool was created successfully: `aip tools get <TOOL_ID>`
- Check that the agent has the tool assigned: `aip agents get <AGENT_ID>`
- Ensure the tool name in the code matches what the agent expects

### Sub-Agent Delegation Issues
- Verify all sub-agents exist and are accessible
- Check that the master agent has the correct sub-agent IDs
- Ensure sub-agents have the tools they need

## 🧹 Cleanup

```bash
# Delete all created agents
aip agents delete $AGENT_ID
aip agents delete $CUSTOM_AGENT_ID
aip agents delete $WEATHER_AGENT_ID

if [ ! -z "$TIME_AGENT_ID" ]; then
  aip agents delete $TIME_AGENT_ID
fi

aip agents delete $MASTER_AGENT_ID

# Delete the custom tool
aip tools delete $TOOL_ID

# Remove temporary files
rm -f weather_tool.py

# Verify cleanup
aip agents list
aip tools list
```

## 💡 Key Concepts Demonstrated

1. **Native Tools Integration**: Using built-in tools like time and date utilities
2. **Custom Tool Creation**: Creating and registering custom tool plugins
3. **Tool Assignment**: Assigning tools to agents for specific functionality
4. **Sub-Agent Delegation**: Coordinating multiple specialized agents
5. **Tool Usage Validation**: Ensuring agents actually use their assigned tools

## 🔗 Related Examples

- **Getting Started**: `01_hello_world_agent.md` - Basic agent creation
- **Intermediate**: `01_conversation_memory.md` - Memory capabilities
- **Advanced**: `03_agent_workflow_orchestration.md` - Complex workflows
- **SDK**: `04_agent_tool_integration.py` - Programmatic tool integration

## 📝 Note on Tool Integration

**Important**: The AIP platform supports two types of tools:
1. **Native Tools**: Built-in tools like time, date, and utility functions
2. **Custom Tools**: User-created tools using the `@tool_plugin` decorator

Custom tools must be properly registered using the `/tools/upload` endpoint (which the CLI handles automatically when using `--file`). The CLI's `--file` option ensures tools are created as plugins rather than just metadata.
