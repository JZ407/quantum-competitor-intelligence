"""Configuration management for lit-review."""

import json
import os

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "db_path": os.path.join(CONFIG_DIR, "literature.db"),
    "semantic_scholar_api_key": "",
}


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return dict(DEFAULTS)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return {**DEFAULTS, **cfg}


def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def get(key: str) -> str:
    cfg = load_config()
    return cfg.get(key, "")


def set_(key: str, value: str) -> None:
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
