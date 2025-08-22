# 🚀 AI Agent Platform SDK Examples

This directory contains comprehensive examples demonstrating how to use the AI Agent Platform SDK and CLI. Examples are organized by complexity and interface type to provide a clear learning path.

## 📁 Directory Structure

```
examples/
├── README.md                    # This file
├── env.example                  # Environment configuration template
├── run_examples.py             # Examples runner and discovery tool
├── getting-started/            # Basic examples for beginners
│   ├── sdk/                    # Python SDK examples
│   │   ├── 01_hello_world_agent.py
│   │   ├── 02_hello_world_tool.py
│   │   └── 03_hello_world_mcp.py
│   └── cli/                    # CLI command examples (Markdown)
│       ├── 01_hello_world_agent.md
│       ├── 02_hello_world_tool.md
│       └── 03_basic_agent_tool.md
├── intermediate/               # Moderate complexity examples
│   ├── sdk/                    # Python SDK examples
│   └── cli/                    # CLI command examples
├── advanced/                   # Complex scenarios for experienced users
│   ├── sdk/                    # Python SDK examples
│   │   └── sdk_sub_agent_lifecycle.py
│   └── cli/                    # CLI command examples
└── demos/                      # Complete workflow demonstrations
    ├── sdk/                    # Python SDK examples
    └── cli/                    # CLI command examples
```

## 🎯 Getting Started

### Prerequisites

1. **Backend Services**: Ensure your AI Agent Platform backend is running
   ```bash
   cd applications/ai-agent-platform-backend
   docker-compose up -d
   ```

2. **Environment Setup**: Copy and configure environment variables
   ```bash
   cp examples/env.example examples/.env
   # Edit .env with your actual API credentials
   ```

3. **Dependencies**: Install Python dependencies
   ```bash
   poetry install
   ```

### Quick Start

1. **List all examples**:
   ```bash
   python examples/run_examples.py
   ```

2. **Run a specific example**:
   ```bash
   poetry run python examples/getting-started/sdk/01_hello_world_agent.py
   ```

3. **Test all SDK examples** (dry run):
   ```bash
   python examples/run_examples.py --run-sdk --dry-run
   ```

## 🔧 Example Categories

### Getting Started (`getting-started/`)
- **01_hello_world_agent.py**: Create and run a simple AI agent
- **02_hello_world_tool.py**: Create and use a custom tool
- **03_hello_world_mcp.py**: Set up a basic MCP server

### Intermediate (`intermediate/`)
- Agent collaboration patterns
- Tool integration workflows
- Error handling and validation

### Advanced (`advanced/`)
- **sdk_sub_agent_lifecycle.py**: Complex multi-agent delegation system
- Advanced tool chaining
- Performance optimization techniques

### Demos (`demos/`)
- End-to-end workflow demonstrations
- Real-world use case implementations
- Integration examples with external systems

## 📚 Example Format

Each SDK example follows a consistent structure:

```python
#!/usr/bin/env python3
"""filename.py - Example Description

Goal: Clear description of what the example demonstrates
Estimated time: Expected completion time
Prerequisites: Required setup and dependencies
Run: Command to execute the example
Cleanup: How resources are managed

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

def main():
    """Main function with clear step-by-step execution."""
    # Implementation here
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

## 🎨 CLI Examples

CLI examples are provided as Markdown files with:
- Copy-pasteable commands
- Expected output snippets
- Step-by-step explanations
- Troubleshooting tips

## 🧪 Testing Examples

### Individual Testing
```bash
# Test a specific example
python examples/getting-started/sdk/01_hello_world_agent.py

# Test with verbose output
python -v examples/getting-started/sdk/01_hello_world_agent.py
```

### Batch Testing
```bash
# Test all examples (import only)
python examples/run_examples.py --run-sdk --dry-run

# Test all examples (full execution)
python examples/run_examples.py --run-sdk
```

### CI Integration
Examples are automatically tested in CI to ensure they remain functional:
- Import validation
- Basic execution testing
- Resource cleanup verification

## 🔍 Troubleshooting

### Common Issues

1. **Environment Variables Not Set**
   ```bash
   ❌ Environment variables not set!
   # Solution: Copy and configure env.example
   cp examples/env.example examples/.env
   ```

2. **Backend Connection Failed**
   ```bash
   ❌ Error: Connection refused
   # Solution: Start backend services
   docker-compose up -d
   ```

3. **Import Errors**
   ```bash
   ❌ ModuleNotFoundError: No module named 'glaip_sdk'
   # Solution: Install dependencies
   poetry install
   ```

### Getting Help

- Check the [main README](../../README.md) for setup instructions
- Review [SDK documentation](../../docs/) for API references
- Open an issue for bugs or feature requests

## 🚀 Contributing

### Adding New Examples

1. **Follow the naming convention**: `XX_description.py` (numbered ordering)
2. **Include consistent headers**: Goal, time, prerequisites, run, cleanup
3. **Add proper error handling**: Check environment, validate inputs
4. **Include cleanup logic**: Always clean up created resources
5. **Test thoroughly**: Ensure examples work in different environments

### Example Guidelines

- **Keep it simple**: Focus on one concept per example
- **Be explicit**: Clear step-by-step execution
- **Handle errors**: Provide helpful error messages
- **Clean up**: Always remove test resources
- **Document**: Clear docstrings and comments

## 📖 Related Documentation

- [SDK API Reference](../../docs/)
- [CLI Commands](../../docs/cli.md)
- [Architecture Overview](../../AI_AGENT_PLATFORM_ARCHITECTURE_DIAGRAMS.md)
- [Development Guide](../../AIP_SDK_DEVELOPMENT_GUIDE.md)

## 🔄 Version Compatibility

| SDK Version | Examples Version | Backend Version | Notes |
|-------------|------------------|-----------------|-------|
| 0.1.0       | 1.0.0           | 0.1.0+         | Initial release |
| 0.2.0       | 1.1.0           | 0.2.0+         | Enhanced examples |

---

**Happy coding! 🎉** If you have questions or suggestions, please open an issue or contribute to the examples.
