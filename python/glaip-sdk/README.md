# AIP SDK — Enterprise AI Agent Platform (Python)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Build, run, and manage AI agents with a minimal, production-ready Python API.**

- **Simple**: `Client()` → create resources → `agent.run("...")`
- **Strong**: typed models (Pydantic), robust errors, clean streaming renderer
- **Enterprise-ready**: shared HTTP session, timeouts/retries, consistent resource lifecycle
- **Secure**: automatic recursive secret masking; no telemetry; TLS recommended
- **Modern CLI**: rich terminal experience, subsequence-based fuzzy search, smart paging, multiple output formats

---

## 📋 Table of Contents

- [Quick Start](#-quick-start-30-seconds)
- [Features](#-features)
- [Latest Improvements](#️-latest-improvements)
- [Use Cases & Industries](#-use-cases--industries)
- [Performance & Scalability](#-performance--scalability)
- [Core API](#core-api-in-60-seconds)
- [CLI](#cli)
- [Configuration](#configuration)
- [Learning Path](#learning-path)
- [Development](#development)
- [Error Handling](#️-error-handling)
- [Troubleshooting](#️-troubleshooting)
- [Getting Help & Support](#️-getting-help--support)
- [Why Choose AIP SDK?](#️-why-choose-aip-sdk)

---

## 🚀 Installation

> **📋 Current Status**: The AIP SDK is currently available for local development. Global installation from PyPI will be available once the package is published.

### Option 1: Local Development Setup (Recommended for developers - Available Now)

```bash
# Clone the repository
git clone <repository-url>
cd ai-agent-platform-sdk

# Install in editable mode - CLI command 'aip' will be available globally
pip install -e .

# Verify installation
aip --help
```

### Option 2: Poetry Development Setup (Alternative for Poetry users - Available Now)

```bash
# Clone the repository
git clone <repository-url>
cd ai-agent-platform-sdk

# Install dependencies and package using Poetry
poetry install

# Run CLI through Poetry (CLI not available globally)
poetry run aip --help
```

### Option 3: Global Installation from PyPI (Coming Soon)

```bash
# Install globally - CLI command 'aip' will be available everywhere
# ⚠️  This option will be available once the package is published to PyPI
pip install glaip-sdk

# Verify installation
aip --help
```

**Note**: All required dependencies including `click` and `rich` are automatically installed with the package. This resolves the previous "click and rich not installed" errors that users encountered.

## 🛠️ Local Development Setup

### Prerequisites

- **Python 3.10+** installed on your system
- **Git** for cloning the repository
- **pip** or **Poetry** for package management

### Quick Local Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd ai-agent-platform-sdk

# 2. Install in editable mode (recommended)
pip install -e .

# 3. Verify CLI is working
aip --version
aip --help

# 4. Test basic functionality
aip status
```

### Development Workflow

```bash
# After making changes to the code:
pip install -e . --force-reinstall

# Or simply reinstall:
pip install -e .

# Test your changes:
aip --version
```

### Testing Examples

```bash
# Run hello world examples
python3 examples/getting-started/sdk/01_hello_world_agent.py
python3 examples/getting-started/sdk/02_hello_world_tool.py

# List all available examples
python3 examples/run_examples.py --list
```

### Updating Local Development

```bash
# Pull latest changes
git pull origin main

# Reinstall to get latest version
pip install -e . --force-reinstall

# Verify version
aip --version

# Test new features
aip --help
```

### Troubleshooting Local Setup

#### Common Issues

**"aip command not found" after pip install -e .**
```bash
# Check if the package was installed correctly
pip list | grep glaip-sdk

# Reinstall with force flag
pip install -e . --force-reinstall

# Verify the CLI script was created
which aip
```

**Permission errors during installation**
```bash
# Use user installation (recommended)
pip install -e . --user

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

**Dependency conflicts**
```bash
# Clean install
pip uninstall glaip-sdk -y
pip install -e . --no-deps
pip install -e .
```

## ⚡ Quick Start (30 seconds)

```bash
# Option 1: Local development setup (Available Now)
git clone <repository-url>
cd ai-agent-platform-sdk
pip install -e .

# Option 2: Install globally from PyPI (Coming Soon)
# pip install glaip-sdk

export AIP_API_KEY="your-api-key"
export AIP_API_URL="https://your-platform.com/api"
```

**Python SDK:**
```python
from glaip_sdk import Client

client = Client()
agent = client.create_agent(name="hello", instruction="You are a helpful assistant.")
print(agent.run("Hello! What can you do?"))
agent.delete()
```

**CLI:**
```bash
# Configure and create your first agent
aip init
aip agents create --name "hello" --instruction "You are a helpful assistant"
aip agents run <AGENT_ID> --input "Hello! What can you do?"
aip agents delete <AGENT_ID>
```

**That's it.** You created, ran, and cleaned up your first agent. 🎉

---

## 🔧 **Connection & Timeouts**

```python
from glaip_sdk import Client

# Auto-config from environment
with Client(timeout=60.0) as client:   # shared HTTP session, closes on exit
    print(len(client.list_agents()))

# Or explicit configuration
client = Client(
    api_url="https://your-platform.com/api",
    api_key="your-key",
    timeout=120.0
)
```

---

## ✨ Features

* **Python SDK**: Simple `Client()` → create resources → `agent.run("...")`
* **CLI Interface**: Full command-line control with `aip` commands
* **Typed Models**: Pydantic-powered `Agent`, `Tool`, `MCP` with `.run()`, `.update()`, and `.delete()` methods
* **Streaming UX**: Live markdown, tool/sub-agent steps, and theme options (`AIP_THEME`, `AIP_NO_EMOJI`)
* **Shared Session**: All sub-clients share one HTTP session for reliability and performance
* **🔐 Enterprise Security**: Automatic recursive secret masking for sensitive data
* **📱 Multiple Output Formats**: Rich, JSON, Plain text, and Markdown views
* **🎯 Modern CLI Experience**: Subsequence-based fuzzy search, smart paging, and intuitive navigation
* **⚡ Performance**: Optimized HTTP sessions, connection pooling, and efficient streaming
* **🛡️ Reliability**: Comprehensive error handling, configurable timeouts, and graceful degradation
* **🔧 Developer Tools**: Rich debugging, comprehensive logging, and testing utilities

---

## 🎯 **Use Cases & Industries**

### **🚀 Development & DevOps**
- **CI/CD Automation**: Deploy agents to manage build pipelines and deployments
- **Code Review**: Automated code analysis and quality checks
- **Infrastructure Management**: Cloud resource provisioning and monitoring
- **Testing Automation**: Intelligent test generation and execution

### **💼 Business Operations**
- **Customer Support**: AI-powered customer service agents
- **Data Analysis**: Automated insights and reporting
- **Process Automation**: Streamline repetitive business workflows
- **Document Processing**: Intelligent document analysis and summarization

### **🔬 Research & Analytics**
- **Data Processing**: Automated data cleaning and transformation
- **Research Automation**: Literature review and data synthesis
- **Model Training**: Automated ML pipeline management
- **Reporting**: Dynamic report generation and insights

### **🏢 Enterprise Applications**
- **Compliance**: Automated regulatory compliance checking
- **Security**: Threat detection and incident response
- **Auditing**: Automated audit trail analysis
- **Integration**: Connect with existing enterprise systems

---

## 🚀 **Performance & Scalability**

### **⚡ High Performance**
- **Connection Pooling**: Efficient HTTP session reuse across requests
- **Streaming Responses**: Real-time data processing without memory bloat
- **Optimized Serialization**: Fast JSON parsing and response handling
- **Concurrent Operations**: Support for parallel agent execution

### **📈 Scalability Features**
- **Resource Management**: Automatic cleanup and lifecycle management
- **Memory Efficiency**: Streaming processing for large datasets
- **Timeout Handling**: Configurable timeouts for long-running operations
- **Connection Management**: Efficient HTTP session reuse and connection pooling

### **🏗️ Enterprise Architecture**
- **Microservices Ready**: Designed for distributed system integration
- **API-First Design**: RESTful endpoints with consistent patterns
- **Monitoring Support**: Built-in logging and debugging capabilities
- **Security Compliance**: Enterprise-grade security and audit features

**Security & Data Handling:**

* **🔐 Secret Masking**: Sensitive data automatically masked in JSON, Plain, and Markdown outputs
* **🔑 API Key Security**: API key read from env/config; **never logged or persisted** by default
* **📊 No Telemetry**: Zero data collection or external reporting
* **💡 Best Practice**: Use `export AIP_API_KEY="..."` instead of command-line flags

**Windows Compatibility:**

* **📄 Pager Behavior**: On Windows, automatically uses Rich's built-in pager for better ANSI support

**Interactive Features (Optional Dependencies):**

* **🔍 Fuzzy Search**: `prompt_toolkit` for intelligent subsequence-based search
* **📋 Select Menus**: `questionary` for interactive selection menus
* **🔄 Fallback Behavior**: Falls back to Rich tables when fuzzy search unavailable or non-TTY

---

## 🆕 **Latest Improvements**

### **🔐 Enhanced Security with Recursive Secret Masking**
Automatically masks sensitive fields like API keys, tokens, and secrets at all levels of nested data structures:

```bash
# Sensitive data is automatically masked in all views
aip agents get <AGENT_ID>  # API keys shown as "••••••••"
aip agents list --view json  # Recursive masking in JSON output
```

### **📱 Multiple Output Formats**
Choose your preferred output format for any command:

```bash
# Rich terminal experience (default)
aip agents list

# Clean JSON for scripting
aip agents list --view json

# Simple plain text
aip agents list --view plain

# Markdown tables
aip agents list --view md
```

### **🎯 Enhanced CLI Experience**
- **Fuzzy Search**: Intelligent search with typo tolerance
- **Smart Paging**: Automatic paging for large datasets
- **Rich Rendering**: Beautiful tables and panels with proper TTY detection

---

## Core API in 60 seconds

### Create & run an agent

```python
from glaip_sdk import Client

client = Client()
agent = client.create_agent(
    name="helper",
    instruction="You are a helpful assistant."
)
print(agent.run("Summarize why streaming is useful."))
```

### Add a tool, then use it

```python
tool = client.create_tool(
    file_path="my_tool.py",
    name="my_tool",          # Optional: extracted from file if not provided
    description="Custom business logic"  # Optional: extracted from file if not provided
)

agent = client.create_agent(
    name="tool-user",
    instruction="Use tools when helpful.",
    tools=[tool.id]
)

print(agent.run("Use the custom tool to process today's data."))
```

### Discover models

```python
for lm in client.list_language_models():
    print(lm["name"], lm["provider"])
```

### Update & delete

```python
agent.update(instruction="Be concise.")
agent.delete()
tool.delete()
```

---

## CLI

```bash
# Configure
aip init

# Agents
aip agents create --name "helper" --instruction "You are helpful"
aip agents run <AGENT_ID> --input "Hello!"
aip agents delete <AGENT_ID>

# Tools
aip tools create --file my_tool.py --name my_tool --description "Custom logic"
aip tools list

# Multiple output formats
aip agents list --view json      # JSON for scripting
aip agents list --view plain     # Simple text
aip agents list --view md        # Markdown tables
```

> Run full examples: `python -m examples`
> Getting started: `examples/getting-started/sdk/01_hello_world_agent.py`

---

## Configuration

* **Environment variables**

  ```bash
  # Copy the example file and fill in your values
  cp .env.example .env

  # Or set manually
  export AIP_API_KEY="your-api-key"
  export AIP_API_URL="https://your-platform.com/api"
  ```
* **Optional config file**: `~/.aip/config.yaml`

  ```yaml
  api_url: https://your-platform.com/api
  api_key: your-api-key
  ```

**Configuration precedence:** CLI context flags ⟶ environment variables ⟶ `~/.aip/config.yaml`
* **Renderer options**

  ```bash
  export AIP_THEME=dark        # or "light"
  export AIP_NO_EMOJI=true     # disable emojis in streaming view
  export AIP_PAGER_HEADER=0    # disable pager headers
  ```
* **Security options**

  ```bash
  export AIP_MASK_OFF=1        # disable secret masking (not recommended)
  export AIP_MASK_FIELDS="custom_field,another_secret"  # add custom fields to mask
  ```

**Environment Variables Reference:**

| Variable                  | Default | Purpose                                  |
| ------------------------- | ------- | ---------------------------------------- |
| `AIP_API_URL`             | —       | Base API endpoint                        |
| `AIP_API_KEY`             | —       | API key used for auth (never logged)     |
| `AIP_TIMEOUT`             | `30.0`  | Request timeout (s)                      |
| `AIP_THEME`               | `dark`  | Streaming code theme (`dark`/`light`)    |
| `AIP_NO_EMOJI`            | `false` | Disable emojis in the stream view        |
| `AIP_PAGER_HEADER`        | `1`     | Show pager header (`0/1`)                |
| `AIP_PAGER_WRAP`          | `0`     | Wrap lines in pager (drops `-S`)         |
| `AIP_LESS_FLAGS`          | auto    | Override default `less` flags            |
| `AIP_MASK_OFF`            | `0`     | Disable secret masking (not recommended) |
| `AIP_MASK_FIELDS`         | —       | Extra comma-separated keys to mask       |
| `AIP_TABLE_NO_SORT`       | `0`     | Disable automatic table sorting          |
* **Enterprise features**

  * Single shared HTTP session across sub-clients for reliability & connection reuse
  * Configurable timeouts and SSE streaming out of the box
  * Proxy support: `HTTP_PROXY` / `HTTPS_PROXY` supported by `httpx`
  * **Python**: 3.10–3.12
  * **Versioning**: semantic versioning; breaking changes bump MAJOR
  * **Security**: API key only read from env/config, never logged; no telemetry by default; TLS recommended

---

## Learning Path

* **Start here**

  * `examples/getting-started/sdk/01_hello_world_agent.py`
  * `examples/getting-started/sdk/02_hello_world_tool.py`
  * `examples/getting-started/sdk/03_hello_world_mcp.py`
* **Build skills**

  * `examples/intermediate/sdk/01_conversation_memory.py`
  * `examples/intermediate/sdk/02_streaming_execution.py`
  * `examples/intermediate/sdk/04_agent_tool_integration.py`
* **Go deeper**

  * `examples/advanced/sdk/01_agent_workflow_orchestration.py`
  * `examples/advanced/sdk/02_error_handling_patterns.py`
  * `examples/advanced/sdk/03_performance_optimization.py`
  * `examples/advanced/sdk/04_metadata_patterns.py`
* **SDK Testing Scenario**
  See: [`SDK_TESTING_SCENARIO.md`](SDK_TESTING_SCENARIO.md) (complete end-to-end coverage plan)

---

## Development

```bash
make install
make test-unit
make test-integration
make pre-commit
```

### Version Management

The project uses `bump2version` for automated version management. This ensures all version references are updated consistently across the codebase.

#### Quick Version Bumps

```bash
# Bump patch version (0.1.0 → 0.1.1) - for bug fixes
python scripts/bump_version.py patch

# Bump minor version (0.1.0 → 0.2.0) - for new features
python scripts/bump_version.py minor

# Bump major version (0.1.0 → 1.0.0) - for breaking changes
python scripts/bump_version.py major

# Preview changes without making them
python scripts/bump_version.py --dry-run patch
```

#### What Gets Updated

The following files are automatically updated when bumping versions:
- `pyproject.toml` - Package version
- `glaip_sdk/__init__.py` - Module version
- `glaip_sdk/cli/main.py` - CLI version display
- `glaip_sdk/config/constants.py` - SDK version constant
- `examples/__init__.py` - Examples version

#### After Version Bump

```bash
# Push changes and tags
git push --follow-tags

# Create GitHub release for the new version
# (GitHub releases will automatically use the git tag)
```

---

## 🚨 **Error Handling**

```python
from glaip_sdk import Client
from glaip_sdk.exceptions import (
    AuthenticationError, NotFoundError, ValidationError,
    RateLimitError, TimeoutError, ServerError, AIPError
)

try:
    client = Client()
    agent = client.create_agent(name="demo", instruction="...")
    print(agent.run("hello"))
except AuthenticationError:
    print("Invalid API key or insufficient permissions.")
except NotFoundError:
    print("Resource not found.")
except RateLimitError:
    print("Rate limited — retry later.")
except TimeoutError:
    print("Request timed out.")
except ValidationError as e:
    print(f"Bad request: {e}")
except ServerError as e:
    print(f"Server issue: {e}")
except AIPError as e:
    print(f"SDK error: {e}")
```

---

## 🔍 **Troubleshooting**

```bash
# Test the connection (auth header is required)
curl -s -H "X-API-Key: $AIP_API_KEY" "$AIP_API_URL/health-check"

# Verify your configuration
echo "API URL: $AIP_API_URL"
echo "API Key length: ${#AIP_API_KEY}"

# Test CLI functionality
aip --version
aip agents list --view json
```

---

## 🆘 **Getting Help & Support**

### **📚 Documentation & Examples**
- **Comprehensive Examples**: Run `python -m examples` for complete working samples
- **Getting Started**: Start with `examples/getting-started/` for basic concepts
- **Advanced Patterns**: Explore `examples/advanced/` for complex use cases
- **Testing Guide**: See `SDK_TESTING_SCENARIO.md` for testing strategies

### **🔧 Troubleshooting**
- **Connection Issues**: Check API URL and authentication
- **Performance**: Monitor timeouts and connection pooling
- **Security**: Verify secret masking and access controls
- **CLI Issues**: Test with `--view json` for debugging

### **💡 Best Practices**
- **Resource Management**: Always clean up resources with `.delete()`
- **Error Handling**: Use try-catch blocks for robust applications
- **Configuration**: Use environment variables for sensitive data
- **Testing**: Test with small datasets before scaling up

---

## 🏆 **Why Choose AIP SDK?**

* **🚀 Production Ready**: Built for enterprise with proper error handling, timeouts, and security
* **🔐 Security First**: Automatic secret masking, no sensitive data logging
* **💻 Developer Experience**: Intuitive CLI with fuzzy search and multiple output formats
* **📊 Rich Streaming**: Beautiful terminal experience with live updates and tool visualization
* **🔧 Simple API**: Minimal boilerplate, maximum functionality
* **🏗️ Enterprise Features**: Shared sessions, proxy support, comprehensive error handling

---

## License

MIT — see [LICENSE](LICENSE)
