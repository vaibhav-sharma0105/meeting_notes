import yaml
import os
from typing import Dict, Any

class Settings:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            # Fallback for when running from root or different dir
            if os.path.exists(os.path.join("backend", self.config_path)):
                self.config_path = os.path.join("backend", self.config_path)
            else:
                raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)

        return config

    def get_llm_config(self) -> Dict[str, Any]:
        """
        Returns the LiteLLM configuration for the selected model.
        Resolves 'os.environ/VAR_NAME' to actual environment variables.
        """
        selected_model = self._config.get("selected_model")
        if not selected_model:
            raise ValueError("No 'selected_model' defined in config.yaml")

        model_config = self._config.get("models", {}).get(selected_model)
        if not model_config:
            raise ValueError(f"Model '{selected_model}' not found in 'models' section")

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
