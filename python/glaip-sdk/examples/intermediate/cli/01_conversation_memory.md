# 01 Conversation Memory - CLI Example

## 🎯 Goal
Demonstrate how to use the AIP CLI to create and manage agents with conversation memory capabilities, showing how agents can maintain context across multiple interactions using chat history.

## ⏱️ Estimated Time
5-10 minutes

## 📋 Prerequisites
- AIP CLI installed and configured (`aip init`)
- Backend services running
- Valid API credentials

## 🚀 Run

### Step 1: Create an Agent with Memory Instructions
```bash
# Create an agent designed for conversation memory
aip agents create \
  --name "memory_agent" \
  --instructions "You are a helpful AI assistant with excellent memory. Remember details from our conversation and refer back to them when relevant. Always acknowledge what you remember from previous exchanges."
```

### Step 2: Verify Agent Creation
```bash
# List all agents to confirm creation
aip agents list

# Get detailed information about the agent
aip agents get <AGENT_ID>
```

### Step 3: Test Conversation Memory with Chat History
```bash
# First interaction - establish context
FIRST_RESPONSE=$(aip agents run <AGENT_ID> \
  --input "Hello! My name is Raymond and I'm working on an AI agent platform project. I'm particularly interested in conversation memory capabilities." \
  --view json | jq -r '.response')

echo "First response: $FIRST_RESPONSE"

# Second interaction - test memory recall (pass chat history)
SECOND_RESPONSE=$(aip agents run <AGENT_ID> \
  --input "What do you remember about me from our previous conversation?" \
  --chat-history "[{\"role\": \"user\", \"content\": \"Hello! My name is Raymond and I'm working on an AI agent platform project. I'm particularly interested in conversation memory capabilities.\"}, {\"role\": \"assistant\", \"content\": \"$FIRST_RESPONSE\"}]" \
  --view json | jq -r '.response')

echo "Second response: $SECOND_RESPONSE"

# Third interaction - test memory persistence (pass updated chat history)
THIRD_RESPONSE=$(aip agents run <AGENT_ID> \
  --input "Can you remind me what project I mentioned I was working on?" \
  --chat-history "[{\"role\": \"user\", \"content\": \"Hello! My name is Raymond and I'm working on an AI agent platform project. I'm particularly interested in conversation memory capabilities.\"}, {\"role\": \"assistant\", \"content\": \"$FIRST_RESPONSE\"}, {\"role\": \"user\", \"content\": \"What do you remember about me from our previous conversation?\"}, {\"role\": \"assistant\", \"content\": \"$SECOND_RESPONSE\"}]" \
  --view json | jq -r '.response')

echo "Third response: $THIRD_RESPONSE"
```

### Step 4: Test Memory with Different Contexts
```bash
# Test memory with specific details (pass full chat history)
FOURTH_RESPONSE=$(aip agents run <AGENT_ID> \
  --input "I'm planning to implement a feature that allows agents to remember user preferences. What do you think about this approach?" \
  --chat-history "[{\"role\": \"user\", \"content\": \"Hello! My name is Raymond and I'm working on an AI agent platform project. I'm particularly interested in conversation memory capabilities.\"}, {\"role\": \"assistant\", \"content\": \"$FIRST_RESPONSE\"}, {\"role\": \"user\", \"content\": \"What do you remember about me from our previous conversation?\"}, {\"role\": \"assistant\", \"content\": \"$SECOND_RESPONSE\"}, {\"role\": \"user\", \"content\": \"Can you remind me what project I mentioned I was working on?\"}, {\"role\": \"assistant\", \"content\": \"$THIRD_RESPONSE\"}]" \
  --view json | jq -r '.response')

echo "Fourth response: $FOURTH_RESPONSE"

# Verify memory retention (pass updated chat history)
FIFTH_RESPONSE=$(aip agents run <AGENT_ID> \
  --input "What was the specific feature I mentioned wanting to implement?" \
  --chat-history "[{\"role\": \"user\", \"content\": \"Hello! My name is Raymond and I'm working on an AI agent platform project. I'm particularly interested in conversation memory capabilities.\"}, {\"role\": \"assistant\", \"content\": \"$FIRST_RESPONSE\"}, {\"role\": \"user\", \"content\": \"What do you remember about me from our previous conversation?\"}, {\"role\": \"assistant\", \"content\": \"$SECOND_RESPONSE\"}, {\"role\": \"user\", \"content\": \"Can you remind me what project I mentioned I was working on?\"}, {\"role\": \"assistant\", \"content\": \"$THIRD_RESPONSE\"}, {\"role\": \"user\", \"content\": \"I'm planning to implement a feature that allows agents to remember user preferences. What do you think about this approach?\"}, {\"role\": \"assistant\", \"content\": \"$FOURTH_RESPONSE\"}]" \
  --view json | jq -r '.response')

echo "Fifth response: $FIFTH_RESPONSE"
```

## 📤 Expected Output

### Agent Creation
```bash
✅ Agent created successfully: memory_agent (ID: 123e4567-e89b-12d3-a456-426614174000)
```

### First Interaction
```bash
First response: Hello Raymond! It's great to meet you. I understand you're working on an AI agent platform project, and you're specifically interested in conversation memory capabilities. This is a fascinating area of AI development that can significantly enhance user experience by maintaining context across interactions.
```

### Memory Recall
```bash
Second response: I remember that your name is Raymond and you're working on an AI agent platform project. You specifically mentioned being interested in conversation memory capabilities, which is exactly what we're exploring right now!
```

### Memory Persistence
```bash
Third response: You mentioned you're working on an AI agent platform project. You were particularly interested in conversation memory capabilities, and in our last exchange, you mentioned planning to implement a feature that allows agents to remember user preferences.
```

## 🔧 Troubleshooting

### Agent Not Responding
- Verify the agent is running: `aip agents get <AGENT_ID>`
- Check backend status: `aip status`
- Ensure API credentials are valid: `aip config list`

### Memory Not Working
- **Important**: The agent doesn't have innate memory - you must pass `--chat-history` with previous conversations
- Confirm the agent instructions mention memory capabilities
- Check if the backend supports conversation memory features
- Verify the agent is the same one across all interactions

### API Errors
- Check your API key: `aip config get api_key`
- Verify the backend URL: `aip config get api_url`
- Test connectivity: `aip status`

### Chat History Format
- Chat history must be valid JSON array with `role` and `content` fields
- Use `--view json` to get structured responses for building chat history
- Each interaction should include the full conversation history

## 🧹 Cleanup

```bash
# Delete the test agent
aip agents delete <AGENT_ID>

# Verify cleanup
aip agents list
```

## 💡 Key Concepts Demonstrated

1. **Chat History Management**: How to build and pass conversation context
2. **Memory Persistence**: Agents can remember context when provided with chat history
3. **Contextual Recall**: Agents can reference previous conversation details
4. **Memory Validation**: Testing that memory features work with proper chat history

## 🔗 Related Examples

- **Getting Started**: `01_hello_world_agent.md` - Basic agent creation
- **Advanced**: `03_agent_workflow_orchestration.md` - Complex memory workflows
- **SDK**: `01_conversation_memory.py` - Programmatic memory management

## 📝 Note on Memory Implementation

**Important**: The AIP backend doesn't have innate memory. Instead, you must:
1. **Pass chat history** with each request using `--chat-history`
2. **Build the history** by collecting responses from previous interactions
3. **Maintain context** by including the full conversation in each request

This approach gives you full control over what context is shared and allows for session isolation.
