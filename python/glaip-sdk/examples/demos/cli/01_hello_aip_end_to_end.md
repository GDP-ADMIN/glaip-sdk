# 01 Hello AIP End-to-End - CLI Demo

## 🎯 Goal
Demonstrate a complete end-to-end workflow using the AIP CLI, from initial setup through resource creation, testing, and cleanup. This demo shows the full lifecycle of working with the AI Agent Platform.

## ⏱️ Estimated Time
10-15 minutes

## 📋 Prerequisites
- AIP CLI installed and configured (`aip init`)
- Backend services running
- Valid API credentials
- Clean environment (no existing test resources)

## 🚀 Run

### Phase 1: Initial Setup & Verification

#### 1.1 Verify Configuration
```bash
# Check current configuration
aip config list

# Verify connection status
aip status

# List available models
aip models list
```

#### 1.2 Clean Environment
```bash
# List existing resources to see what's already there
aip agents list
aip tools list
aip mcps list

# Note any existing resources for later cleanup
```

### Phase 2: Tool Creation & Management

#### 2.1 Create Test Tool
```bash
# Create a simple Python tool file
cat > demo_greeting_tool.py << 'EOF'
def greet_user(name: str, time_of_day: str = "day") -> str:
    """Greet a user with a personalized message."""
    return f"Good {time_of_day}, {name}! Welcome to the AI Agent Platform."
EOF

# Create the tool using the CLI
aip tools create \
  --file demo_greeting_tool.py \
  --name "demo_greeting_tool" \
  --description "Simple greeting tool for end-to-end demo purposes"
```

#### 2.2 Verify Tool Creation
```bash
# List all tools to confirm creation
aip tools list

# Get detailed information about the created tool
aip tools get <TOOL_ID>

# Note the tool ID for later use
TOOL_ID="<TOOL_ID>"
```

### Phase 3: Agent Creation & Configuration

#### 3.1 Create Demo Agent
```bash
# Create an agent with the greeting tool
aip agents create \
  --name "demo_agent" \
  --instructions "You are a helpful AI assistant for demonstrating the AI Agent Platform. You have access to a greeting tool that you should use when appropriate. Always be friendly and informative." \
  --tools $TOOL_ID
```

#### 3.2 Verify Agent Creation
```bash
# List all agents to confirm creation
aip agents list

# Get detailed information about the agent
aip agents get <AGENT_ID>

# Note the agent ID for later use
AGENT_ID="<AGENT_ID>"
```

### Phase 4: Agent Testing & Execution

#### 4.1 Basic Agent Test
```bash
# Test basic agent functionality
aip agents run $AGENT_ID \
  --input "Hello! Can you introduce yourself and explain what you can do?"
```

#### 4.2 Tool Integration Test
```bash
# Test agent using the greeting tool
aip agents run $AGENT_ID \
  --input "Please greet Raymond using your greeting tool"
```

#### 4.3 Complex Query Test
```bash
# Test with a more complex request
aip agents run $AGENT_ID \
  --input "Explain how you work with tools and what makes you different from a regular chatbot"
```

### Phase 5: Agent Updates & Modifications

#### 5.1 Update Agent Instructions
```bash
# Update the agent with enhanced instructions
aip agents update $AGENT_ID \
  --instructions "You are a helpful AI assistant for demonstrating the AI Agent Platform. You have access to a greeting tool that you should use when appropriate. Always be friendly, informative, and mention that this is a demo. Keep responses concise but helpful. When asked about your capabilities, emphasize your tool integration features."
```

#### 5.2 Verify Updates
```bash
# Get updated agent information
aip agents get $AGENT_ID

# Test the updated agent
aip agents run $AGENT_ID \
  --input "What are your updated capabilities and how do you work with tools?"
```

### Phase 6: Advanced Testing

#### 6.1 Test Different View Formats
```bash
# Test with rich view (default)
aip agents run $AGENT_ID \
  --input "Give me a summary of what we've accomplished in this demo" \
  --view rich

# Test with plain view
aip agents run $AGENT_ID \
  --input "List the key features you've demonstrated" \
  --view plain

# Test with JSON view
aip agents run $AGENT_ID \
  --input "Provide a structured response about your tool capabilities" \
  --view json
```

#### 6.2 Test with File Attachment
```bash
# Create a test document
echo "This is a test document for the AIP CLI demo. It contains information about artificial intelligence and agent platforms." > demo_document.txt

# Test agent with file processing
aip agents run $AGENT_ID \
  --input "Please analyze this document and provide insights" \
  --file demo_document.txt
```

### Phase 7: Performance & Monitoring

#### 7.1 Test Multiple Requests
```bash
# Test multiple rapid requests to see performance
for i in {1..3}; do
  echo "Request $i:"
  aip agents run $AGENT_ID \
    --input "Quick test request $i - respond briefly" \
    --view plain
  echo "---"
done
```

#### 7.2 Monitor Resource Usage
```bash
# Check current status
aip status

# List all resources
echo "Current Resources:"
aip agents list --view plain
aip tools list --view plain
```

### Phase 8: Cleanup & Verification

#### 8.1 Cleanup Resources
```bash
# Delete the demo agent
aip agents delete $AGENT_ID

# Delete the demo tool
aip tools delete $TOOL_ID

# Remove test files
rm -f demo_greeting_tool.py demo_document.txt
```

#### 8.2 Final Verification
```bash
# Verify cleanup
echo "Verifying cleanup:"
aip agents list
aip tools list

# Check final status
aip status
```

## 📤 Expected Output

### Tool Creation
```bash
✅ Tool created successfully: demo_greeting_tool (ID: 123e4567-e89b-12d3-a456-426614174000)
```

### Agent Creation
```bash
✅ Agent created successfully: demo_agent (ID: 987fcdef-1234-5678-9abc-def123456789)
```

### Basic Agent Response
```bash
Hello! I'm your AI assistant for demonstrating the AI Agent Platform. I'm designed to be helpful and informative, and I have access to a greeting tool that I can use when appropriate. I'm here to showcase the platform's capabilities and help you understand how AI agents can work with tools to provide enhanced functionality.
```

### Tool Integration Response
```bash
I'll use my greeting tool to greet you, Raymond!

Good day, Raymond! Welcome to the AI Agent Platform.

This demonstrates how I can integrate with tools to provide specific functionality. The greeting tool allows me to create personalized messages, showing the power of tool integration in AI agents.
```

### Updated Agent Response
```bash
Based on my updated instructions, I'm a helpful AI assistant for demonstrating the AI Agent Platform. I have access to a greeting tool that I use when appropriate, and I'm designed to be friendly, informative, and mention that this is a demo.

My key capabilities include:
- Tool integration (like the greeting tool)
- Natural language processing
- Context awareness
- Demo-focused responses

I keep my responses concise but helpful, emphasizing the platform's tool integration features that make me different from regular chatbots.
```

## 🔧 Troubleshooting

### Tool Creation Issues
- Ensure the Python file syntax is correct
- Check file permissions and readability
- Verify the backend supports tool creation
- Use `--view json` for detailed error information

### Agent Creation Issues
- Verify the tool ID is correct and exists
- Check that instructions are properly formatted
- Ensure the backend is running and accessible
- Check API credentials with `aip config list`

### Execution Issues
- Verify the agent ID is correct
- Check backend status with `aip status`
- Ensure the agent has the required tools
- Use `--view plain` for simpler output if rich view fails

### Cleanup Issues
- Verify resource IDs before deletion
- Check if resources are already deleted
- Use `--view json` to see detailed resource information
- Ensure you have proper permissions

## 🧹 Cleanup

The demo includes comprehensive cleanup:
- All created agents are deleted
- All created tools are removed
- Test files are cleaned up
- Final verification confirms clean state

## 💡 Key Concepts Demonstrated

1. **Complete Workflow**: End-to-end resource lifecycle management
2. **Tool Integration**: Creating and using custom tools with agents
3. **Agent Management**: Creation, configuration, and updates
4. **Testing Strategies**: Multiple test scenarios and view formats
5. **Resource Cleanup**: Proper cleanup and verification
6. **CLI Proficiency**: Comprehensive use of all major CLI commands

## 🔗 Related Examples

- **Getting Started**: `01_hello_world_agent.md` - Basic agent creation
- **Intermediate**: `01_conversation_memory.md` - Memory capabilities
- **Advanced**: `01_agent_workflow_orchestration.md` - Complex workflows
- **SDK**: `01_hello_aip_end_to_end.py` - Programmatic equivalent

## 🚀 Advanced Usage

### Batch Processing
```bash
# Create multiple tools in batch
for tool_name in "tool1" "tool2" "tool3"; do
  echo "Creating $tool_name..."
  # Tool creation commands
done
```

### Automation Scripts
```bash
# Use JSON view for automation
aip agents list --view json | jq '.[] | select(.name | contains("demo")) | .id'
```

### Error Handling
```bash
# Test error scenarios
aip agents get invalid-uuid
aip tools get non-existent-tool
```

This demo provides a comprehensive introduction to the AIP CLI and demonstrates best practices for resource management and testing! 🎉
