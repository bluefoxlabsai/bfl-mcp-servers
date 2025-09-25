"""Environment variable utilities."""

import os


def is_env_truthy(env_var: str, default: str = "false") -> bool:
    """Check if an environment variable is set to a truthy value.
    
    Args:
        env_var: The environment variable name
        default: Default value if env var is not set
        
    Returns:
        True if the environment variable is set to a truthy value
    """
    value = os.getenv(env_var, default).lower()
    return value in ("true", "1", "yes", "on")