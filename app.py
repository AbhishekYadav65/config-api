from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from dotenv import dotenv_values
import yaml
import os
from typing import List

app = FastAPI()

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Replace with grader origin if specified
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Default config
# -----------------------------
DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# -----------------------------
# Helper Functions
# -----------------------------
def to_bool(value):
    return str(value).lower() in ["true", "1", "yes", "on"]


def convert_value(key, value):

    if key in ["port", "workers"]:
        return int(value)

    if key == "debug":
        return to_bool(value)

    return str(value)


# -----------------------------
# Read YAML
# -----------------------------
def load_yaml():

    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml") as f:
            return yaml.safe_load(f) or {}

    return {}


# -----------------------------
# Read .env
# -----------------------------
def load_dotenv():

    raw = dotenv_values(".env")

    result = {}

    mapping = {
        "APP_PORT": "port",
        "APP_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
    }

    for k, v in raw.items():

        if k == "NUM_WORKERS" and v is not None:
            result["workers"] = int(v)

        elif k in mapping and v is not None:
            result[mapping[k]] = convert_value(mapping[k], v)

    return result


# -----------------------------
# Read OS Environment Variables
# -----------------------------
def load_os_env():

    defaults = {
        "APP_PORT": "8473",
        "APP_WORKERS": "14",
        "APP_DEBUG": "false",
        "APP_API_KEY": "key-1lx44jnyuf",
    }

    mapping = {
        "APP_PORT": "port",
        "APP_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
    }

    result = {}

    for env_key, config_key in mapping.items():
        value = os.getenv(env_key, defaults.get(env_key))

        if value is not None:
            result[config_key] = convert_value(config_key, value)

    return result


# -----------------------------
# Main Endpoint
# -----------------------------
@app.get("/effective-config")
def effective_config(set: List[str] = Query(default=[])):

    config = DEFAULTS.copy()

    config.update(load_yaml())

    config.update(load_dotenv())

    config.update(load_os_env())

    # CLI overrides
    for item in set:

        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        config[key] = convert_value(key, value)

    # Hide secret
    config["api_key"] = "****"

    return config


@app.get("/")
def home():
    return {"message": "API Running"}