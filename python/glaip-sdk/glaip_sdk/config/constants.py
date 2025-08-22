"""Configuration constants for the AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

# Default language model configuration
DEFAULT_MODEL = "gpt-4.1"
DEFAULT_MODEL_PROVIDER = "openai"

# Default timeout values
DEFAULT_TIMEOUT = 30.0
DEFAULT_AGENT_TIMEOUT = 300.0

# User agent
SDK_NAME = "glaip-sdk"
SDK_VERSION = "0.1.0"

# Reserved names that cannot be used for agents/tools
RESERVED_NAMES = {
    "system",
    "admin",
    "root",
    "test",
    "example",
    "demo",
    "sample",
}
