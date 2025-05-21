"""
Configuration settings for the Unity MCP Server.
This file contains all configurable parameters for the server.
"""

from dataclasses import dataclass
import json
import os
import logging

@dataclass
class ServerConfig:
    """Main configuration class for the MCP server."""
    
    # Network settings
    unity_host: str = "localhost"
    unity_port: int = 6400
    mcp_port: int = 6500
    
    # Connection settings
    connection_timeout: float = 86400.0  # 24 hours timeout
    buffer_size: int = 16 * 1024 * 1024  # 16MB buffer
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Server settings
    max_retries: int = 3
    retry_delay: float = 1.0

# Create a global config instance
config = ServerConfig()


def _load_config_from_file(path: str) -> None:
    """Load configuration overrides from a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "unity_port" in data:
            config.unity_port = int(data["unity_port"])
    except Exception as e:
        logging.warning(f"Failed to load config file {path}: {e}")


def _apply_environment_overrides() -> None:
    """Override configuration from environment variables if present."""
    env_port = os.getenv("UNITY_MCP_PORT")
    if env_port:
        try:
            config.unity_port = int(env_port)
            return
        except ValueError:
            logging.warning(f"Invalid UNITY_MCP_PORT value: {env_port}")

    config_path = os.getenv("UNITY_MCP_CONFIG")
    if config_path and os.path.exists(config_path):
        _load_config_from_file(config_path)
    else:
        default_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(default_path):
            _load_config_from_file(default_path)


_apply_environment_overrides()
