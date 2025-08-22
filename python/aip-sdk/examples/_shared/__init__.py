"""Shared utilities for AI Agent Platform examples.

This package provides common functionality used across multiple examples
to ensure consistency and prevent code duplication.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from .env import (
    EnvConfig,
    get_env_with_default,
    load_env,
    mask,
    require,
    validate_env_config,
)
from .printing import (
    blank_line,
    clear_line,
    code,
    data,
    fail,
    flush_output,
    h1,
    h2,
    h3,
    info,
    ok,
    print_dict,
    print_json,
    print_list,
    print_progress,
    print_table,
    separator,
    step,
    warn,
)
from .runtime import (
    RUN_ID,
    PerformanceTimer,
    get_run_info,
    measure_time,
    print_run_info,
    register_cleanup,
    resource_tracker,
    retry_handler,
    timeout_handler,
)

__all__ = [
    "load_env",
    "require",
    "mask",
    "EnvConfig",
    "validate_env_config",
    "get_env_with_default",
    "h1",
    "h2",
    "h3",
    "step",
    "ok",
    "warn",
    "fail",
    "info",
    "code",
    "data",
    "separator",
    "blank_line",
    "print_table",
    "print_json",
    "print_list",
    "print_dict",
    "print_progress",
    "clear_line",
    "flush_output",
    "RUN_ID",
    "register_cleanup",
    "timeout_handler",
    "retry_handler",
    "resource_tracker",
    "get_run_info",
    "print_run_info",
    "PerformanceTimer",
    "measure_time",
]
