import base64
import hashlib
import json
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s.%(funcName)s - %(levelname)s - %(message)s",
)

from . import env_utils as Env

DEFAULT_CONFIG_ENV_NAME = "BEYONDSILENCE_CONFIG"
logging.info(f"DEFAULT_CONFIG_ENV_NAME: {DEFAULT_CONFIG_ENV_NAME}")
DEFAULT_KEYS_ENV_NAME = "BEYONDSILENCE_KEYS"
logging.info(f"DEFAULT_KEYS_ENV_NAME: {DEFAULT_KEYS_ENV_NAME}")

raw_config = None


def sha256_of(string):
    return hashlib.sha256(string.encode("utf-8")).hexdigest()


def load_keys():
    if Env.get_env_var(DEFAULT_KEYS_ENV_NAME):
        raw_keys = Env.get_env_var(DEFAULT_KEYS_ENV_NAME)
        logging.info(f"Using environment variable {DEFAULT_KEYS_ENV_NAME}")
    elif os.path.exists("keys.json"):
        # read from keys.json
        with open("keys.json", "r", encoding="utf-8") as f:
            raw_keys = f.read()
        logging.info("Using keys.json")
    elif os.path.exists("keys.example.json"):
        # read from keys.example.json
        with open("keys.example.json", "r", encoding="utf-8") as f:
            raw_keys = f.read()
        logging.info("Using keys.example.json")
        logging.warning(
            "keys.example.json is for testing only, are you sure you want to use it?"
        )
    else:
        logging.info("No keys file found, keys is empty")
        raw_keys = r"{}"
    hash_of_raw_keys = sha256_of(raw_keys)
    logging.info(f"SHA256 of raw keys: {hash_of_raw_keys}")
    try:
        keys = json.loads(raw_keys)
        logging.info(f"Load keys from json")
    except json.JSONDecodeError:
        try:
            decoded_keys = base64.b64decode(raw_keys).decode("utf-8")
            keys = json.loads(decoded_keys)
            logging.info(f"Load keys from Base64")
        except (base64.binascii.Error, json.JSONDecodeError):
            # Handle error when unable to load keys
            keys = None
            logging.error("Unable to load keys")
            raise Exception("Unable to load keys")

    # Validate and subprocess keys
    # Keys is a dict with key:string pairs or empty dict
    if not isinstance(keys, dict):
        logging.error("Keys must be a dict")
        raise Exception("Keys must be a dict")
    if len(keys) == 0:
        logging.info("Keys is empty, pass")
    else:
        for key in keys:
            if not isinstance(keys[key], str):
                logging.error(f"Key {sha256_of(key)} must be a string")
                raise Exception(f"Key {sha256_of(key)} must be a string")

    return keys


def load_config(raw_config):
    hash_of_raw_config = sha256_of(raw_config)
    logging.info(f"SHA256 of raw config: {hash_of_raw_config}")
    try:
        config = json.loads(raw_config)
        logging.info(f"Load config from json")
    except json.JSONDecodeError:
        try:
            decoded_config = base64.b64decode(raw_config).decode("utf-8")
            config = json.loads(decoded_config)
            logging.info(f"Load config from Base64")
        except (base64.binascii.Error, json.JSONDecodeError):
            # Handle error when unable to load config
            config = None
            logging.error("Unable to load config")
            raise Exception("Unable to load config")

    # Try to load keys
    try:
        keys = load_keys()
    except Exception as e:
        logging.warning("Unable to load keys, keys is empty")
        keys = {}

    # Validate and subprocess config

    # github_user_name
    # Must be a string
    if not isinstance(config["github_user_name"], str):
        logging.error("github_user_name must be a string")
        raise Exception("github_user_name must be a string")

    # days_before
    # Must be a number between 1 and 90
    if not isinstance(config["days_before"], int):
        logging.error("days_before must be an integer")
        raise Exception("days_before must be an integer")
    if config["days_before"] > 90 or config["days_before"] < 1:
        logging.warning("days_before must be between 1 and 90, set to 89")
        config["days_before"] = 89

    # main_description
    # Must be a string
    if not isinstance(config["main_description"], str):
        logging.error("main_description must be a string")
        raise Exception("main_description must be a string")

    # dump_config_when_triggered
    # Must be a boolean
    if not isinstance(config["dump_config_when_triggered"], bool):
        logging.error("dump_config_when_triggered must be a boolean")
        raise Exception("dump_config_when_triggered must be a boolean")

    # trigger_when_api_404
    # Must be a boolean
    if not isinstance(config["trigger_when_api_404"], bool):
        logging.error("trigger_when_api_404 must be a boolean")
        raise Exception("trigger_when_api_404 must be a boolean")

    # messages
    # Must be a list
    if not isinstance(config["messages"], list):
        logging.error("messages must be a list")
        raise Exception("messages must be a list")
    # Every item of messages must be a dict, has environ and description and both strings
    # Validate messages
    for message in config["messages"]:
        if not isinstance(message, dict):
            logging.error("Each item of messages must be a dictionary")
            raise Exception("Each item of messages must be a dictionary")
        if "environ" not in message or "description" not in message:
            logging.error("Each message must have 'environ' and 'description' keys")
            raise Exception("Each message must have 'environ' and 'description' keys")
        if not isinstance(message["environ"], str) or not isinstance(
            message["description"], str
        ):
            logging.error("The values of 'environ' and 'description' must be strings")
            raise Exception("The values of 'environ' and 'description' must be strings")
        # There must be an ENV for the environ name or environ name is in keys dict
        if not Env.get_env_var(message["environ"]):
            if message["environ"] in keys:
                # Edit "content" of message
                message["content"] = keys[message["environ"]]
                logging.info(f"Found {sha256_of(message['environ'])} in keys dict")
            elif (
                isinstance(message["content"], str) and message["content"] != ""
            ):  # If message["content"] is string and not empty
                logging.info(f"Found {sha256_of(message['environ'])} in config content")
            else:
                logging.error(
                    f"There is no environment variable set for {sha256_of(message['environ'])} and {sha256_of(message['environ'])} is not in keys dict or in config content"
                )
                raise Exception(
                    f"There is no environment variable set for {sha256_of(message['environ'])} and {sha256_of(message['environ'])} is not in keys dict or in config content"
                )
        else:
            # Edit "content" of message
            message["content"] = Env.get_env_var(message["environ"])
            logging.info(f"Found {sha256_of(message['environ'])} in environment")

    return config


if Env.get_env_var(DEFAULT_CONFIG_ENV_NAME):
    raw_config = Env.get_env_var(DEFAULT_CONFIG_ENV_NAME)
    logging.info(f"Using environment variable {DEFAULT_CONFIG_ENV_NAME}")
elif os.path.exists("config.json"):
    # read from config.json
    with open("config.json", "r", encoding="utf-8") as f:
        raw_config = f.read()
    logging.info("Using config.json")
elif os.path.exists("config.example.json"):
    # read from config.example.json
    with open("config.example.json", "r", encoding="utf-8") as f:
        raw_config = f.read()
    logging.info("Using config.example.json")
    logging.warning(
        "config.example.json is for testing only, are you sure you want to use it?"
    )
else:
    logging.error("No config file found")
    raise Exception("No config file found")

config = load_config(raw_config)
