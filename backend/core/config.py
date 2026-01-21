import yaml
import os
import sys
from typing import Dict, Any

class Settings:
    def __init__(self, config_filename: str = "config.yaml"):
        self.config_filename = config_filename
        self.config_path = self._find_config_path()
        self._config = self._load_config()

    def _find_config_path(self) -> str:
        """
        Locates config.yaml robustly across platforms and execution contexts.
        Prioritizes:
        1. Current working directory
        2. 'backend/' subdirectory (if running from root)
        3. Directory containing this file's parent (backend/core/../)
        """
        # 1. CWD
        if os.path.exists(self.config_filename):
            return os.path.abspath(self.config_filename)

        # 2. backend/ subdirectory (Running from root)
        path_in_backend = os.path.join("backend", self.config_filename)
        if os.path.exists(path_in_backend):
            return os.path.abspath(path_in_backend)

        # 3. Relative to this file (backend/core/config.py -> backend/config.yaml)
        # __file__ = backend/core/config.py
        # parent = backend/core
        # grandparent = backend
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        path_relative = os.path.join(backend_dir, self.config_filename)
        if os.path.exists(path_relative):
            return path_relative

        # If we are in backend dir already?
        return self.config_filename # Let it fail later or create new there

    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
             # Don't crash immediately, might be creating it
             print(f"Warning: Config file not found at {self.config_path}")
             return {}

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        return config if config else {}

    def get_llm_config(self) -> Dict[str, Any]:
        """
        Returns the LiteLLM configuration for the selected model.
        Resolves 'os.environ/VAR_NAME' to actual environment variables.
        """
        selected_model = self._config.get("selected_model")
        if not selected_model:
            # Fallback default if config is empty/broken
            return {"model": "gpt-3.5-turbo"}

        model_config = self._config.get("models", {}).get(selected_model)
        if not model_config:
            # Fallback
            return {"model": "gpt-3.5-turbo"}

        # Resolve environment variables
        final_config = {}
        for key, value in model_config.items():
            if isinstance(value, str) and value.startswith("os.environ/"):
                env_var = value.split("/", 1)[1]
                final_config[key] = os.environ.get(env_var)
            else:
                final_config[key] = value

        return final_config

settings = Settings()
