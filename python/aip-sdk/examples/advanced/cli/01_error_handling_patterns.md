# 02 Error Handling Patterns - CLI Example

## 🎯 Goal
Demonstrate how to use the AIP CLI to implement robust error handling patterns when working with agents, tools, and MCPs. Show best practices for handling different types of errors and implementing retry logic.

## ⏱️ Estimated Time
10-15 minutes

## 📋 Prerequisites
- AIP CLI installed and configured (`aip init`)
- Backend services running
- Valid API credentials
- Understanding of basic CLI operations

## 🚀 Run

### Phase 1: Setup and Basic Error Testing

#### 1.1 Test Invalid Resource Access
```bash
# Test with invalid agent ID
aip agents get invalid-uuid-format

# Test with non-existent agent
aip agents get 00000000-0000-0000-0000-000000000000

# Test with invalid tool ID
aip tools get invalid-tool-id

# Test with invalid MCP ID
aip mcps get invalid-mcp-id
```

#### 1.2 Test Invalid Input Parameters
```bash
# Test agent creation with missing required fields
aip agents create --name "test_agent"
# Should fail due to missing instructions

# Test tool creation with invalid file
aip tools create --file non_existent_file.py --name "invalid_tool"

# Test MCP creation with invalid config
aip mcps create --name "test_mcp" --type "invalid_type"
```

### Phase 2: Error Recovery and Retry Patterns

#### 2.1 Create Test Resources for Error Scenarios
```bash
# Create a simple tool for testing
cat > test_error_tool.py << 'EOF'
def test_function():
    """A simple test function."""
    return "Hello from test tool"
EOF

# Create the tool
aip tools create \
  --file test_error_tool.py \
  --name "error_test_tool" \
  --description "Tool for testing error handling patterns"

# Note the tool ID
TOOL_ID=$(aip tools list --view json | jq -r '.[] | select(.name == "error_test_tool") | .id')
echo "Tool ID: $TOOL_ID"

# Create an agent with the tool
aip agents create \
  --name "error_test_agent" \
  --instructions "You are a test agent for demonstrating error handling. Use your tools when appropriate." \
  --tools $TOOL_ID

# Note the agent ID
AGENT_ID=$(aip agents list --view json | jq -r '.[] | select(.name == "error_test_agent") | .id')
echo "Agent ID: $AGENT_ID"
```

#### 2.2 Test Graceful Degradation
```bash
# Test agent with valid request
aip agents run $AGENT_ID \
  --input "Hello, can you introduce yourself?"

# Test agent with potentially problematic request
aip agents run $AGENT_ID \
  --input "Please perform a complex calculation that might exceed your capabilities"

# Test with very long input that might trigger limits
long_input=$(printf 'A%.0s' {1..1000})
aip agents run $AGENT_ID \
  --input "$long_input"
```

### Phase 3: Advanced Error Handling

#### 3.1 Test Resource Conflicts
```bash
# Try to create duplicate resources
aip agents create \
  --name "error_test_agent" \
  --instructions "This should fail due to duplicate name"

aip tools create \
  --file test_error_tool.py \
  --name "error_test_tool" \
  --description "This should fail due to duplicate name"
```

#### 3.2 Test Network and Timeout Scenarios
```bash
# Test with very short timeout (if supported)
aip agents run $AGENT_ID \
  --input "Please provide a detailed analysis of quantum computing" \
  --timeout 1

# Test with different view formats to see error handling
aip agents run $AGENT_ID \
  --input "Test request" \
  --view json

aip agents run $AGENT_ID \
  --input "Test request" \
  --view plain
```

#### 3.3 Test Tool Integration Errors
```bash
# Test agent with tool that might fail
aip agents run $AGENT_ID \
  --input "Please use your test tool to perform a complex operation"

# Test with malformed input that might confuse the agent
aip agents run $AGENT_ID \
  --input "Execute: rm -rf /; sudo shutdown -h now"
```

### Phase 4: Error Analysis and Debugging

#### 4.1 Analyze Error Responses
```bash
# Use JSON view to get detailed error information
aip agents get invalid-id --view json

aip tools get invalid-id --view json

aip mcps get invalid-id --view json

# Test list commands with invalid parameters
aip agents list --view json --limit invalid-number
```

#### 4.2 Test Error Recovery
```bash
# Test updating resources with invalid data
aip agents update $AGENT_ID \
  --instructions ""

aip tools update $TOOL_ID \
  --description ""

# Test with malformed JSON if supported
echo '{"invalid": "json"' > malformed.json
# Try to use malformed.json in commands if supported
```

### Phase 5: Cleanup and Verification

#### 5.1 Cleanup Test Resources
```bash
# Delete test agent
aip agents delete $AGENT_ID

# Delete test tool
aip tools delete $TOOL_ID

# Remove test files
rm -f test_error_tool.py malformed.json
```

#### 5.2 Final Verification
```bash
# Verify cleanup
aip agents list
aip tools list

# Test status
aip status
```

## 📤 Expected Output

### Invalid Resource Access
```bash
❌ Error: Invalid UUID format
# or
❌ Error: Resource not found
```

### Missing Required Fields
```bash
❌ Error: Missing required field 'instructions'
# or
❌ Error: Validation failed
```

### Duplicate Resource Creation
```bash
❌ Error: Resource with name 'error_test_agent' already exists
# or
❌ Error: Conflict - duplicate resource
```

### Timeout Errors
```bash
⏳ Request timed out after 1 second
# or
❌ Error: Request timeout
```

### JSON Error Details
```json
{
  "error": "Resource not found",
  "error_type": "NotFoundError",
  "status_code": 404,
  "request_id": "req_123456"
}
```

## 🔧 Troubleshooting

### Common Error Patterns
- **Validation Errors**: Check required fields and data formats
- **Authentication Errors**: Verify API credentials and permissions
- **Resource Errors**: Ensure resources exist and are accessible
- **Network Errors**: Check connectivity and backend status
- **Timeout Errors**: Adjust timeout values or simplify requests

### Debugging Tips
- Use `--view json` for detailed error information
- Check backend logs for server-side errors
- Verify resource IDs before operations
- Test with simple requests first
- Use `aip status` to check system health

### Error Recovery Strategies
- **Retry Logic**: Implement exponential backoff for transient errors
- **Graceful Degradation**: Handle partial failures gracefully
- **Resource Validation**: Verify resources before operations
- **User Feedback**: Provide clear error messages to users

## 🧹 Cleanup

The demo includes comprehensive cleanup:
- All test agents are deleted
- All test tools are removed
- Test files are cleaned up
- Final verification confirms clean state

## 💡 Key Concepts Demonstrated

1. **Error Types**: Understanding different error categories
2. **Error Handling**: Implementing robust error handling patterns
3. **Recovery Strategies**: Graceful degradation and retry logic
4. **Debugging**: Using CLI tools for error analysis
5. **Best Practices**: Following error handling best practices
6. **User Experience**: Providing clear error feedback

## 🔗 Related Examples

- **Getting Started**: `01_hello_world_agent.md` - Basic operations
- **Intermediate**: `01_conversation_memory.md` - Memory management
- **Advanced**: `01_agent_workflow_orchestration.md` - Complex workflows
- **SDK**: `02_error_handling_patterns.py` - Programmatic error handling

## 🚀 Advanced Usage

### Error Monitoring
```bash
# Monitor for specific error types
aip agents list --view json | jq '.[] | select(.status == "error")'

# Track error patterns over time
for i in {1..5}; do
  echo "Test $i:"
  aip agents run $AGENT_ID --input "Test request $i"
  echo "---"
done
```

### Automated Error Recovery
```bash
# Script to retry failed operations
max_retries=3
for attempt in $(seq 1 $max_retries); do
  if aip agents run $AGENT_ID --input "Test request"; then
    echo "Success on attempt $attempt"
    break
  else
    echo "Failed on attempt $attempt"
    sleep $((2 ** attempt))
  fi
done
```

This example demonstrates comprehensive error handling patterns that are essential for building robust AI agent applications! 🛡️
