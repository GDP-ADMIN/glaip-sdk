# Shared Utilities for AI Agent Platform Examples

This directory contains shared utilities that provide consistent functionality across all examples, preventing code duplication and ensuring maintainability.

## 🎯 Purpose

The shared utilities provide:
- **Consistent formatting**: Standardized output styling and formatting
- **Environment management**: Unified environment loading and validation
- **Runtime utilities**: Cleanup registration, timeout handling, and performance measurement
- **Code reuse**: Common functionality that can be imported by any example

## 📁 Structure

```
_shared/
├── __init__.py          # Main package exports
├── env.py               # Environment utilities
├── printing.py          # Output formatting utilities
├── runtime.py           # Runtime management utilities
└── README.md            # This file
```

## 🚀 Quick Start

### Basic Import
```python
from examples._shared import h1, step, ok, load_env, RUN_ID
```

### Environment Setup
```python
# Load and validate environment
load_env()

# Check specific variables
from examples._shared import require
require("AIP_API_URL", "AIP_API_KEY")
```

### Output Formatting
```python
from examples._shared import h1, h2, step, ok, fail

h1("Main Title")
h2("Section Title")
step("Performing operation...")
ok("Operation completed successfully")
fail("Operation failed")
```

### Runtime Management
```python
from examples._shared import register_cleanup, print_run_info

# Register cleanup function
register_cleanup(lambda: cleanup_resources(), "cleanup_resources")

# Print run information
print_run_info()
```

## 🔧 Available Utilities

### Environment Utilities (`env.py`)

#### Core Functions
- `load_env(required=("AIP_API_URL", "AIP_API_KEY))`: Load and validate environment
- `require(*keys)`: Ensure required environment variables are set
- `mask(key, value)`: Mask sensitive values in output

#### Configuration
- `EnvConfig.from_env()`: Create configuration from environment
- `validate_env_config()`: Validate and return masked configuration
- `get_env_with_default(key, default)`: Get env var with fallback

### Printing Utilities (`printing.py`)

#### Headings
- `h1(text)`: Main heading with full-width separator
- `h2(text)`: Secondary heading with medium separator
- `h3(text)`: Tertiary heading with short separator

#### Status Messages
- `step(text)`: Step in a process
- `ok(text)`: Success message
- `warn(text)`: Warning message
- `fail(text)`: Failure message
- `info(text)`: Informational message

#### Data Display
- `print_table(headers, rows, title)`: Formatted table output
- `print_json(data, title)`: JSON-formatted output
- `print_list(items, title, bullet)`: Bulleted list output
- `print_dict(data, title)`: Key-value pair output

#### Progress & Control
- `print_progress(current, total, description)`: Progress bar
- `clear_line()`: Clear current line
- `flush_output()`: Flush stdout buffer

### Runtime Utilities (`runtime.py`)

#### Core Management
- `RUN_ID`: Unique identifier for each run
- `register_cleanup(func, name)`: Register cleanup function
- `run_cleanup()`: Execute all registered cleanup functions

#### Context Managers
- `timeout_handler(seconds, message)`: Timeout handling
- `retry_handler(max_retries, base_delay, max_delay)`: Retry with backoff
- `resource_tracker(name)`: Resource creation tracking

#### Performance
- `PerformanceTimer(name)`: Execution time measurement
- `measure_time(func)`: Function timing decorator

#### Information
- `get_run_info()`: Get current run information
- `print_run_info()`: Display run information

## 📝 Usage Examples

### Complete Example Structure
```python
#!/usr/bin/env python3
"""Example using shared utilities.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples._shared import (
    h1, h2, step, ok, fail, info,
    load_env, register_cleanup, print_run_info
)
from glaip_sdk import Client


def main() -> bool:
    """Main function using shared utilities."""
    try:
        h1("Example Title")
        print_run_info()

        h2("Environment Setup")
        step("Loading environment...")
        load_env()
        ok("Environment loaded")

        h2("Main Logic")
        step("Performing operation...")
        # Your logic here
        ok("Operation completed")

        return True

    except Exception as e:
        fail(f"Example failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

### Environment Management
```python
from examples._shared import load_env, EnvConfig, mask

# Load environment
load_env()

# Get configuration
config = EnvConfig.from_env()
print(f"API URL: {config.api_url}")
print(f"API Key: {mask('AIP_API_KEY', config.api_key)}")
```

### Cleanup Registration
```python
from examples._shared import register_cleanup

# Register cleanup for resources
register_cleanup(
    lambda: client.delete_agent(agent.id),
    f"delete_agent_{agent.id}"
)

# Cleanup runs automatically on exit
```

### Performance Measurement
```python
from examples._shared import PerformanceTimer, measure_time

# Using context manager
with PerformanceTimer("API Call"):
    response = client.call_api()

# Using decorator
@measure_time
def slow_function():
    time.sleep(2)
```

## 🔒 Best Practices

### 1. Always Import from `_shared`
```python
# ✅ Good
from examples._shared import h1, step, ok

# ❌ Bad - direct imports
from examples._shared.printing import h1
```

### 2. Use Consistent Naming
```python
# ✅ Good - consistent with shared utilities
h1("Main Title")
h2("Section Title")
step("Performing operation...")
ok("Operation completed")

# ❌ Bad - inconsistent formatting
print("Main Title")
print("Section Title")
print("Performing operation...")
print("Operation completed")
```

### 3. Register Cleanup Functions
```python
# ✅ Good - automatic cleanup
register_cleanup(lambda: cleanup(), "cleanup")

# ❌ Bad - manual cleanup
# User must remember to call cleanup()
```

### 4. Handle Errors Gracefully
```python
# ✅ Good - proper error handling
try:
    operation()
    ok("Operation successful")
except Exception as e:
    fail(f"Operation failed: {e}")
    return False
```

## 🚨 Error Handling

The shared utilities include comprehensive error handling:

- **Environment errors**: Clear messages for missing variables
- **Import errors**: Graceful fallbacks for optional dependencies
- **Runtime errors**: Proper cleanup on failures
- **Signal handling**: Graceful shutdown on interrupts

## 🔄 Updates and Maintenance

When updating shared utilities:

1. **Test all examples**: Ensure no examples break
2. **Update documentation**: Keep this README current
3. **Maintain backward compatibility**: Don't break existing imports
4. **Add tests**: Include tests for new functionality

## 📚 Related Documentation

- [Examples README](../README.md) - Main examples documentation
- [CLI Testing Scenario](../../CLI_TESTING_SCENARIO.md) - CLI usage examples
- [SDK Documentation](../../docs/) - SDK API reference
