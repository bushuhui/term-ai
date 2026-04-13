import os
import sys
from getpass import getpass
from pathlib import Path
from tempfile import gettempdir
from typing import Any

from click import UsageError

CONFIG_FOLDER = os.path.expanduser("~/.config")
SHELL_GPT_CONFIG_FOLDER = Path(CONFIG_FOLDER) / "shell_gpt"
SHELL_GPT_CONFIG_PATH = SHELL_GPT_CONFIG_FOLDER / ".sgptrc"
ROLE_STORAGE_PATH = SHELL_GPT_CONFIG_FOLDER / "roles"
FUNCTIONS_PATH = SHELL_GPT_CONFIG_FOLDER / "functions"
CHAT_CACHE_PATH = Path(gettempdir()) / "chat_cache"
CACHE_PATH = Path(gettempdir()) / "cache"

DEFAULT_CONFIG = {
    # TODO: Refactor it to CHAT_STORAGE_PATH.
    "CHAT_CACHE_PATH": os.getenv("CHAT_CACHE_PATH", str(CHAT_CACHE_PATH)),
    "CACHE_PATH": os.getenv("CACHE_PATH", str(CACHE_PATH)),
    "CHAT_CACHE_LENGTH": int(os.getenv("CHAT_CACHE_LENGTH", "100")),
    "CACHE_LENGTH": int(os.getenv("CHAT_CACHE_LENGTH", "100")),
    "REQUEST_TIMEOUT": int(os.getenv("REQUEST_TIMEOUT", "60")),
    "DEFAULT_MODEL": os.getenv("DEFAULT_MODEL", "gpt-4o"),
    "DEFAULT_COLOR": os.getenv("DEFAULT_COLOR", "magenta"),
    "ROLE_STORAGE_PATH": os.getenv("ROLE_STORAGE_PATH", str(ROLE_STORAGE_PATH)),
    "DEFAULT_EXECUTE_SHELL_CMD": os.getenv("DEFAULT_EXECUTE_SHELL_CMD", "false"),
    "DISABLE_STREAMING": os.getenv("DISABLE_STREAMING", "false"),
    "CODE_THEME": os.getenv("CODE_THEME", "dracula"),
    "OPENAI_FUNCTIONS_PATH": os.getenv("OPENAI_FUNCTIONS_PATH", str(FUNCTIONS_PATH)),
    "OPENAI_USE_FUNCTIONS": os.getenv("OPENAI_USE_FUNCTIONS", "true"),
    "SHOW_FUNCTIONS_OUTPUT": os.getenv("SHOW_FUNCTIONS_OUTPUT", "false"),
    "API_BASE_URL": "default",
    "PRETTIFY_MARKDOWN": os.getenv("PRETTIFY_MARKDOWN", "true"),
    "USE_LITELLM": os.getenv("USE_LITELLM", "false"),
    "SHELL_INTERACTION": os.getenv("SHELL_INTERACTION ", "true"),
    "OS_NAME": os.getenv("OS_NAME", "auto"),
    "SHELL_NAME": os.getenv("SHELL_NAME", "auto"),
    # New features might add their own config variables here.
}


def _do_setup(config_path: Path) -> None:
    """Run interactive setup and write config, then exit."""
    config_path.parent.mkdir(parents=True, exist_ok=True)

    print("\n=== PI Term AI Setup ===\n")
    api_url = input("Enter LLM API URL (e.g., https://api.openai.com/v1): ").strip()
    if not api_url:
        print("Error: API URL cannot be empty.")
        os._exit(1)
    model_name = input("Enter model name (e.g., gpt-4o): ").strip()
    if not model_name:
        print("Error: Model name cannot be empty.")
        os._exit(1)
    api_key = getpass(prompt="Enter API key: ")
    if not api_key:
        print("Error: API key cannot be empty.")
        os._exit(1)

    config = {**DEFAULT_CONFIG}
    config["API_BASE_URL"] = api_url
    config["DEFAULT_MODEL"] = model_name
    config["OPENAI_API_KEY"] = api_key

    with open(config_path, "w", encoding="utf-8") as file:
        for key, value in config.items():
            file.write(f"{key}={value}\n")

    print(f"\nConfig saved to: {config_path.absolute()}")
    print("Setup complete! Please run your command again.")
    os._exit(0)


def needs_setup() -> bool:
    """Check if the config is missing essential LLM settings."""
    if not SHELL_GPT_CONFIG_PATH.exists():
        return True
    temp_cfg: dict[str, str] = {}
    with open(SHELL_GPT_CONFIG_PATH, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                temp_cfg[key] = value
    return not temp_cfg.get("OPENAI_API_KEY")


def run_setup_if_needed() -> None:
    """If --setup is in sys.argv or config is missing, handle interactive setup."""
    if "--setup" not in sys.argv and not needs_setup():
        return
    config_path = SHELL_GPT_CONFIG_PATH
    if config_path.exists() and "--setup" in sys.argv:
        print(f"Config file already exists at: {config_path.absolute()}")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != "y":
            print("Setup cancelled.")
            os._exit(0)
    _do_setup(config_path)


# TODO: Refactor it to CHAT_STORAGE_PATH.
def setup_config() -> None:
    """Interactive setup to configure LLM settings."""
    config_path = SHELL_GPT_CONFIG_PATH
    if config_path.exists():
        print(f"Config file already exists at: {config_path.absolute()}")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != "y":
            print("Setup cancelled.")
            return
    _do_setup(config_path)


class Config(dict):  # type: ignore
    def __init__(self, config_path: Path, **defaults: Any):
        self.config_path = config_path

        if self._exists:
            self._read()
            has_new_config = False
            for key, value in defaults.items():
                if key not in self:
                    has_new_config = True
                    self[key] = value
            if has_new_config:
                self._write()
        else:
            # No config file — just use defaults. First-time interactive setup
            # is handled by run_setup_if_needed() in entry_point().
            super().__init__(**defaults)
            self._write()

    @property
    def _exists(self) -> bool:
        return self.config_path.exists()

    def _write(self) -> None:
        with open(self.config_path, "w", encoding="utf-8") as file:
            string_config = ""
            for key, value in self.items():
                string_config += f"{key}={value}\n"
            file.write(string_config)

    def _read(self) -> None:
        with open(self.config_path, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    self[key] = value

    def get(self, key: str) -> str:  # type: ignore
        # Prioritize environment variables over config file.
        value = os.getenv(key) or super().get(key)
        if not value:
            raise UsageError(f"Missing config key: {key}")
        return value


cfg = Config(SHELL_GPT_CONFIG_PATH, **DEFAULT_CONFIG)
