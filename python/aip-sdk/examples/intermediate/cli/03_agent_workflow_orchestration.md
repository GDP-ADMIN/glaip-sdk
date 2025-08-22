# 03 Agent Workflow Orchestration - CLI Example

## 🎯 Goal
Demonstrate how to use the AIP CLI to create and coordinate multiple agents working together in a simple workflow. Show basic agent delegation and coordination patterns suitable for MVP implementations.

## ⏱️ Estimated Time
8-10 minutes

## 📋 Prerequisites
- AIP CLI installed and configured (`aip init`)
- Backend services running
- Valid API credentials
- Understanding of basic agent and tool operations

## 🚀 Run

### Phase 1: Setup and Tool Creation

#### 1.1 Create Calculation Tool
```bash
# Create a simple calculation tool file
cat > calculation_tool.py << 'EOF'
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

def calculate_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle."""
    return length * width
EOF

# Create the tool using the CLI
aip tools create \
  --file calculation_tool.py \
  --name "calculation_tool" \
  --description "Simple mathematical operations for workflow demonstration"
```

#### 1.2 Verify Tool Creation
```bash
# List all tools to confirm creation
aip tools list

# Get detailed information about the tool
aip tools get <TOOL_ID>

# Note the tool ID for later use
TOOL_ID="<TOOL_ID>"
```

### Phase 2: Create Specialized Agents

#### 2.1 Create Math Specialist Agent
```bash
# Create a math specialist agent
aip agents create \
  --name "math_specialist" \
  --instructions "You are a math specialist agent. You excel at mathematical calculations and always show your work step by step. Use your calculation tools when performing math operations." \
  --tools $TOOL_ID
```

#### 2.2 Create Workflow Coordinator Agent
```bash
# Create a workflow coordinator agent
aip agents create \
  --name "workflow_coordinator" \
  --instructions "You are a workflow coordinator. You can delegate mathematical tasks to the math specialist agent. Always explain your workflow and coordinate between different agents when needed." \
  --agents <MATH_AGENT_ID>
```

#### 2.3 Verify Agent Creation
```bash
# List all agents to confirm creation
aip agents list

# Get detailed information about both agents
aip agents get <MATH_AGENT_ID>
aip agents get <COORDINATOR_AGENT_ID>

# Note the agent IDs for later use
MATH_AGENT_ID="<MATH_AGENT_ID>"
COORDINATOR_AGENT_ID="<COORDINATOR_AGENT_ID>"
```

### Phase 3: Test Basic Workflow

#### 3.1 Test Math Specialist Directly
```bash
# Test the math specialist with a simple calculation
aip agents run $MATH_AGENT_ID \
  --input "Please calculate 15 + 27 and show your work"
```

#### 3.2 Test Basic Coordination
```bash
# Test the workflow coordinator with a simple delegation
aip agents run $COORDINATOR_AGENT_ID \
  --input "I need to calculate 23 * 17. Please coordinate with your math specialist to get this done."
```

### Phase 4: Test Complex Workflow

#### 4.1 Test Area Calculation Workflow
```bash
# Test with a more complex mathematical problem
aip agents run $COORDINATOR_AGENT_ID \
  --input "I need to calculate the area of a rectangle that is 8.5 meters long and 6.2 meters wide. Please coordinate with your math specialist to get this done and explain the workflow."
```

#### 4.2 Test Multi-Step Problem
```bash
# Test with a multi-step mathematical workflow
aip agents run $COORDINATOR_AGENT_ID \
  --input "I need to solve this problem: A rectangular garden has a length of 12 meters and a width of 8 meters. I want to add a path around it that's 1 meter wide. What's the new total area? Please work through this step by step."
```

### Phase 5: Workflow Analysis

#### 5.1 Test Different View Formats
```bash
# Test workflow with rich view
aip agents run $COORDINATOR_AGENT_ID \
  --input "Explain how you coordinate with other agents" \
  --view rich

# Test workflow with JSON view for analysis
aip agents run $COORDINATOR_AGENT_ID \
  --input "Show me your coordination workflow" \
  --view json
```

#### 5.2 Test Workflow Variations
```bash
# Test with different types of mathematical problems
aip agents run $COORDINATOR_AGENT_ID \
  --input "Please help me calculate: (15 + 7) * (23 - 8) / 5. Show the complete workflow."

# Test delegation with multiple steps
aip agents run $COORDINATOR_AGENT_ID \
  --input "I need to calculate the perimeter and area of a rectangle with length 10m and width 6m. Please coordinate this with your math specialist."
```

### Phase 6: Cleanup and Verification

#### 6.1 Cleanup Resources
```bash
# Delete the workflow coordinator agent
aip agents delete $COORDINATOR_AGENT_ID

# Delete the math specialist agent
aip agents delete $MATH_AGENT_ID

# Delete the calculation tool
aip tools delete $TOOL_ID

# Remove test files
rm -f calculation_tool.py
```

#### 6.2 Final Verification
```bash
# Verify cleanup
aip agents list
aip tools list

# Check final status
aip status
```

## 📤 Expected Output

### Tool Creation
```bash
✅ Tool created successfully: calculation_tool (ID: 123e4567-e89b-12d3-a456-426614174000)
```

### Agent Creation
```bash
✅ Agent created successfully: math_specialist (ID: 987fcdef-1234-5678-9abc-def123456789)
✅ Agent created successfully: workflow_coordinator (ID: abc12345-6789-def0-1234-567890abcdef)
```

### Math Specialist Response
```bash
I'll calculate 15 + 27 for you.

Using my calculation tool:
15 + 27 = 42

The result is 42. This demonstrates how I can use my mathematical tools to perform calculations accurately.
```

### Workflow Coordination Response
```bash
I'll coordinate with my math specialist to calculate the area of your rectangle.

**Workflow Steps:**
1. **Task Analysis**: Calculate area of 8.5m × 6.2m rectangle
2. **Delegation**: Sending this to my math specialist agent
3. **Calculation**: Using the area formula: length × width
4. **Result**: 8.5 × 6.2 = 52.7 square meters

**Workflow Summary**: I coordinated with my math specialist to calculate the area, showing how agents can work together to solve problems efficiently.
```

### Complex Workflow Response
```bash
I'll coordinate with my math specialist to solve this multi-step problem.

**Workflow Analysis:**
1. **Original Garden**: 12m × 8m = 96 square meters
2. **Path Addition**: 1 meter wide path around the garden
3. **New Dimensions**: 14m × 10m (adding 2m total for path)
4. **New Total Area**: 14 × 10 = 140 square meters

**Coordination Process**: I delegated the mathematical calculations to my math specialist, who provided the step-by-step solution showing how the path increases the total area.
```

## 🔧 Troubleshooting

### Agent Creation Issues
- Verify the tool ID is correct and exists
- Check that agent instructions are properly formatted
- Ensure the backend supports agent-to-agent coordination
- Use `--view json` for detailed error information

### Coordination Issues
- Verify both agents exist and are accessible
- Check that the coordinator agent has the math agent in its agents list
- Ensure the math agent has access to the calculation tool
- Test each agent individually before testing coordination

### Workflow Execution Issues
- Start with simple calculations before complex workflows
- Verify that the math agent can use the calculation tool
- Check that the coordinator agent understands delegation
- Use `--view plain` for simpler output if rich view fails

## 🧹 Cleanup

The demo includes comprehensive cleanup:
- All created agents are deleted
- All created tools are removed
- Test files are cleaned up
- Final verification confirms clean state

## 💡 Key Concepts Demonstrated

1. **Agent Specialization**: Creating agents with specific expertise
2. **Tool Integration**: Agents using tools for specific tasks
3. **Agent Coordination**: Delegating tasks between agents
4. **Workflow Management**: Coordinating multi-step processes
5. **Resource Management**: Proper cleanup and verification
6. **MVP Patterns**: Simple but effective workflow orchestration

## 🔗 Related Examples

- **Getting Started**: `01_hello_world_agent.md` - Basic agent creation
- **Intermediate**: `01_conversation_memory.md` - Memory capabilities
- **Intermediate**: `02_streaming_execution.md` - Execution patterns
- **Advanced**: `02_error_handling_patterns.md` - Error handling
- **SDK**: `03_agent_workflow_orchestration.py` - Programmatic workflow management

## 🚀 Advanced Usage

### Workflow Variations
```bash
# Test different coordination patterns
aip agents run $COORDINATOR_AGENT_ID \
  --input "Please coordinate a calculation involving multiple mathematical operations"

# Test delegation with constraints
aip agents run $COORDINATOR_AGENT_ID \
  --input "Calculate the volume of a cube with side length 5m, but show your workflow"
```

### Workflow Monitoring
```bash
# Monitor agent performance
for i in {1..3}; do
  echo "Workflow test $i:"
  aip agents run $COORDINATOR_AGENT_ID \
    --input "Calculate 10^$i" \
    --view plain
  echo "---"
done
```

This example demonstrates practical agent workflow orchestration that's perfect for MVP implementations! 🤝
