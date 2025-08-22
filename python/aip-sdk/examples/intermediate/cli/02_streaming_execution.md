# 02 Streaming Execution - CLI Example

## 🎯 Goal
Demonstrate how to use the AIP CLI to run agents with streaming execution, showing that streaming is automatic and default in the AIP platform.

## ⏱️ Estimated Time
5-10 minutes

## 📋 Prerequisites
- AIP CLI installed and configured (`aip init`)
- Backend services running
- Valid API credentials

## 🚀 Run

### Step 1: Create a Test Agent
```bash
# Create an agent for testing streaming behavior
aip agents create \
  --name "streaming_demo_agent" \
  --instructions "You are a helpful AI assistant that can use tools and provide detailed explanations. When asked to explain something, break it down into clear sections with examples."
```

### Step 2: Verify Agent Creation
```bash
# List all agents to confirm creation
aip agents list

# Get detailed information about the agent
aip agents get <AGENT_ID>
```

### Step 3: Test Natural Streaming Behavior
```bash
# Test with a simple request - streaming is automatic!
aip agents run <AGENT_ID> \
  --input "Please explain the concept of artificial intelligence in simple terms"
```

### Step 4: Test Streaming with Different View Formats
```bash
# Test streaming with rich view (default - shows real-time streaming)
aip agents run <AGENT_ID> \
  --input "Describe the architecture of a microservices system" \
  --view rich

# Test streaming with plain view (still streams, just different formatting)
aip agents run <AGENT_ID> \
  --input "Explain the benefits of containerization" \
  --view plain

# Test streaming with JSON view for automation (still streams)
aip agents run <AGENT_ID> \
  --input "List the key principles of DevOps" \
  --view json
```

### Step 5: Test Streaming with Tools (if available)
```bash
# Test streaming with tool usage - tools execute in real-time
aip agents run <AGENT_ID> \
  --input "What is the current time? Please use your available tools."
```

### Step 6: Test Streaming with File Attachments
```bash
# Create a test file for analysis
echo "This is a sample document about artificial intelligence and its applications in modern technology." > ai_document.txt

# Test streaming with file processing
aip agents run <AGENT_ID> \
  --input "Please analyze this document and provide insights about AI applications mentioned." \
  --file ai_document.txt
```

## 📤 Expected Output

### Agent Creation
```bash
✅ Agent created successfully: streaming_demo_agent (ID: 123e4567-e89b-12d3-a456-426614174000)
```

### Streaming Response (Rich View - Default)
```bash
🤖 streaming_demo_agent is thinking...

Let me explain artificial intelligence in simple terms:

1. **What is Artificial Intelligence?**
   Artificial intelligence, or AI, is when computers or machines are made to think and learn like humans.

2. **How Does It Work?**
   - Data Collection: Gather relevant information
   - Data Preparation: Clean and organize the data
   - Model Training: Teach the algorithm patterns
   - Evaluation: Test how well it performs
   - Deployment: Use the trained model

3. **Real-World Examples:**
   - Recommendation systems (Netflix, Amazon)
   - Image recognition (Google Photos)
   - Language translation (Google Translate)
   - Fraud detection (banking systems)

4. **Benefits:**
   - Automates complex tasks
   - Improves over time
   - Handles large datasets efficiently
   - Provides personalized experiences
```

### Streaming with File Analysis
```bash
📄 Analyzing document: ai_document.txt

Based on the document content, here are the key insights about AI applications:

**Main Topics Identified:**
- Artificial Intelligence fundamentals
- Modern technology applications
- Practical implementations

**Key Applications Mentioned:**
1. **Technology Integration**: AI in modern systems
2. **Practical Use Cases**: Real-world applications
3. **Industry Impact**: Transformation of various sectors

**Analysis Summary:**
The document provides a high-level overview of AI and its role in contemporary technology, emphasizing practical applications and real-world impact.
```

## 🔧 Troubleshooting

### Streaming Not Working
- **Note**: Streaming is automatic and enabled by default in AIP
- Verify the backend is running: `aip status`
- Check if the agent model supports streaming responses
- Ensure you're using a recent version of the CLI
- Try different view formats to see if streaming works in some modes

### Slow Response Times
- Check backend performance: `aip status`
- Verify network connectivity
- Consider using `--view plain` for faster output
- Check if the request is particularly complex

### View Format Issues
- Rich view requires TTY support and shows real-time streaming
- Use `--no-tty` if running in non-interactive environments
- JSON view is best for automation and scripting
- Plain view works in all environments

### File Processing Errors
- Ensure the file exists and is readable
- Check file size limits
- Verify supported file formats
- Use absolute paths if relative paths fail

## 🧹 Cleanup

```bash
# Delete the test agent
aip agents delete <AGENT_ID>

# Remove test files
rm -f ai_document.txt

# Verify cleanup
aip agents list
```

## 💡 Key Concepts Demonstrated

1. **Automatic Streaming**: Streaming is enabled by default - no special configuration needed
2. **View Format Options**: Different output formats for different use cases
3. **File Processing**: Handling file attachments with streaming responses
4. **Progress Monitoring**: Watching agent progress in real-time
5. **Format Flexibility**: Switching between rich, plain, and JSON views

## 🔗 Related Examples

- **Getting Started**: `01_hello_world_agent.md` - Basic agent creation
- **Intermediate**: `01_conversation_memory.md` - Memory capabilities
- **Advanced**: `03_agent_workflow_orchestration.md` - Complex workflows
- **SDK**: `02_streaming_execution.py` - Programmatic streaming management

## 🚀 Advanced Usage

### Batch Processing with Streaming
```bash
# Process multiple requests with streaming
for topic in "AI" "ML" "Data Science"; do
  echo "Processing: $topic"
  aip agents run <AGENT_ID> \
    --input "Explain $topic in detail" \
    --view plain
  echo "---"
done
```

### Streaming with Custom Timeouts
```bash
# Set custom timeout for long-running streaming requests
aip agents run <AGENT_ID> \
  --input "Provide a comprehensive analysis of quantum computing" \
  --timeout 120
```

## 📝 Note on Streaming Implementation

**Important**: The AIP platform has streaming enabled by default:
- ✅ **No special methods needed** - streaming is automatic
- ✅ **Real-time feedback** as the agent thinks and responds
- ✅ **Tool execution visible** in real-time
- ✅ **Better user experience** with immediate feedback
- ✅ **Handles long responses** gracefully
- ✅ **Works with all agent operations**

The CLI automatically shows streaming output - you don't need to configure anything special!
