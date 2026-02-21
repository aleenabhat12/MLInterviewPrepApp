"""Persistent settings manager for the mobile app.

Settings are stored as JSON in Kivy's ``user_data_dir`` so they survive
app restarts on Android/iOS.  When running on the desktop during
development the file lives next to ``main.py`` instead.
"""

import json
import os

_SETTINGS_FILE = "ml_prep_settings.json"

_DEFAULTS = {
    # Active provider: "azure" | "openai" | "ollama"
    "ai_provider": "azure",
    # Azure OpenAI
    "azure_openai_endpoint": "",
    "azure_openai_api_key": "",
    "azure_openai_deployment": "",
    "azure_openai_api_version": "2024-08-01-preview",
    # OpenAI (api.openai.com)
    "openai_api_key": "",
    "openai_model": "gpt-4o-mini",
    # Ollama (local)
    "ollama_base_url": "http://localhost:11434",
    "ollama_model": "llama3.1",
}


def _settings_path() -> str:
    """Return the path to the settings JSON file."""
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and app.user_data_dir:
            return os.path.join(app.user_data_dir, _SETTINGS_FILE)
    except Exception:
        pass
    # Fallback for early/dev use: same directory as this file
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), _SETTINGS_FILE)


def load_settings() -> dict:
    """Load settings from disk, returning defaults for missing keys."""
    path = _settings_path()
    data = dict(_DEFAULTS)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            data.update({k: v for k, v in saved.items() if k in _DEFAULTS})
        except Exception:
            pass
    return data


def save_settings(settings: dict) -> None:
    """Persist *settings* dict to disk."""
    path = _settings_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    to_save = {k: settings.get(k, _DEFAULTS[k]) for k in _DEFAULTS}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(to_save, f, indent=2)


def apply_settings(settings: dict) -> None:
    """Push *settings* values into the live ``config`` module so that
    ``question_generator`` picks them up immediately."""
    import config
    config.AI_PROVIDER              = settings.get("ai_provider", "azure")
    config.AZURE_OPENAI_ENDPOINT    = settings.get("azure_openai_endpoint", "")
    config.AZURE_OPENAI_API_KEY     = settings.get("azure_openai_api_key", "")
    config.AZURE_OPENAI_DEPLOYMENT  = settings.get("azure_openai_deployment", "")
    config.AZURE_OPENAI_API_VERSION = settings.get("azure_openai_api_version",
                                                    "2024-08-01-preview")
    config.OPENAI_API_KEY           = settings.get("openai_api_key", "")
    config.OPENAI_MODEL             = settings.get("openai_model", "gpt-4o-mini")
    config.OLLAMA_BASE_URL          = settings.get("ollama_base_url", "http://localhost:11434")
    config.OLLAMA_MODEL             = settings.get("ollama_model", "llama3.1")


def is_configured(settings: dict | None = None) -> bool:
    """Return True if the minimum required settings for the active provider are present."""
    if settings is None:
        settings = load_settings()
    provider = settings.get("ai_provider", "azure")
    if provider == "openai":
        return bool(settings.get("openai_api_key") and settings.get("openai_model"))
    if provider == "ollama":
        return bool(settings.get("ollama_base_url") and settings.get("ollama_model"))
    # azure
    return bool(settings.get("azure_openai_endpoint") and
                settings.get("azure_openai_api_key") and
                settings.get("azure_openai_deployment"))
