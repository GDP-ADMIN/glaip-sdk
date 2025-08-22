"""Environment utilities for AI Agent Platform examples.

Provides consistent environment loading, validation, and masking functionality
across all examples.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import os
from dataclasses import dataclass
from typing import Any

# Keys that should be masked in output
MASK_KEYS = {
    "AIP_API_KEY",
    "AIP_SECRET_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_API_VERSION",
}


def mask(key: str, value: str | None) -> str:
    """Mask sensitive values in output.

    Args:
        key: Environment variable name
        value: Environment variable value

    Returns:
        Masked value if key is sensitive, original value otherwise
    """
    if key in MASK_KEYS and value:
        return "****"
    return value


def require(*keys: str) -> None:
    """Require environment variables to be set.

    Args:
        *keys: Environment variable names that must be set

    Raises:
        RuntimeError: If any required environment variables are missing
    """
    missing = [k for k in keys if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Please check your .env file or environment configuration."
        )


def load_env(required: tuple[str, ...] = ("AIP_API_URL", "AIP_API_KEY")) -> None:
    """Load environment variables from .env file and validate required ones.

    Args:
        required: Tuple of required environment variable names

    Raises:
        RuntimeError: If required environment variables are missing
    """
    # Try to load from .env file
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        # python-dotenv not available, continue with system env
        pass
    except Exception:
        # Other errors loading .env, continue with system env
        pass

    # Validate required environment variables
    require(*required)


def get_env_with_default(key: str, default: str | None = None) -> str | None:
    """Get environment variable with optional default.

    Args:
        key: Environment variable name
        default: Default value if not set

    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default)


def validate_env_config() -> dict[str, Any]:
    """Validate and return current environment configuration.

    Returns:
        Dictionary with environment configuration (sensitive values masked)

    Raises:
        RuntimeError: If required environment variables are missing
    """
    # Load and validate environment
    load_env()

    # Build configuration dict with masking
    config = {}
    for key in ["AIP_API_URL", "AIP_API_KEY", "AIP_ORG_ID", "AIP_PROJECT_ID"]:
        value = os.getenv(key)
        if value:
            config[key] = mask(key, value)
        else:
            config[key] = None

    # Add optional configuration
    optional_keys = [
        "AIP_TIMEOUT",
        "AIP_RETRY_MAX",
        "AIP_TLS_VERIFY",
        "AIP_CA_BUNDLE",
        "AIP_CONCURRENCY",
        "AIP_DEFAULT_MODEL",
    ]

    for key in optional_keys:
        value = os.getenv(key)
        if value:
            config[key] = value
        else:
            config[key] = None

    return config


@dataclass
class EnvConfig:
    """Environment configuration container."""

    api_url: str
    api_key: str
    org_id: str | None = None
    project_id: str | None = None
    timeout: float = 30.0
    retry_max: int = 3
    tls_verify: bool = True
    ca_bundle: str | None = None
    concurrency: int = 4
    default_model: str | None = None

    @classmethod
    def from_env(cls) -> "EnvConfig":
        """Create EnvConfig from environment variables.

        Returns:
            EnvConfig instance with current environment values

        Raises:
            RuntimeError: If required environment variables are missing
        """
        load_env()

        return cls(
            api_url=os.getenv("AIP_API_URL", ""),
            api_key=os.getenv("AIP_API_KEY", ""),
            org_id=os.getenv("AIP_ORG_ID"),
            project_id=os.getenv("AIP_PROJECT_ID"),
            timeout=float(os.getenv("AIP_TIMEOUT", "30.0")),
            retry_max=int(os.getenv("AIP_RETRY_MAX", "3")),
            tls_verify=os.getenv("AIP_TLS_VERIFY", "true").lower() == "true",
            ca_bundle=os.getenv("AIP_CA_BUNDLE"),
            concurrency=int(os.getenv("AIP_CONCURRENCY", "4")),
            default_model=os.getenv("AIP_DEFAULT_MODEL"),
        )
