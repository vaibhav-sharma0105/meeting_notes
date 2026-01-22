import yaml
import os
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.config import settings

router = APIRouter(prefix="/settings", tags=["settings"])

class SettingsUpdate(BaseModel):
    selected_model: str
    embedding_model: Optional[str] = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    model_provider: str = "openai" # or ollama, etc.

class ModelFetchRequest(BaseModel):
    api_base: str
    api_key: Optional[str] = None

@router.get("/")
def get_settings():
    """
    Returns the current configuration.
    """
    # Reload config to ensure freshness
    config = settings._load_config()

    selected_model = config.get("selected_model", "gpt-4o")
    embedding_model = config.get("embedding_model", "openai/text-embedding-3-small")
    model_config = config.get("models", {}).get(selected_model, {})

    return {
        "selected_model": selected_model,
        "embedding_model": embedding_model,
        "api_base": model_config.get("api_base", "https://api.openai.com/v1"),
        "api_key": "*****" if model_config.get("api_key") else "",
        "current_config_dump": config # For debug/MVP
    }

@router.post("/")
def update_settings(update: SettingsUpdate):
    """
    Updates the config.yaml file.
    Note: In a real prod app, we might update a DB or ENV, but user asked for config update.
    """
    try:
        # Load current
        config = settings._load_config()

        # We will create a new entry in 'models' or update the existing one
        model_alias = update.selected_model

        # Construct the model config
        new_model_config = {
            "model": f"{update.model_provider}/{update.selected_model}",
        }

        if update.api_base:
            new_model_config["api_base"] = update.api_base

        if update.api_key and update.api_key != "*****":
            new_model_config["api_key"] = update.api_key
        elif update.api_key == "*****":
            # Keep existing key if user didn't change it
            existing = config.get("models", {}).get(model_alias, {})
            if "api_key" in existing:
                new_model_config["api_key"] = existing["api_key"]

        # Update config object
        config["selected_model"] = model_alias
        if update.embedding_model:
            config["embedding_model"] = update.embedding_model

        if "models" not in config:
            config["models"] = {}
        config["models"][model_alias] = new_model_config

        # Write back to yaml
        with open(settings.config_path, "w") as f:
            yaml.dump(config, f)

        # Reload in memory
        settings._config = config

        return {"status": "updated", "config": config}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fetch-models")
def fetch_available_models(req: ModelFetchRequest):
    """
    Tries to fetch models from the provider.
    Works for OpenAI-compatible endpoints (Ollama, vLLM, etc).
    """
    try:
        # Clean url
        base_url = req.api_base.rstrip("/")
        if base_url.endswith("/v1"):
            url = f"{base_url}/models"
        else:
            url = f"{base_url}/v1/models"

        headers = {}
        if req.api_key:
            headers["Authorization"] = f"Bearer {req.api_key}"

        # Specific handling for Ollama if not running in standard compat mode
        # Ollama usually is localhost:11434/api/tags
        if "localhost:11434" in base_url and "/v1" not in base_url:
             url = f"{base_url}/api/tags"
             resp = requests.get(url, timeout=5)
             if resp.status_code == 200:
                 data = resp.json()
                 # Ollama format: {"models": [{"name": "llama3:latest"}]}
                 return {"models": [m["name"] for m in data.get("models", [])]}

        # Standard OpenAI format
        resp = requests.get(url, headers=headers, timeout=5)

        if resp.status_code == 200:
            data = resp.json()
            # OpenAI format: {"data": [{"id": "gpt-4"}]}
            if "data" in data:
                 return {"models": [m["id"] for m in data["data"]]}
            else:
                 return {"models": [], "raw": data}
        else:
             raise HTTPException(status_code=400, detail=f"Provider returned {resp.status_code}")

    except Exception as e:
        print(f"Fetch error: {e}")
        # Fallback/Mock for demo if connection fails
        return {
            "error": str(e),
            "models": ["gpt-4o", "gpt-3.5-turbo", "llama3", "mistral"]
        }
