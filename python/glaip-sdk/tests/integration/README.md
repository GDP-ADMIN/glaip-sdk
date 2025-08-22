# Integration Tests

This directory contains integration tests that require a running backend to test actual API interactions.

## Test Structure

```
tests/integration/
├── sdk/                    # SDK integration tests
│   ├── test_agent_integration.py      # Agent lifecycle and operations
│   ├── test_tool_integration.py       # Tool management and operations
│   ├── test_mcp_integration.py        # MCP lifecycle and operations
│   ├── test_workflow_integration.py   # End-to-end workflows
│   ├── test_sdk_integration.py        # Core SDK functionality
│   ├── test_basic_integration.py      # Basic connectivity and operations
│   ├── test_resource_management.py    # Resource lifecycle and cleanup patterns
│   └── test_authentication_patterns.py # Authentication and security testing
├── cli/                    # CLI integration tests
│   ├── test_cli_agents.py             # CLI agent commands
│   ├── test_cli_tools.py              # CLI tool commands
│   ├── test_cli_mcps.py               # CLI MCP commands
│   ├── test_cli_models.py             # CLI language model commands
│   └── test_cli_workflows.py          # CLI workflow commands
├── test_helpers.py         # Shared SDK test helper functions
├── cli_test_helpers.py     # Shared CLI test helper functions
└── README.md               # This file
```

## Test Categories

### SDK Tests (`@pytest.mark.sdk`)
Test the Python SDK client functionality:
- **Agent Management**: Create, read, update, delete, search, run
- **Tool Management**: Upload, list, get, update, delete
- **MCP Management**: Create, configure, connect, manage tools
- **Workflows**: End-to-end scenarios, concurrent operations
- **Error Handling**: Validation, authentication, server errors
- **Resource Management**: Lifecycle patterns, cleanup strategies, resource isolation
- **Authentication**: Security patterns, credential management, audit logging

### CLI Tests (`@pytest.mark.cli`)
Test the command-line interface:
- **Command Execution**: All CLI subcommands and options
- **Output Formats**: JSON and rich output modes
- **Error Handling**: Invalid inputs, missing resources
- **Workflows**: Multi-step CLI operations
- **Configuration**: Environment variables, config files

## Helper Modules

### `test_helpers.py` - SDK Test Helpers
Provides common functionality for SDK integration tests:

- **Environment Management**: `get_test_environment()`, `create_test_client()`
- **Resource Management**: `ResourceManager`, `TestResourceContext`
- **Test Data Generation**: `generate_test_name()`, `create_test_tool_file()`
- **Resource Creation**: `create_test_agent()`, `create_test_tool()`, `create_test_mcp()`
- **Validation Helpers**: `assert_agent_created()`, `assert_tool_created()`
- **Error Testing**: `assert_raises_not_found()`, `assert_raises_validation_error()`
- **Utilities**: `retry_on_failure()`, `check_backend_health()`

### `cli_test_helpers.py` - CLI Test Helpers
Provides common functionality for CLI integration tests:

- **CLI Execution**: `run_cli_command()`, `run_cli_command_success()`
- **Output Validation**: `assert_cli_output_contains()`, `assert_json_output_valid()`
- **Resource Management**: `CLITestResourceManager`, `CLITestContext`
- **Resource Creation**: `create_cli_test_agent()`, `create_cli_test_tool()`
- **Error Testing**: `test_cli_error_handling()`, `assert_cli_failure()`
- **Format Testing**: `test_cli_output_formats()`
- **Health Checks**: `check_cli_health()`, `ensure_cli_healthy()`

## Running Tests

### Prerequisites
- Backend services must be running
- Environment variables set:
  - `AIP_API_KEY`: Your API key
  - `AIP_API_URL`: Backend API URL

### Run All Integration Tests
```bash
pytest tests/integration/ -m integration
```

### Run SDK Tests Only
```bash
pytest tests/integration/sdk/ -m sdk
```

### Run CLI Tests Only
```bash
pytest tests/integration/cli/ -m cli
```

### Run Specific Test Categories
```bash
# Agent-related tests
pytest tests/integration/sdk/test_agent_integration.py -m sdk
pytest tests/integration/cli/test_cli_agents.py -m cli

# Tool-related tests
pytest tests/integration/sdk/test_tool_integration.py -m sdk
pytest tests/integration/cli/test_cli_tools.py -m cli

# MCP-related tests
pytest tests/integration/sdk/test_mcp_integration.py -m sdk
pytest tests/integration/cli/test_cli_mcps.py -m cli
```

### Run with Verbose Output
```bash
pytest tests/integration/ -m integration -v
```

### Run with Coverage
```bash
pytest tests/integration/ -m integration --cov=glaip_sdk --cov-report=html
```

## Test Markers

- `@pytest.mark.integration`: All integration tests
- `@pytest.mark.sdk`: SDK client functionality tests
- `@pytest.mark.cli`: Command-line interface tests

## Test Isolation

Each test class:
- Creates unique test resources with UUID-based names
- Cleans up resources in `teardown_method`
- Uses isolated test data to avoid conflicts
- Handles cleanup failures gracefully

## Environment Setup

Tests automatically:
- Load environment variables from `.env` files
- Skip if required environment variables are missing
- Use test-specific resource naming to avoid conflicts
- Clean up test resources after each test

## Debugging Tests

### Run Single Test
```bash
pytest tests/integration/sdk/test_agent_integration.py::TestAgentIntegration::test_create_and_delete_agent -v
```

### Run with Print Output
```bash
pytest tests/integration/ -m integration -s
```

### Run with Maximum Verbosity
```bash
pytest tests/integration/ -m integration -vvv
```

## Adding New Tests

### SDK Tests
1. Create test file in `tests/integration/sdk/`
2. Use `@pytest.mark.integration` and `@pytest.mark.sdk`
3. Import and use helper functions from `test_helpers.py`
4. Use `ResourceManager` or `TestResourceContext` for automatic cleanup
5. Inherit from existing test patterns

### CLI Tests
1. Create test file in `tests/integration/cli/`
2. Use `@pytest.mark.integration` and `@pytest.mark.cli`
3. Import and use helper functions from `cli_test_helpers.py`
4. Use `CLITestResourceManager` or `CLITestContext` for automatic cleanup
5. Test both success and error scenarios

### Test Naming Convention
- Test files: `test_<feature>_integration.py`
- Test classes: `Test<Feature>Integration`
- Test methods: `test_<specific_scenario>`

## Using Helper Modules

### SDK Test Example
```python
from test_helpers import create_test_agent, assert_agent_created

def test_agent_creation(self):
    # Create agent with automatic cleanup
    agent, resource_manager = create_test_agent(
        self.client,
        name="test-agent",
        instructions="Test instructions"
    )

    # Assertions
    assert_agent_created(agent, "test-agent")

    # Cleanup is automatic via resource_manager
```

### CLI Test Example
```python
from cli_test_helpers import create_cli_test_agent, assert_cli_success

def test_cli_agent_creation(self):
    # Create agent via CLI with automatic cleanup
    agent_name, resource_manager = create_cli_test_agent(
        name="test-cli-agent",
        instructions="Test instructions"
    )

    # Verify creation
    result = run_cli_command(["agents", "get", agent_name])
    assert_cli_success(result)

    # Cleanup is automatic via resource_manager
```

### Resource Management Patterns
```python
# Using context manager
with TestResourceContext(self.client) as resources:
    agent = self.client.create_agent(name="test", instructions="test")
    resources.add_agent(agent.id)
    # Resources automatically cleaned up when context exits

# Using decorator
@with_resource_cleanup
def test_with_cleanup(self, resource_manager):
    agent = self.client.create_agent(name="test", instructions="test")
    resource_manager.add_agent(agent.id)
    # Resources automatically cleaned up after function completes
```

## Common Patterns

### Resource Creation
```python
def test_create_resource(self):
    resource_name = f"{self.test_prefix}-resource"
    result = self._run_cli_command(["create", resource_name])
    assert result.returncode == 0
    self.created_resources.append(("type", resource_name))
```

### Resource Cleanup
```python
def teardown_method(self):
    for resource_type, resource_name in self.created_resources:
        try:
            self._run_cli_command([resource_type, "delete", resource_name])
        except Exception:
            pass  # Cleanup failures shouldn't fail tests
```

### Error Testing
```python
def test_error_handling(self):
    with pytest.raises(Exception):
        self.client.get_resource("non-existent-id")
```
